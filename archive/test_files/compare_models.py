#!/usr/bin/env python3
"""
Quick comparison test of LSTM, Random Forest, and ResNet
Tests all 3 models on solubility dataset with baseline (no augmentation)
"""

import sys
import time
import torch

sys.path.insert(0, '/home/hor20kud/aug/EPA')

from benchmark_config import BenchmarkConfig
from benchmark_runner import BenchmarkRunner


def compare_models(dataset='solubility', max_samples=1000):
    """Compare all 3 models on a dataset"""
    
    models = ['lstm', 'random_forest', 'resnet']
    results = {}
    
    print("\n" + "="*70)
    print(f"Model Comparison on {dataset} dataset ({max_samples} samples)")
    print("="*70 + "\n")
    
    for model_type in models:
        print(f"\n{'='*70}")
        print(f"Testing {model_type.upper()}")
        print('='*70)
        
        # Create config
        config = BenchmarkConfig(
            model_type=model_type,
            dataset_name=dataset,
            augmentations=['baseline'],
            epochs=5 if model_type != 'random_forest' else 1,
            batch_size=32,
            use_subset=True,
            subset_size=max_samples,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        # Run benchmark
        start_time = time.time()
        runner = BenchmarkRunner(config)
        model_results = runner.run()
        elapsed = time.time() - start_time
        
        # Store results
        if model_results:
            result = model_results[0]  # baseline result
            results[model_type] = {
                'accuracy': result.get('test_acc', result.get('test_spearman', 0)),
                'mcc': result.get('test_mcc', 0),
                'time': elapsed
            }
        
        print(f"\n⏱️  Time: {elapsed:.1f}s")
    
    # Print comparison
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    print(f"\n{'Model':<15} {'Accuracy/Spearman':<20} {'MCC':<10} {'Time (s)':<10}")
    print("-" * 70)
    
    for model_type, res in results.items():
        print(f"{model_type:<15} {res['accuracy']:<20.4f} {res['mcc']:<10.4f} {res['time']:<10.1f}")
    
    print("\n" + "="*70)
    
    # Determine winner
    best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
    fastest_model = min(results.items(), key=lambda x: x[1]['time'])
    
    print(f"🏆 Best Accuracy: {best_model[0]} ({best_model[1]['accuracy']:.4f})")
    print(f"⚡ Fastest: {fastest_model[0]} ({fastest_model[1]['time']:.1f}s)")
    print("="*70 + "\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare LSTM, RF, and ResNet')
    parser.add_argument('--dataset', type=str, default='solubility',
                       help='Dataset to test on')
    parser.add_argument('--samples', type=int, default=1000,
                       help='Number of samples to use')
    args = parser.parse_args()
    
    results = compare_models(args.dataset, args.samples)
