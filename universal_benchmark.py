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
from scipy.stats import spearmanr

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


class RegressionModel(nn.Module):
    """LSTM model for regression tasks (single output value)"""
    def __init__(self, embed_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, 1)  # Single output for regression
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(self.dropout(x.mean(dim=1))).squeeze(-1)  # Return shape: (batch_size,)


class ResidueLSTMModel(nn.Module):
    """LSTM model for per-residue classification"""
    def __init__(self, num_classes=3, embed_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)  # (batch, seq_len, hidden_dim*2)
        return self.fc(self.dropout(x))  # (batch, seq_len, num_classes)


def train_epoch(model, loader, criterion, optimizer, device, is_ppi=False, task_type='classification'):
    model.train()
    total_loss = 0
    
    if task_type == 'regression':
        # Regression: track loss only
        for batch in tqdm(loader, desc="Training", leave=False):
            seqs, labels = batch
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            
            optimizer.zero_grad()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(loader), 0.0  # Return 0 for accuracy placeholder
    
    elif task_type == 'residue_classification':
        # Residue-level classification with masking
        correct, total = 0, 0
        for batch in tqdm(loader, desc="Training", leave=False):
            seqs, (labels, masks) = batch
            seqs, labels, masks = seqs.to(device), labels.to(device), masks.to(device)
            outputs = model(seqs)  # (batch, seq_len, num_classes)
            
            # Reshape for loss calculation
            outputs_flat = outputs.view(-1, outputs.size(-1))  # (batch*seq_len, num_classes)
            labels_flat = labels.view(-1)  # (batch*seq_len,)
            masks_flat = masks.view(-1)  # (batch*seq_len,)
            
            # Apply mask
            outputs_masked = outputs_flat[masks_flat]
            labels_masked = labels_flat[masks_flat]
            
            optimizer.zero_grad()
            loss = criterion(outputs_masked, labels_masked)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = outputs_masked.max(1)
            correct += predicted.eq(labels_masked).sum().item()
            total += labels_masked.size(0)
        
        return total_loss / len(loader), correct / total if total > 0 else 0.0
    
    else:
        # Standard classification or PPI
        correct, total = 0, 0
        
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


def evaluate(model, loader, device, is_ppi=False, task_type='classification'):
    model.eval()
    
    if task_type == 'regression':
        # Regression: compute Spearman correlation
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for batch in tqdm(loader, desc="Evaluating", leave=False):
                seqs, labels = batch
                seqs, labels = seqs.to(device), labels.to(device)
                outputs = model(seqs)
                
                all_preds.extend(outputs.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Compute Spearman correlation
        spearman, _ = spearmanr(all_labels, all_preds)
        return spearman, 0.0  # Return spearman as "accuracy", 0 for MCC
    
    elif task_type == 'residue_classification':
        # Residue-level classification with masking
        correct, total = 0, 0
        all_preds, all_labels = [], []
        
        with torch.no_grad():
            for batch in tqdm(loader, desc="Evaluating", leave=False):
                seqs, (labels, masks) = batch
                seqs, labels, masks = seqs.to(device), labels.to(device), masks.to(device)
                outputs = model(seqs)
                
                # Flatten and mask
                outputs_flat = outputs.view(-1, outputs.size(-1))
                labels_flat = labels.view(-1)
                masks_flat = masks.view(-1)
                
                outputs_masked = outputs_flat[masks_flat]
                labels_masked = labels_flat[masks_flat]
                
                _, predicted = outputs_masked.max(1)
                correct += predicted.eq(labels_masked).sum().item()
                total += labels_masked.size(0)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels_masked.cpu().numpy())
        
        acc = correct / total if total > 0 else 0.0
        mcc = matthews_corrcoef(all_labels, all_preds) if len(set(all_labels)) > 1 else 0.0
        return acc, mcc
    
    else:
        # Standard classification or PPI
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
    task_type = config.get('task_type', 'classification')
    
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
    
    # Create model based on task type
    if task_type == 'regression':
        model = RegressionModel().to(device)
        criterion = nn.MSELoss()
    elif task_type == 'residue_classification':
        model = ResidueLSTMModel(num_classes=config['num_classes']).to(device)
        criterion = nn.CrossEntropyLoss()
    elif is_ppi:
        model = PPIModel(num_classes=config['num_classes']).to(device)
        criterion = nn.CrossEntropyLoss()
    else:
        model = LSTMModel(num_classes=config['num_classes']).to(device)
        criterion = nn.CrossEntropyLoss()
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    best_valid_metric, best_state = -float('inf'), None
    
    # Training loop
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, is_ppi, task_type)
        valid_metric, valid_mcc = evaluate(model, valid_loader, device, is_ppi, task_type)
        
        # For regression, valid_metric is Spearman correlation; for classification, it's accuracy
        metric_name = 'Spearman' if task_type == 'regression' else 'Acc'
        print(f"Epoch {epoch+1}/{epochs}: Loss={train_loss:.4f}, Train={train_acc:.4f}, Valid {metric_name}={valid_metric:.4f}, MCC={valid_mcc:.4f}")
        
        if valid_metric > best_valid_metric:
            best_valid_metric = valid_metric
            best_state = model.state_dict().copy()
    
    # Test with best model
    model.load_state_dict(best_state)
    test_metric, test_mcc = evaluate(model, test_loader, device, is_ppi, task_type)
    print(f"✅ {aug_name}: Valid {metric_name}={best_valid_metric:.4f}, Test {metric_name}={test_metric:.4f}, MCC={test_mcc:.4f}")
    
    # Clear GPU memory
    del model, criterion, optimizer, train_loader, valid_loader, test_loader
    del train_ds, valid_ds, test_ds
    torch.cuda.empty_cache()
    
    # Return results with appropriate metric names
    result = {
        'augmentation': aug_name,
        'magnitude': magnitude,
        'test_mcc': test_mcc
    }
    
    if task_type == 'regression':
        result['best_valid_spearman'] = best_valid_metric
        result['test_spearman'] = test_metric
    else:
        result['best_valid_acc'] = best_valid_metric
        result['test_acc'] = test_metric
    
    return result


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
    config = get_dataset_config(args.dataset)
    task_type = config.get('task_type', 'classification')
    
    if task_type == 'regression':
        print("Top 5 Augmentations by Test Spearman Correlation:")
        sorted_results = sorted(results, key=lambda x: x.get('test_spearman', -1), reverse=True)
        for i, r in enumerate(sorted_results[:5], 1):
            print(f"  {i}. {r['augmentation']:20s} - Test Spearman: {r.get('test_spearman', 0):.4f}")
    else:
        print("Top 5 Augmentations by Test Accuracy:")
        sorted_results = sorted(results, key=lambda x: x.get('test_acc', 0), reverse=True)
        for i, r in enumerate(sorted_results[:5], 1):
            print(f"  {i}. {r['augmentation']:20s} - Test Acc: {r.get('test_acc', 0):.4f}, MCC: {r['test_mcc']:.4f}")


if __name__ == "__main__":
    main()
