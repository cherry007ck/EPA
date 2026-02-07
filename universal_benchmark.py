#!/usr/bin/env python3
"""
Universal EPA Benchmark - Works with any dataset
Tests all augmentations on a specified dataset
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
import random
import json
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import matthews_corrcoef

# Import our flexible dataset handler
from flexible_dataset import FlexibleLMDBDataset, get_collate_fn
from dataset_config import get_dataset_config, list_available_datasets

sys.path.insert(0, 'epa')
from epa_augmentations import augment_list


class LSTMModel(nn.Module):
    """Simple LSTM model for sequence classification"""
    def __init__(self, num_classes=2, embed_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)  # 20 AAs + padding
        self.lstm = nn.LSTM(embed_dim, hidden_dim, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(self.dropout(x.mean(dim=1)))


class PPIModel(nn.Module):
    """Model for protein-protein interaction (two sequences)"""
    def __init__(self, num_classes=2, embed_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 4, num_classes)  # Concatenate both sequence representations
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        if isinstance(x, tuple):
            x1, x2 = x
            # Process first sequence
            h1 = self.embedding(x1)
            h1, _ = self.lstm(h1)
            h1 = h1.mean(dim=1)
            
            # Process second sequence
            h2 = self.embedding(x2)
            h2, _ = self.lstm(h2)
            h2 = h2.mean(dim=1)
            
            # Concatenate
            h = torch.cat([h1, h2], dim=1)
            return self.fc(self.dropout(h))
        else:
            # Single sequence fallback
            x = self.embedding(x)
            x, _ = self.lstm(x)
            return self.fc(self.dropout(x.mean(dim=1)))


def train_epoch(model, loader, criterion, optimizer, device, is_ppi=False):
    model.train()
    total_loss, correct, total = 0, 0, 0
    
    for batch in tqdm(loader, desc="Training", leave=False):
        if is_ppi:
            (seqs1, seqs2), labels = batch
            seqs1, seqs2 = seqs1.to(device), seqs2.to(device)
            labels = labels.to(device)
            outputs = model((seqs1, seqs2))
        else:
            seqs, labels = batch
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
        
        optimizer.zero_grad()
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
    
    return total_loss / len(loader), correct / total


def evaluate(model, loader, device, is_ppi=False):
    model.eval()
    correct, total = 0, 0
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for batch in tqdm(loader, desc="Evaluating", leave=False):
            if is_ppi:
                (seqs1, seqs2), labels = batch
                seqs1, seqs2 = seqs1.to(device), seqs2.to(device)
                labels = labels.to(device)
                outputs = model((seqs1, seqs2))
            else:
                seqs, labels = batch
                seqs, labels = seqs.to(device), labels.to(device)
                outputs = model(seqs)
            
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    acc = correct / total
    mcc = matthews_corrcoef(all_labels, all_preds) if len(set(all_labels)) > 1 else 0.0
    return acc, mcc


def train_with_augmentation(dataset_name, aug_name, aug_fn, magnitude, device, epochs=30, batch_size=64):
    """Train model with specific augmentation"""
    print(f"\n{'='*70}\nTraining: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
    
    # Get dataset config
    config = get_dataset_config(dataset_name)
    is_ppi = not config['has_single_sequence']
    
    # Augmentation function
    def augment(seq):
        return aug_fn(seq, magnitude)
    
    # Create datasets
    train_ds = FlexibleLMDBDataset(dataset_name, 'train', 
                                   augment_fn=augment if aug_name != "baseline" else None)
    valid_ds = FlexibleLMDBDataset(dataset_name, 'valid')
    test_ds = FlexibleLMDBDataset(dataset_name, 'test')
    
    # Create dataloaders
    collate = get_collate_fn(dataset_name)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, 
                             collate_fn=collate, num_workers=0, pin_memory=True)
    valid_loader = DataLoader(valid_ds, batch_size=batch_size, shuffle=False,
                             collate_fn=collate, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                            collate_fn=collate, num_workers=0, pin_memory=True)
    
    # Create model
    if is_ppi:
        model = PPIModel(num_classes=config['num_classes']).to(device)
    else:
        model = LSTMModel(num_classes=config['num_classes']).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    best_valid_acc, best_state = 0, None
    
    # Training loop
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, is_ppi)
        valid_acc, valid_mcc = evaluate(model, valid_loader, device, is_ppi)
        
        print(f"Epoch {epoch+1}/{epochs}: Loss={train_loss:.4f}, Train={train_acc:.4f}, Valid={valid_acc:.4f}, MCC={valid_mcc:.4f}")
        
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_state = model.state_dict().copy()
    
    # Test with best model
    model.load_state_dict(best_state)
    test_acc, test_mcc = evaluate(model, test_loader, device, is_ppi)
    print(f"✅ {aug_name}: Valid={best_valid_acc:.4f}, Test={test_acc:.4f}, MCC={test_mcc:.4f}")
    
    # Clear GPU memory
    del model, criterion, optimizer, train_loader, valid_loader, test_loader
    del train_ds, valid_ds, test_ds
    torch.cuda.empty_cache()
    
    return {
        'augmentation': aug_name,
        'magnitude': magnitude,
        'best_valid_acc': best_valid_acc,
        'test_acc': test_acc,
        'test_mcc': test_mcc
    }


def main():
    parser = argparse.ArgumentParser(description='EPA Universal Benchmark')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Dataset name (e.g., subcellular_localization, yeast_ppi)')
    parser.add_argument('--epochs', type=int, default=30,
                       help='Number of training epochs per augmentation')
    parser.add_argument('--batch_size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--list', action='store_true',
                       help='List available datasets and exit')
    args = parser.parse_args()
    
    if args.list:
        list_available_datasets()
        return
    
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}\n")
    
    # Get dataset config
    try:
        config = get_dataset_config(args.dataset)
        print(f"Dataset: {config['name']}")
        print(f"Number of classes: {config['num_classes']}")
        print(f"Task type: {config['task_type']}")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nUse --list to see available datasets")
        return
    
    # Set seeds
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    print(f"\n{'='*70}")
    print(f"BENCHMARK: 23 augmentations × {args.epochs} epochs")
    print(f"{'='*70}\n")
    
    results = []
    ops = augment_list()
    
    # Baseline
    results.append(train_with_augmentation(args.dataset, "baseline", 
                                          lambda seq, m: seq, 0.0, device, args.epochs, args.batch_size))
    
    # All augmentations
    for fn, min_mag, max_mag in ops:
        mag = (min_mag + max_mag) / 2
        results.append(train_with_augmentation(args.dataset, fn.__name__, fn, mag, 
                                              device, args.epochs, args.batch_size))
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"benchmark_results_{args.dataset}_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("Benchmark Complete!")
    print(f"Results saved to: {output_file}")
    print(f"{'='*70}\n")
    
    # Print summary
    print("Top 5 Augmentations by Test Accuracy:")
    sorted_results = sorted(results, key=lambda x: x['test_acc'], reverse=True)
    for i, r in enumerate(sorted_results[:5], 1):
        print(f"  {i}. {r['augmentation']:20s} - Test Acc: {r['test_acc']:.4f}, MCC: {r['test_mcc']:.4f}")


if __name__ == "__main__":
    main()
