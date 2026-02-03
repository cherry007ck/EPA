#!/usr/bin/env python3
"""
Visualize benchmark results
"""

import json
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_results(json_file):
    """Load benchmark results from JSON"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def plot_results(results_file):
    """Create visualizations of benchmark results"""
    data = load_results(results_file)
    results = data['results']
    
    # Extract data
    augmentations = [r['augmentation'] for r in results]
    test_accs = [r['test_acc'] for r in results]
    test_mccs = [r['test_mcc'] for r in results]
    valid_accs = [r['best_valid_acc'] for r in results]
    
    # Find baseline
    baseline_idx = augmentations.index('baseline_no_aug')
    baseline_acc = test_accs[baseline_idx]
    
    # Calculate improvements
    improvements = [acc - baseline_acc for acc in test_accs]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('EPA Augmentation Benchmark Results', fontsize=16, fontweight='bold')
    
    # 1. Test Accuracy Bar Chart
    ax1 = axes[0, 0]
    colors = ['red' if aug == 'baseline_no_aug' else 'steelblue' for aug in augmentations]
    bars = ax1.barh(range(len(augmentations)), test_accs, color=colors, alpha=0.7)
    ax1.set_yticks(range(len(augmentations)))
    ax1.set_yticklabels(augmentations, fontsize=8)
    ax1.set_xlabel('Test Accuracy', fontweight='bold')
    ax1.set_title('Test Accuracy by Augmentation')
    ax1.axvline(baseline_acc, color='red', linestyle='--', linewidth=2, label='Baseline')
    ax1.legend()
    ax1.grid(axis='x', alpha=0.3)
    
    # 2. Improvement over Baseline
    ax2 = axes[0, 1]
    colors2 = ['green' if imp > 0 else 'red' for imp in improvements]
    ax2.barh(range(len(augmentations)), improvements, color=colors2, alpha=0.7)
    ax2.set_yticks(range(len(augmentations)))
    ax2.set_yticklabels(augmentations, fontsize=8)
    ax2.set_xlabel('Improvement over Baseline', fontweight='bold')
    ax2.set_title('Performance Gain/Loss vs Baseline')
    ax2.axvline(0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    
    # 3. MCC vs Accuracy Scatter
    ax3 = axes[1, 0]
    scatter_colors = ['red' if aug == 'baseline_no_aug' else 'steelblue' for aug in augmentations]
    ax3.scatter(test_accs, test_mccs, c=scatter_colors, alpha=0.6, s=100)
    ax3.set_xlabel('Test Accuracy', fontweight='bold')
    ax3.set_ylabel('Test MCC', fontweight='bold')
    ax3.set_title('MCC vs Accuracy')
    
    # Annotate baseline
    ax3.annotate('Baseline', 
                (test_accs[baseline_idx], test_mccs[baseline_idx]),
                fontsize=10, fontweight='bold',
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round', fc='yellow', alpha=0.5))
    ax3.grid(alpha=0.3)
    
    # 4. Top 10 and Bottom 5
    ax4 = axes[1, 1]
    sorted_idx = np.argsort(improvements)[::-1]
    top_10_idx = sorted_idx[:10]
    bottom_5_idx = sorted_idx[-5:]
    
    # Combine and plot
    selected_idx = np.concatenate([top_10_idx, bottom_5_idx])
    selected_names = [augmentations[i] for i in selected_idx]
    selected_imps = [improvements[i] for i in selected_idx]
    
    colors4 = ['darkgreen' if i in top_10_idx else 'darkred' for i in selected_idx]
    ax4.barh(range(len(selected_names)), selected_imps, color=colors4, alpha=0.7)
    ax4.set_yticks(range(len(selected_names)))
    ax4.set_yticklabels(selected_names, fontsize=9)
    ax4.set_xlabel('Improvement over Baseline', fontweight='bold')
    ax4.set_title('Top 10 Best & Bottom 5 Worst')
    ax4.axvline(0, color='black', linestyle='-', linewidth=1)
    ax4.axhline(9.5, color='gray', linestyle='--', alpha=0.5)  # Separator
    ax4.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    output_file = results_file.replace('.json', '_visualization.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_file}")
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_benchmark.py <results_file.json>")
        print("\nExample: python visualize_benchmark.py benchmark_results_final_20260203_123456.json")
        sys.exit(1)
    
    results_file = sys.argv[1]
    plot_results(results_file)
