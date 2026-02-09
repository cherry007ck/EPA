#!/usr/bin/env python3
"""
Monitor and document EPA benchmark results across all datasets
"""
import os
import json
import glob
from datetime import datetime
from collections import defaultdict

def find_result_files():
    """Find all benchmark result JSON files"""
    pattern = "benchmark_results_*.json"
    files = glob.glob(pattern)
    
    results_by_dataset = defaultdict(list)
    for f in files:
        # Extract dataset name from filename
        parts = f.replace("benchmark_results_", "").replace(".json", "").split("_")
        # Dataset name is everything except the last 2 parts (timestamp)
        dataset = "_".join(parts[:-2]) if len(parts) > 2 else parts[0]
        results_by_dataset[dataset].append(f)
    
    return results_by_dataset

def load_results(filepath):
    """Load results from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def analyze_results(results):
    """Analyze benchmark results"""
    if not results:
        return None
    
    # Sort by test accuracy
    sorted_results = sorted(results, key=lambda x: x.get('test_acc', 0), reverse=True)
    
    baseline = next((r for r in results if r['augmentation'] == 'baseline'), None)
    
    analysis = {
        'total_augmentations': len(results),
        'baseline': baseline,
        'best': sorted_results[0] if sorted_results else None,
        'worst': sorted_results[-1] if sorted_results else None,
        'top_5': sorted_results[:5],
        'improvements': []
    }
    
    # Find improvements over baseline
    if baseline:
        baseline_acc = baseline.get('test_acc', 0)
        for r in sorted_results:
            if r['augmentation'] != 'baseline':
                improvement = r.get('test_acc', 0) - baseline_acc
                if improvement > 0:
                    analysis['improvements'].append({
                        'augmentation': r['augmentation'],
                        'test_acc': r.get('test_acc', 0),
                        'improvement': improvement,
                        'relative_improvement': (improvement / baseline_acc * 100) if baseline_acc > 0 else 0
                    })
    
    return analysis

def print_dataset_summary(dataset_name, result_files):
    """Print summary for a dataset"""
    print(f"\n{'='*80}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*80}")
    
    if not result_files:
        print("  No results found yet.")
        return
    
    # Use most recent file
    latest_file = max(result_files, key=os.path.getmtime)
    timestamp = datetime.fromtimestamp(os.path.getmtime(latest_file))
    
    print(f"  Latest results: {latest_file}")
    print(f"  Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = load_results(latest_file)
    if not results:
        print("  Failed to load results.")
        return
    
    analysis = analyze_results(results)
    if not analysis:
        print("  Failed to analyze results.")
        return
    
    print(f"  Total augmentations tested: {analysis['total_augmentations']}")
    
    # Baseline
    if analysis['baseline']:
        b = analysis['baseline']
        print(f"\n  Baseline Performance:")
        print(f"    Test Acc: {b.get('test_acc', 0):.4f}")
        print(f"    Test MCC: {b.get('test_mcc', 0):.4f}")
    
    # Best augmentation
    if analysis['best']:
        best = analysis['best']
        print(f"\n  Best Augmentation: {best['augmentation']}")
        print(f"    Test Acc: {best.get('test_acc', 0):.4f}")
        print(f"    Test MCC: {best.get('test_mcc', 0):.4f}")
        
        if analysis['baseline']:
            improvement = best.get('test_acc', 0) - analysis['baseline'].get('test_acc', 0)
            rel_improvement = (improvement / analysis['baseline'].get('test_acc', 1)) * 100
            print(f"    Improvement: {improvement:+.4f} ({rel_improvement:+.2f}%)")
    
    # Top 5
    print(f"\n  Top 5 Augmentations:")
    for i, aug in enumerate(analysis['top_5'], 1):
        improvement = ""
        if analysis['baseline']:
            diff = aug.get('test_acc', 0) - analysis['baseline'].get('test_acc', 0)
            improvement = f" ({diff:+.4f})"
        print(f"    {i}. {aug['augmentation']:25s} - Acc: {aug.get('test_acc', 0):.4f}{improvement}")
    
    # Improvements summary
    if analysis['improvements']:
        print(f"\n  Augmentations Better Than Baseline: {len(analysis['improvements'])}")
        print(f"  Best Improvement: {analysis['improvements'][0]['augmentation']} "
              f"({analysis['improvements'][0]['relative_improvement']:.2f}%)")

def create_comparison_table(results_by_dataset):
    """Create comparison table across datasets"""
    print(f"\n{'='*80}")
    print("Cross-Dataset Comparison")
    print(f"{'='*80}\n")
    
    # Header
    print(f"{'Dataset':<35} {'Baseline':>10} {'Best Aug':>10} {'Improvement':>12}")
    print("-" * 80)
    
    for dataset, files in sorted(results_by_dataset.items()):
        if not files:
            continue
        
        latest_file = max(files, key=os.path.getmtime)
        results = load_results(latest_file)
        if not results:
            continue
        
        analysis = analyze_results(results)
        if not analysis:
            continue
        
        baseline_acc = analysis['baseline'].get('test_acc', 0) if analysis['baseline'] else 0
        best_acc = analysis['best'].get('test_acc', 0) if analysis['best'] else 0
        improvement = best_acc - baseline_acc
        
        print(f"{dataset:<35} {baseline_acc:>10.4f} {best_acc:>10.4f} {improvement:>+12.4f}")

def main():
    print("="*80)
    print("EPA Benchmark Results Summary")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results_by_dataset = find_result_files()
    
    if not results_by_dataset:
        print("\nNo result files found yet.")
        print("Results will appear as benchmark_results_*.json files.")
        return
    
    # Print individual dataset summaries
    for dataset, files in sorted(results_by_dataset.items()):
        print_dataset_summary(dataset, files)
    
    # Create comparison table
    create_comparison_table(results_by_dataset)
    
    print(f"\n{'='*80}")
    print("Summary complete!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
