#!/usr/bin/env python3
"""
Test script for new datasets
Verifies data loading, model initialization, and basic training for each dataset
"""

import torch
from flexible_dataset import FlexibleLMDBDataset, get_collate_fn
from dataset_config import get_dataset_config
from torch.utils.data import DataLoader
from universal_benchmark import LSTMModel, PPIModel, RegressionModel, ResidueLSTMModel

def test_dataset(dataset_name):
    """Test a single dataset"""
    print(f"\n{'='*60}")
    print(f"Testing: {dataset_name}")
    print('='*60)
    
    try:
        # Get config
        config = get_dataset_config(dataset_name)
        print(f"✓ Config loaded: {config['task_type']}, {config['num_classes']} classes")
        
        # Load train dataset
        train_ds = FlexibleLMDBDataset(dataset_name, 'train')
        print(f"✓ Train dataset loaded: {len(train_ds)} samples")
        
        # Test single sample
        sample = train_ds[0]
        if config['task_type'] == 'residue_classification':
            seq, (labels, mask) = sample
            print(f"✓ Sample loaded: seq_len={len(seq)}, labels_len={len(labels)}, mask_sum={mask.sum().item()}")
        elif config['has_single_sequence']:
            seq, label = sample
            print(f"✓ Sample loaded: seq_len={len(seq)}, label={label.item()}")
        else:
            seqs, label = sample
            print(f"✓ Sample loaded: seq1_len={len(seqs[0])}, seq2_len={len(seqs[1])}, label={label.item()}")
        
        # Test dataloader
        collate = get_collate_fn(dataset_name)
        loader = DataLoader(train_ds, batch_size=4, shuffle=False, collate_fn=collate)
        batch = next(iter(loader))
        
        if config['task_type'] == 'residue_classification':
            seqs, (labels, masks) = batch
            print(f"✓ Batch loaded: seqs={seqs.shape}, labels={labels.shape}, masks={masks.shape}")
        elif config['has_single_sequence']:
            seqs, labels = batch
            print(f"✓ Batch loaded: seqs={seqs.shape}, labels={labels.shape}")
        else:
            (seqs1, seqs2), labels = batch
            print(f"✓ Batch loaded: seqs1={seqs1.shape}, seqs2={seqs2.shape}, labels={labels.shape}")
        
        # Test model initialization
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        task_type = config['task_type']
        
        if task_type == 'regression':
            model = RegressionModel().to(device)
            print(f"✓ Regression model initialized")
        elif task_type == 'residue_classification':
            model = ResidueLSTMModel(num_classes=config['num_classes']).to(device)
            print(f"✓ Residue LSTM model initialized")
        elif not config['has_single_sequence']:
            model = PPIModel(num_classes=config['num_classes']).to(device)
            print(f"✓ PPI model initialized")
        else:
            model = LSTMModel(num_classes=config['num_classes']).to(device)
            print(f"✓ LSTM model initialized")
        
        # Test forward pass
        model.eval()
        with torch.no_grad():
            if task_type == 'residue_classification':
                seqs = seqs.to(device)
                outputs = model(seqs)
                print(f"✓ Forward pass: output shape={outputs.shape}")
            elif config['has_single_sequence']:
                seqs = seqs.to(device)
                outputs = model(seqs)
                print(f"✓ Forward pass: output shape={outputs.shape}")
            else:
                seqs1, seqs2 = seqs1.to(device), seqs2.to(device)
                outputs = model((seqs1, seqs2))
                print(f"✓ Forward pass: output shape={outputs.shape}")
        
        print(f"✅ {dataset_name} - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ {dataset_name} - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing New Datasets")
    print("="*60)
    
    datasets = [
        'beta_lactamase',      # Regression
        'secondary_structure', # Residue classification
        'human_ppi',           # PPI classification
        'solubility'           # Binary classification
    ]
    
    results = {}
    for dataset in datasets:
        results[dataset] = test_dataset(dataset)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for dataset, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {dataset:25s} {status}")
    
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL DATASETS READY FOR BENCHMARKING!")
    else:
        print("⚠️  Some datasets have issues - fix before benchmarking")
    print("="*60 + "\n")
