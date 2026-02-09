#!/usr/bin/env python3
"""
Test Random Forest model on EPA datasets
Quick validation before full benchmarking
"""

import sys
import torch
import numpy as np
from sklearn.metrics import accuracy_score, matthews_corrcoef
from scipy.stats import spearmanr
from tqdm import tqdm

sys.path.insert(0, '/home/hor20kud/aug/EPA')

from flexible_dataset import FlexibleLMDBDataset
from dataset_config import get_dataset_config
from models.random_forest_models import RandomForestModel


def decode_sequence(tensor):
    """Convert tensor back to amino acid sequence"""
    vocab = "ACDEFGHIKLMNPQRSTVWY"
    seq = []
    for idx in tensor:
        if idx > 0:  # Skip padding (0)
            seq.append(vocab[idx - 1])
    return ''.join(seq)


def load_sequences_and_labels(dataset, max_samples=None):
    """Load all sequences and labels from dataset"""
    sequences = []
    labels = []
    
    n_samples = min(len(dataset), max_samples) if max_samples else len(dataset)
    
    for i in tqdm(range(n_samples), desc="Loading data"):
        seq_tensor, label = dataset[i]
        
        # Handle PPI datasets (dual sequences)
        if isinstance(seq_tensor, list):
            seq1 = decode_sequence(seq_tensor[0])
            seq2 = decode_sequence(seq_tensor[1])
            sequences.append((seq1, seq2))
        else:
            sequences.append(decode_sequence(seq_tensor))
        
        # Handle label types
        if isinstance(label, torch.Tensor):
            labels.append(label.item())
        else:
            labels.append(label)
    
    return sequences, np.array(labels)


def test_random_forest_classification(dataset_name, max_train=5000, max_test=1000):
    """Test Random Forest on a classification dataset"""
    print(f"\n{'='*70}")
    print(f"Testing Random Forest on: {dataset_name}")
    print('='*70)
    
    config = get_dataset_config(dataset_name)
    is_ppi = not config['has_single_sequence']
    
    print(f"Task: {config['task_type']}")
    print(f"Classes: {config['num_classes']}")
    print(f"PPI: {is_ppi}")
    
    # Load datasets
    print("\n📂 Loading datasets...")
    train_ds = FlexibleLMDBDataset(dataset_name, 'train')
    test_ds = FlexibleLMDBDataset(dataset_name, 'test')
    
    print(f"Train size: {len(train_ds)} (using {max_train})")
    print(f"Test size: {len(test_ds)} (using {max_test})")
    
    # Load sequences and labels
    X_train, y_train = load_sequences_and_labels(train_ds, max_train)
    X_test, y_test = load_sequences_and_labels(test_ds, max_test)
    
    # For PPI, separate sequences
    if is_ppi:
        X_train = list(zip(*X_train))  # Unzip to (seqs1, seqs2)
        X_test = list(zip(*X_test))
    
    # Train Random Forest
    print("\n🌲 Training Random Forest...")
    rf_model = RandomForestModel(
        task_type='classification',
        n_estimators=100,
        n_jobs=-1,
        random_state=42
    )
    rf_model.fit(X_train, y_train, is_ppi=is_ppi)
    print("✓ Training complete")
    
    # Evaluate on test set
    print("\n📊 Evaluating...")
    y_pred = rf_model.predict(X_test, is_ppi=is_ppi)
    
    accuracy = accuracy_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    
    print(f"\n{'='*70}")
    print(f"Results:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  MCC: {mcc:.4f}")
    print('='*70)
    
    return accuracy, mcc


def test_random_forest_regression(dataset_name, max_train=3000, max_test=500):
    """Test Random Forest on a regression dataset"""
    print(f"\n{'='*70}")
    print(f"Testing Random Forest on: {dataset_name}")
    print('='*70)
    
    config = get_dataset_config(dataset_name)
    
    print(f"Task: {config['task_type']}")
    
    # Load datasets
    print("\n📂 Loading datasets...")
    train_ds = FlexibleLMDBDataset(dataset_name, 'train')
    test_ds = FlexibleLMDBDataset(dataset_name, 'test')
    
    print(f"Train size: {len(train_ds)} (using {max_train})")
    print(f"Test size: {len(test_ds)} (using {max_test})")
    
    # Load sequences and labels
    X_train, y_train = load_sequences_and_labels(train_ds, max_train)
    X_test, y_test = load_sequences_and_labels(test_ds, max_test)
    
    # Train Random Forest
    print("\n🌲 Training Random Forest Regressor...")
    rf_model = RandomForestModel(
        task_type='regression',
        n_estimators=100,
        n_jobs=-1,
        random_state=42
    )
    rf_model.fit(X_train, y_train, is_ppi=False)
    print("✓ Training complete")
    
    # Evaluate on test set
    print("\n📊 Evaluating...")
    y_pred = rf_model.predict(X_test, is_ppi=False)
    
    spearman, _ = spearmanr(y_test, y_pred)
    
    print(f"\n{'='*70}")
    print(f"Results:")
    print(f"  Spearman Correlation: {spearman:.4f}")
    print('='*70)
    
    return spearman


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Random Forest on datasets')
    parser.add_argument('--dataset', type=str, default='solubility',
                       help='Dataset to test (default: solubility)')
    parser.add_argument('--max_train', type=int, default=5000,
                       help='Max training samples')
    parser.add_argument('--max_test', type=int, default=1000,
                       help='Max test samples')
    args = parser.parse_args()
    
    config = get_dataset_config(args.dataset)
    
    if config['task_type'] == 'regression':
        test_random_forest_regression(args.dataset, args.max_train, args.max_test)
    else:
        test_random_forest_classification(args.dataset, args.max_train, args.max_test)
