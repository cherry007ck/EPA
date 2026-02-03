#!/usr/bin/env python3
"""
Comprehensive Augmentation Benchmark
Tests each of the 23 augmentations individually to find which ones help most
"""

import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import lmdb
import pickle
import random
import numpy as np
from datetime import datetime
import json
from tqdm import tqdm

# Add EPA to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'epa'))
from epa_augmentations import augment_list
from util import load_config

# Metrics
from sklearn.metrics import matthews_corrcoef


class LMDBDataset(Dataset):
    """LMDB dataset loader"""
    def __init__(self, lmdb_path, augment_fn=None):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False, readahead=False, meminit=False)
        with self.env.begin() as txn:
            self.length = txn.stat()['entries']
        self.augment_fn = augment_fn
    
    def __len__(self):
        return self.length
    
    def __getitem__(self, idx):
        with self.env.begin() as txn:
            data = pickle.loads(txn.get(str(idx).encode()))
        
        sequence = list(data['primary'])
        label = int(data['localization'])
        
        # Apply augmentation if provided
        if self.augment_fn is not None:
            sequence = self.augment_fn(sequence.copy())
        
        # Convert to tensor
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq_tensor = torch.zeros(len(sequence), dtype=torch.long)
        for i, aa in enumerate(sequence):
            if aa in vocab:
                seq_tensor[i] = vocab.index(aa)
        
        return seq_tensor, torch.tensor(label, dtype=torch.long)


def collate_fn(batch):
    """Collate with padding"""
    sequences, labels = zip(*batch)
    max_len = max(len(s) for s in sequences)
    
    padded_seqs = torch.zeros(len(sequences), max_len, dtype=torch.long)
    for i, seq in enumerate(sequences):
        padded_seqs[i, :len(seq)] = seq
    
    labels = torch.stack(labels)
    return padded_seqs, labels


class LSTMModel(nn.Module):
    """LSTM model for binary classification"""
    def __init__(self, vocab_size=20, embed_dim=128, hidden_dim=256, num_layers=2, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = x.mean(dim=1)  # Global average pooling
        x = self.dropout(x)
        x = self.fc(x)
        return x


def train_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for seqs, labels in tqdm(loader, desc="Training", leave=False):
        seqs, labels = seqs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(seqs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
    
    return total_loss / len(loader), correct / total


def evaluate(model, loader, device):
    """Evaluate model"""
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for seqs, labels in tqdm(loader, desc="Evaluating", leave=False):
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            _, predicted = outputs.max(1)
            
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    accuracy = correct / total
    mcc = matthews_corrcoef(all_labels, all_preds)
    
    return accuracy, mcc


def train_with_augmentation(aug_name, aug_fn, magnitude, config, device, epochs=30):
    """Train model with specific augmentation"""
    print(f"\n{'='*70}")
    print(f"Training with: {aug_name} (magnitude: {magnitude:.2f})")
    print(f"{'='*70}")
    
    # Create augmentation function
    def augment(seq):
        return aug_fn(seq, magnitude)
    
    # Load datasets
    train_dataset = LMDBDataset(config.dataset.train_path, augment_fn=augment)
    valid_dataset = LMDBDataset(config.dataset.valid_path, augment_fn=None)
    test_dataset = LMDBDataset(config.dataset.test_path, augment_fn=None)
    
    train_loader = DataLoader(train_dataset, batch_size=config.train.batch_size, 
                              shuffle=True, collate_fn=collate_fn, num_workers=0)
    valid_loader = DataLoader(valid_dataset, batch_size=config.train.batch_size, 
                              shuffle=False, collate_fn=collate_fn, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=config.train.batch_size, 
                             shuffle=False, collate_fn=collate_fn, num_workers=0)
    
    # Initialize model
    model = LSTMModel(
        vocab_size=20,
        embed_dim=config.model.get('embed_dim', 128),
        hidden_dim=config.model.get('hidden_dim', 256),
        num_layers=config.model.get('num_layers', 2),
        num_classes=2
    ).to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.optimizer.lr)
    
    # Training
    best_valid_acc = 0
    best_model_state = None
    
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        valid_acc, valid_mcc = evaluate(model, valid_loader, device)
        
        print(f"Epoch {epoch+1}/{epochs}: "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
              f"Valid Acc: {valid_acc:.4f}, Valid MCC: {valid_mcc:.4f}")
        
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_model_state = model.state_dict().copy()
    
    # Test with best model
    model.load_state_dict(best_model_state)
    test_acc, test_mcc = evaluate(model, test_loader, device)
    
    print(f"\n✅ Results for {aug_name}:")
    print(f"   Best Valid Acc: {best_valid_acc:.4f}")
    print(f"   Test Acc: {test_acc:.4f}, Test MCC: {test_mcc:.4f}")
    
    return {
        'augmentation': aug_name,
        'magnitude': magnitude,
        'best_valid_acc': best_valid_acc,
        'test_acc': test_acc,
        'test_mcc': test_mcc
    }


def main():
    # Configuration
    config_path = "config/LSTM/binloc_LSTM.yaml"
    config = load_config(config_path)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Set seeds
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    
    # Hyperparameters
    EPOCHS = 30  # Increased for better accuracy
    MAGNITUDE = 0.15  # Moderate magnitude for all augmentations
    
    # Get all augmentations
    augs = augment_list()
    print(f"\n{'='*70}")
    print(f"COMPREHENSIVE AUGMENTATION BENCHMARK")
    print(f"{'='*70}")
    print(f"Total augmentations to test: {len(augs)}")
    print(f"Epochs per augmentation: {EPOCHS}")
    print(f"Magnitude: {MAGNITUDE}")
    print(f"{'='*70}\n")
    
    # Results storage
    results = []
    
    # 1. Baseline (no augmentation)
    print("\n" + "="*70)
    print("BASELINE (No Augmentation)")
    print("="*70)
    
    baseline_result = train_with_augmentation(
        "baseline_no_aug", 
        lambda seq, m: seq,  # No augmentation
        0.0,
        config,
        device,
        epochs=EPOCHS
    )
    results.append(baseline_result)
    
    # 2. Test each augmentation
    for i, (aug_fn, low_mag, high_mag) in enumerate(augs, 1):
        aug_name = aug_fn.__name__
        
        # Use middle of magnitude range or MAGNITUDE if that's better
        aug_magnitude = MAGNITUDE if low_mag <= MAGNITUDE <= high_mag else (low_mag + high_mag) / 2
        
        result = train_with_augmentation(
            aug_name,
            aug_fn,
            aug_magnitude,
            config,
            device,
            epochs=EPOCHS
        )
        results.append(result)
        
        # Save intermediate results
        output_file = f"EPA/benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS SUMMARY")
    print("="*70)
    
    # Sort by test accuracy
    sorted_results = sorted(results, key=lambda x: x['test_acc'], reverse=True)
    
    print(f"\n{'Rank':<6} {'Augmentation':<35} {'Test Acc':<12} {'Test MCC':<12} {'Valid Acc':<12}")
    print("-" * 85)
    
    for rank, result in enumerate(sorted_results, 1):
        print(f"{rank:<6} {result['augmentation']:<35} "
              f"{result['test_acc']:.4f}       "
              f"{result['test_mcc']:.4f}       "
              f"{result['best_valid_acc']:.4f}")
    
    # Save final results
    final_output = f"EPA/benchmark_results_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(final_output, 'w') as f:
        json.dump({
            'config': {
                'epochs': EPOCHS,
                'magnitude': MAGNITUDE,
                'seed': seed
            },
            'results': sorted_results
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {final_output}")
    
    # Performance analysis
    baseline_acc = baseline_result['test_acc']
    print(f"\n{'='*70}")
    print("PERFORMANCE ANALYSIS")
    print(f"{'='*70}")
    print(f"Baseline accuracy: {baseline_acc:.4f}")
    
    improvements = [(r['augmentation'], r['test_acc'] - baseline_acc) 
                   for r in results if r['augmentation'] != 'baseline_no_aug']
    improvements.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 10 Improvements over Baseline:")
    for i, (name, improvement) in enumerate(improvements[:10], 1):
        symbol = "📈" if improvement > 0 else "📉"
        print(f"{i:2}. {symbol} {name:<35} {improvement:+.4f} ({improvement*100:+.2f}%)")
    
    print(f"\nBottom 5 (Worst Performers):")
    for i, (name, improvement) in enumerate(improvements[-5:], 1):
        print(f"{i:2}. 📉 {name:<35} {improvement:+.4f} ({improvement*100:+.2f}%)")


if __name__ == "__main__":
    main()
