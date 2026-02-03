#!/usr/bin/env python3
"""
Quick Test of Benchmark Script
Tests just baseline + 2 augmentations to verify everything works
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
        
        if self.augment_fn is not None:
            sequence = self.augment_fn(sequence.copy())
        
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq_tensor = torch.zeros(len(sequence), dtype=torch.long)
        for i, aa in enumerate(sequence):
            if aa in vocab:
                seq_tensor[i] = vocab.index(aa)
        
        return seq_tensor, torch.tensor(label, dtype=torch.long)


def collate_fn(batch):
    sequences, labels = zip(*batch)
    max_len = max(len(s) for s in sequences)
    padded_seqs = torch.zeros(len(sequences), max_len, dtype=torch.long)
    for i, seq in enumerate(sequences):
        padded_seqs[i, :len(seq)] = seq
    labels = torch.stack(labels)
    return padded_seqs, labels


class LSTMModel(nn.Module):
    def __init__(self, vocab_size=20, embed_dim=128, hidden_dim=256, num_layers=2, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = x.mean(dim=1)
        x = self.dropout(x)
        x = self.fc(x)
        return x


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for seqs, labels in loader:
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
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for seqs, labels in loader:
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


def quick_test(aug_name, aug_fn, magnitude, config, device, epochs=5):
    """Quick test with reduced epochs"""
    print(f"\n{'='*70}")
    print(f"Testing: {aug_name}")
    print(f"{'='*70}")
    
    def augment(seq):
        return aug_fn(seq, magnitude)
    
    # Load datasets
    train_dataset = LMDBDataset(config.dataset.train_path, augment_fn=augment if aug_name != "baseline" else None)
    valid_dataset = LMDBDataset(config.dataset.valid_path, augment_fn=None)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, collate_fn=collate_fn, num_workers=0)
    valid_loader = DataLoader(valid_dataset, batch_size=64, shuffle=False, collate_fn=collate_fn, num_workers=0)
    
    # Initialize model
    model = LSTMModel().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    best_valid_acc = 0
    
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        valid_acc, valid_mcc = evaluate(model, valid_loader, device)
        
        print(f"Epoch {epoch+1}/{epochs}: Train Loss: {train_loss:.4f}, "
              f"Train Acc: {train_acc:.4f}, Valid Acc: {valid_acc:.4f}, MCC: {valid_mcc:.4f}")
        
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
    
    print(f"✅ Best Valid Acc: {best_valid_acc:.4f}")
    
    return {
        'augmentation': aug_name,
        'best_valid_acc': best_valid_acc
    }


def main():
    print("\n" + "="*70)
    print("QUICK BENCHMARK TEST")
    print("="*70)
    print("Testing baseline + 2 augmentations with 5 epochs each")
    print("="*70 + "\n")
    
    config_path = "config/LSTM/binloc_LSTM.yaml"
    config = load_config(config_path)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}\n")
    
    # Set seeds
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Get all augmentations
    augs = augment_list()
    
    results = []
    
    # 1. Baseline
    print("1/3: Testing Baseline (no augmentation)")
    result = quick_test("baseline", lambda seq, m: seq, 0.0, config, device, epochs=5)
    results.append(result)
    
    # 2. Random substitute (simple augmentation)
    print("\n2/3: Testing random_substitute")
    result = quick_test("random_substitute", augs[1][0], 0.15, config, device, epochs=5)
    results.append(result)
    
    # 3. Conservative substitute (our addition)
    print("\n3/3: Testing conservative_substitute")
    result = quick_test("conservative_substitute", augs[12][0], 0.15, config, device, epochs=5)
    results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("QUICK TEST RESULTS")
    print("="*70)
    for r in results:
        print(f"{r['augmentation']:<30} Valid Acc: {r['best_valid_acc']:.4f}")
    
    print("\n✅ Benchmark script is working correctly!")
    print("📊 Ready to run full benchmark with all 23 augmentations")
    print("\nTo run full benchmark:")
    print("  cd EPA && ./run_benchmark.sh")


if __name__ == "__main__":
    main()
