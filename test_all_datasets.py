#!/usr/bin/env python3
"""
Quick test to verify all datasets work with the benchmark
Tests just 1 epoch with baseline to ensure everything loads correctly
"""
import sys
import torch
from torch.utils.data import DataLoader
from flexible_dataset import FlexibleLMDBDataset, get_collate_fn
from dataset_config import get_dataset_config, DATASET_CONFIGS
from universal_benchmark import LSTMModel, PPIModel, train_epoch, evaluate
import torch.nn as nn

def quick_test_dataset(dataset_name, device):
    """Quick test: 1 epoch of baseline training"""
    print(f"\nTesting: {dataset_name}")
    print("-" * 60)
    
    try:
        # Get config
        config = get_dataset_config(dataset_name)
        is_ppi = not config['has_single_sequence']
        
        print(f"  Task: {config['task_type']}")
        print(f"  Classes: {config['num_classes']}")
        print(f"  Type: {'PPI (2 sequences)' if is_ppi else 'Single sequence'}")
        
        # Load datasets
        print(f"  Loading data...")
        train_ds = FlexibleLMDBDataset(dataset_name, 'train')
        valid_ds = FlexibleLMDBDataset(dataset_name, 'valid')
        test_ds = FlexibleLMDBDataset(dataset_name, 'test')
        
        print(f"  Train: {len(train_ds)}, Valid: {len(valid_ds)}, Test: {len(test_ds)}")
        
        # Create dataloaders (small batch for testing)
        collate = get_collate_fn(dataset_name)
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, 
                                 collate_fn=collate, num_workers=0)
        valid_loader = DataLoader(valid_ds, batch_size=32, shuffle=False,
                                 collate_fn=collate, num_workers=0)
        
        # Create model
        print(f"  Creating model...")
        if is_ppi:
            model = PPIModel(num_classes=config['num_classes']).to(device)
        else:
            model = LSTMModel(num_classes=config['num_classes']).to(device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Train 1 epoch
        print(f"  Training 1 epoch...")
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device, is_ppi)
        
        # Evaluate
        print(f"  Evaluating...")
        valid_acc, valid_mcc = evaluate(model, valid_loader, device, is_ppi)
        
        print(f"  ✅ SUCCESS")
        print(f"     Train: {train_acc:.4f}, Valid: {valid_acc:.4f}, MCC: {valid_mcc:.4f}")
        
        # Cleanup
        del model, train_loader, valid_loader, train_ds, valid_ds, test_ds
        torch.cuda.empty_cache()
        
        return True, train_acc, valid_acc, valid_mcc
        
    except Exception as e:
        print(f"  ❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0, 0, 0

def main():
    print("=" * 70)
    print("EPA Dataset Compatibility Test")
    print("Testing all datasets with 1 epoch baseline training")
    print("=" * 70)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice: {device}")
    
    # Test all datasets
    results = {}
    for dataset_name in DATASET_CONFIGS.keys():
        success, train_acc, valid_acc, mcc = quick_test_dataset(dataset_name, device)
        results[dataset_name] = {
            'success': success,
            'train_acc': train_acc,
            'valid_acc': valid_acc,
            'mcc': mcc
        }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}\n")
    
    for dataset_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        if result['success']:
            print(f"{status} {dataset_name:35s} - Valid Acc: {result['valid_acc']:.4f}")
        else:
            print(f"{status} {dataset_name:35s}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 All datasets are working! Ready for full benchmark.")
        print("\nNext steps:")
        print("  1. Run: ./submit_all_benchmarks.sh")
        print("  2. Or run individual: sbatch run_universal_benchmark.sbatch <dataset>")
        return 0
    else:
        print("⚠️  Some datasets failed. Fix issues before running full benchmark.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
