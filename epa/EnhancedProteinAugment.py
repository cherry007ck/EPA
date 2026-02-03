"""
Enhanced Protein Augmentation (EPA) - Main Training Script

Two-phase training with automated policy search:
1. Baseline training without augmentation
2. Policy search to find optimal augmentation strategy
"""

import os
import sys
import math
import pprint
import shutil
import logging
import argparse
import numpy as np
import random

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from epa_augmentations import augment_list, apply_augment
from util import load_config, get_root_logger, create_working_directory

# Add metrics
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..'))
from metrics import accuracy as compute_accuracy, mcc as compute_mcc

# Dataset paths
DATASET_BASE = "/home/luffy/dsa_project/merged/protein_augmentation/protein_augmentation/datasets"

# Amino acids
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
VOCAB_SIZE = 21


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="yaml configuration file", required=True)
    parser.add_argument("--seed", help="random seed", type=int, default=0)
    return parser.parse_known_args()[0]


def set_seed(seed):
    """Set random seed for reproducibility"""
    torch.manual_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ============================================================================
# MODEL (Simple LSTM from benchmark)
# ============================================================================

class LSTMModel(nn.Module):
    def __init__(self, embed=64, hidden=128, num_classes=2):
        super().__init__()
        self.emb = nn.Embedding(VOCAB_SIZE, embed, padding_idx=0)
        self.lstm = nn.LSTM(embed, hidden, batch_first=True, bidirectional=True)
        self.head = nn.Sequential(
            nn.Linear(hidden * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        x = self.emb(x)
        _, (h, _) = self.lstm(x)
        h = torch.cat([h[-2], h[-1]], dim=1)
        return self.head(h)


# ============================================================================
# DATASET (LMDB-based from benchmark)
# ============================================================================

import lmdb
import pickle

class ProteinDataset(Dataset):
    def __init__(self, lmdb_path, max_len=512, augment_policy=None, augment_prob=0.7):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False)
        self.max_len = max_len
        self.augment_policy = augment_policy
        self.augment_prob = augment_prob
        self.keys = []
        
        # Load all valid keys
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                try:
                    rec = pickle.loads(value)
                    if isinstance(rec, dict) and 'primary' in rec and 'localization' in rec:
                        self.keys.append(key)
                except Exception:
                    continue
    
    def __len__(self):
        return len(self.keys)
    
    def encode(self, seq):
        """Encode sequence to tensor"""
        vocab = {aa: i + 1 for i, aa in enumerate(AMINO_ACIDS)}
        encoded = [vocab.get(aa, 0) for aa in seq[:self.max_len]]
        encoded += [0] * (self.max_len - len(encoded))
        return torch.tensor(encoded, dtype=torch.long)
    
    def __getitem__(self, idx):
        key = self.keys[idx]
        with self.env.begin() as txn:
            rec = pickle.loads(txn.get(key))
        
        seq = list(rec['primary'])
        label = float(rec['localization'])
        
        # Apply augmentation if policy is provided
        if self.augment_policy and random.random() < self.augment_prob:
            try:
                seq = apply_augment(seq, self.augment_policy)
                if len(seq) < 5:  # Sanity check
                    seq = list(rec['primary'])
            except Exception:
                seq = list(rec['primary'])
        
        return self.encode(''.join(seq)), torch.tensor(label, dtype=torch.long)


def collate_fn(batch):
    seqs, labs = zip(*batch)
    return torch.stack(seqs), torch.stack(labs)


# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def train_epoch(model, loader, criterion, optimizer, device):
    """Train one epoch"""
    model.train()
    total_loss, correct, total = 0, 0, 0
    
    for seqs, labels in loader:  #removed tqdm 
        seqs, labels = seqs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(seqs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion, device):
    """Evaluate model"""
    model.eval()
    total_loss, correct, total = 0, 0, 0
    
    with torch.no_grad():
        for seqs, labels in loader:
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    
    return total_loss / len(loader), correct / total


# ============================================================================
# POLICY SEARCH
# ============================================================================

def generate_random_policy(num_subpolicy=4, num_op=2):
    """Generate a random augmentation policy"""
    ops = augment_list()
    policy = []
    
    for _ in range(num_subpolicy):
        subpolicy = []
        for _ in range(num_op):
            op_idx = np.random.randint(len(ops))
            prob = np.random.uniform(0.0, 1.0)
            level = np.random.uniform(0.0, 1.0)
            subpolicy.append((ops[op_idx][0].__name__, prob, level))
        policy.append(subpolicy)
    
    return policy


def finetune_with_policy(cfg, model, train_loader, valid_loader, criterion, optimizer, 
                        device, policy, logger, finetune_epoch=5):
    """Fine-tune model with a specific policy"""
    # Create dataset with policy
    train_dataset = ProteinDataset(
        cfg.dataset.train_path,
        augment_policy=policy,
        augment_prob=0.7
    )
    train_loader = DataLoader(train_dataset, batch_size=cfg.train.batch_size,
                             shuffle=True, collate_fn=collate_fn)
    
    best_val_acc = 0.0
    for epoch in range(finetune_epoch):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, valid_loader, criterion, device)
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
        
        logger.info(f"  Epoch {epoch+1}/{finetune_epoch}: "
                   f"Train: {train_acc:.4f} | Val: {val_acc:.4f}")
    
    return best_val_acc


def search_best_policy(cfg, baseline_model_path, train_loader, valid_loader, logger):
    """Search for the best augmentation policy"""
    device = torch.device(f"cuda:{cfg.device.gpus[0]}" if len(cfg.device.gpus) > 0 else "cpu")
    
    finetune_num = cfg.epa.finetune_num
    finetune_epoch = cfg.epa.finetune_epoch
    num_subpolicy = cfg.epa.num_subpolicy
    num_op = cfg.epa.num_op
    
    logger.info("")
    logger.info("="*80)
    logger.info(f"PHASE 2: POLICY SEARCH - {finetune_num} trials × {finetune_epoch} epochs")
    logger.info("="*80)
    
    best_policy = None
    best_score = float('-inf')
    
    for trial in range(finetune_num):
        logger.info(f"\n{'─'*80}")
        logger.info(f"Trial {trial+1}/{finetune_num}")
        logger.info(f"{'─'*80}")
        
        # Load baseline model
        model = LSTMModel(embed=cfg.model.embed_dim, hidden=cfg.model.hidden_dim,
                         num_classes=cfg.model.num_classes).to(device)
        model.load_state_dict(torch.load(baseline_model_path))
        
        # Generate random policy
        policy = generate_random_policy(num_subpolicy, num_op)
        logger.info(f"Generated policy with {len(policy)} sub-policies:")
        for i, subpolicy in enumerate(policy[:2], 1):  # Show first 2
            logger.info(f"  SubPolicy {i}: {subpolicy}")
        if len(policy) > 2:
            logger.info(f"  ... and {len(policy)-2} more")
        
        # Create optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=cfg.optimizer.lr)
        criterion = nn.CrossEntropyLoss()
        
        # Fine-tune with this policy
        val_acc = finetune_with_policy(cfg, model, train_loader, valid_loader,
                                      criterion, optimizer, device, policy,
                                      logger, finetune_epoch)
        
        logger.info(f"Final Val Acc: {val_acc:.4f}")
        
        if val_acc > best_score:
            best_score = val_acc
            best_policy = policy
            logger.info(f"✅ New best! Acc = {best_score:.4f}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Search Complete! Best Score: {best_score:.4f}")
    logger.info("="*80)
    
    return best_policy, best_score


# ============================================================================
# MAIN
# ============================================================================

def main():
    args = parse_args()
    cfg = load_config(args.config)
    set_seed(args.seed)
    
    output_dir = create_working_directory(cfg)
    logger = get_root_logger()
    
    logger.info("="*80)
    logger.info("EPA: Enhanced Protein Augmentation")
    logger.info("="*80)
    logger.info(f"Config: {args.config}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Seed: {args.seed}")
    logger.info("="*80)
    logger.info(pprint.pformat(cfg))
    
    device = torch.device(f"cuda:{cfg.device.gpus[0]}" if len(cfg.device.gpus) > 0 else "cpu")
    logger.info(f"Device: {device}")
    
    # Create datasets
    train_dataset = ProteinDataset(cfg.dataset.train_path)
    valid_dataset = ProteinDataset(cfg.dataset.valid_path)
    test_dataset = ProteinDataset(cfg.dataset.test_path)
    
    train_loader = DataLoader(train_dataset, batch_size=cfg.train.batch_size,
                             shuffle=True, collate_fn=collate_fn)
    valid_loader = DataLoader(valid_dataset, batch_size=cfg.train.batch_size,
                             collate_fn=collate_fn)
    test_loader = DataLoader(test_dataset, batch_size=cfg.train.batch_size,
                            collate_fn=collate_fn)
    
    logger.info(f"Train: {len(train_dataset)}, Valid: {len(valid_dataset)}, Test: {len(test_dataset)}")
    
    # Phase 1: Baseline training
    logger.info("\n" + "="*80)
    logger.info("PHASE 1: BASELINE TRAINING (No Augmentation)")
    logger.info("="*80)
    
    model = LSTMModel(embed=cfg.model.embed_dim, hidden=cfg.model.hidden_dim,
                     num_classes=cfg.model.num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.optimizer.lr)
    
    best_val_acc = 0.0
    best_epoch = 0
    
    for epoch in range(cfg.epa.baseline_epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, valid_loader, criterion, device)
        
        # Calculate MCC
        model.eval()
        all_preds, all_targets = [], []
        with torch.no_grad():
            for seqs, labels in valid_loader:
                seqs = seqs.to(device)
                outputs = model(seqs)
                all_preds.append(outputs)
                all_targets.append(labels)
        all_preds = torch.cat(all_preds, dim=0)
        all_targets = torch.cat(all_targets, dim=0)
        val_mcc = compute_mcc(all_preds, all_targets)
        
        logger.info(f"Epoch {epoch+1:>2}/{cfg.epa.baseline_epochs} | "
                   f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
                   f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | Val MCC: {val_mcc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch + 1
            torch.save(model.state_dict(), os.path.join(output_dir, "baseline_best.pt"))
    
    logger.info("")
    logger.info(f"✅ Baseline Best: Epoch {best_epoch}, Val Acc = {best_val_acc:.4f}")

    
    # Phase 2: Policy search
    if cfg.epa.search:
        baseline_model_path = os.path.join(output_dir, "baseline_best.pt")
        best_policy, best_score = search_best_policy(cfg, baseline_model_path,
                                                     train_loader, valid_loader, logger)
        
        # Save best policy
        import json
        with open(os.path.join(output_dir, "best_policy.json"), 'w') as f:
            json.dump(best_policy, f, indent=2)
    
    # Phase 3: Final test
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: FINAL EVALUATION")
    logger.info("="*80)
    
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    logger.info(f"Test Acc: {test_acc:.4f}")
    
    logger.info("\nEPA Training Complete!")


if __name__ == "__main__":
    main()
