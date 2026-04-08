#!/usr/bin/env python3
"""
Universal Benchmark Runner
Runs EPA augmentation benchmarks for any model on any dataset
Handles both online augmentation (LSTM, ResNet) and offline augmentation (RF)

Usage:
    # Using config file (recommended)
    python benchmark_runner.py --model lstm --dataset subcellular_localization_2
    
    # Using BenchmarkConfig (legacy)
    python benchmark_runner.py --benchmark quick_test
"""

import sys
import os
import json
import random
import numpy as np
import torch
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from tqdm import tqdm

sys.path.insert(0, 'epa')
from epa_augmentations import augment_list

from benchmark_config import BenchmarkConfig
from dataset_config import get_dataset_config
from model_config import get_model_config, validate_model_dataset_compatibility
from config_loader import get_config_loader


class BenchmarkRunner:
    """Universal benchmark runner for all models and datasets"""
    
    def __init__(self, 
                 config: Optional[BenchmarkConfig] = None,
                 model_type: Optional[str] = None,
                 dataset_name: Optional[str] = None,
                 config_override: Optional[Dict[str, Any]] = None):
        """
        Initialize benchmark runner
        
        Args:
            config: Legacy BenchmarkConfig (deprecated)
            model_type: Model type (lstm, random_forest, resnet) - loads from YAML
            dataset_name: Dataset name - loads from YAML
            config_override: Override specific config values
        """
        # Load from YAML config if model_type and dataset_name provided
        if model_type and dataset_name:
            config_loader = get_config_loader()
            yaml_config = config_loader.load_model_config(model_type, dataset_name)
            
            # Apply overrides if provided
            if config_override:
                self._apply_overrides(yaml_config, config_override)
            
            # Convert YAML config to attributes
            self.config_dict = yaml_config
            self.model_type = model_type
            self.dataset_name = dataset_name
            self.using_yaml = True
            
            print(f"\n{'='*70}")
            print(f"Loaded configuration from YAML")
            print(f"   Model: {model_type}")
            print(f"   Dataset: {dataset_name}")
            print(f"{'='*70}\n")
            
        # Use legacy BenchmarkConfig
        elif config:
            self.config = config
            self.model_type = config.model_type
            self.dataset_name = config.dataset_name
            self.using_yaml = False
            
            print(f"\n{'='*70}")
            print(f"Using legacy BenchmarkConfig (consider migrating to YAML)")
            print(f"{'='*70}\n")
        else:
            raise ValueError("Must provide either (model_type, dataset_name) or config")
        
        self.results = []
        
        # Validate compatibility
        dataset_cfg = get_dataset_config(self.dataset_name)
        model_cfg = get_model_config(self.model_type)
        
        if not validate_model_dataset_compatibility(self.model_type, dataset_cfg):
            raise ValueError(
                f"Model {self.model_type} not compatible with dataset {self.dataset_name}\n"
                f"Task: {dataset_cfg['task_type']}, PPI: {not dataset_cfg['has_single_sequence']}"
            )
        
        self.dataset_cfg = dataset_cfg
        self.model_cfg = model_cfg
        
        # Set random seeds
        self._set_seeds(42)
        
        # Print configuration summary
        self._print_config_summary()
    
    def _apply_overrides(self, config: Dict, overrides: Dict):
        """Recursively apply config overrides"""
        for key, value in overrides.items():
            if isinstance(value, dict) and key in config:
                self._apply_overrides(config[key], value)
            else:
                config[key] = value
    
    def _print_config_summary(self):
        """Print configuration summary"""
        print(f"\n{'='*70}")
        print(f"Benchmark Runner Initialized")
        print(f"{'='*70}")
        print(f"Model: {self.model_cfg['name']}")
        print(f"Dataset: {self.dataset_cfg['name']}")
        print(f"Task: {self.dataset_cfg['task_type']}")
        
        if self.using_yaml:
            strategy = self.config_dict['augmentation']['strategy']
            print(f"Strategy: {strategy}")
            print(f"Epochs: {self.config_dict['training']['epochs']}")
            print(f"Batch Size: {self.config_dict['training'].get('batch_size', 'N/A')}")
            print(f"Learning Rate: {self.config_dict['training'].get('learning_rate', 'N/A')}")
        else:
            print(f"Strategy: {self.config.strategy}")
            print(f"Augmentations: {len(self.config.augmentations)}")
        
        print(f"{'='*70}\n")
    
    def _set_seeds(self, seed: int):
        """Set random seeds for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
    
    def run(self) -> List[Dict[str, Any]]:
        """Run the benchmark"""
        
        if self.config.strategy == 'online_augmentation':
            return self._run_online_augmentation()
        else:
            return self._run_offline_augmentation()
    
    def _run_online_augmentation(self) -> List[Dict[str, Any]]:
        """
        Run benchmark with online augmentation (for LSTM, ResNet, ESM-2)
        Augmentations applied during training
        """
        from trainers.deep_learning_trainer import DeepLearningTrainer
        
        trainer = DeepLearningTrainer(self.config, self.dataset_cfg, self.model_cfg)
        
        # Get augmentation functions
        ops = augment_list()
        
        # Baseline (no augmentation)
        print(f"\n{'='*70}\nRunning: baseline\n{'='*70}")
        result = trainer.train(augmentation_name='baseline', augmentation_fn=None, magnitude=0.0)
        self.results.append(result)
        
        # All augmentations
        for aug_name in self.config.augmentations:
            if aug_name == 'baseline':
                continue
            
            # Find augmentation function
            aug_fn = None
            magnitude = 0.0
            
            for fn, min_mag, max_mag in ops:
                if fn.__name__ == aug_name:
                    aug_fn = fn
                    magnitude = (min_mag + max_mag) / 2
                    break
            
            if aug_fn is None:
                print(f"Warning: Augmentation {aug_name} not found, skipping")
                continue
            
            print(f"\n{'='*70}\nRunning: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
            result = trainer.train(aug_name, aug_fn, magnitude)
            self.results.append(result)
        
        return self.results
    
    def _run_offline_augmentation(self) -> List[Dict[str, Any]]:
        """
        Run benchmark with offline augmentation (for Random Forest)
        Pre-augment data, then train
        """
        from trainers.traditional_ml_trainer import TraditionalMLTrainer
        
        trainer = TraditionalMLTrainer(self.config, self.dataset_cfg, self.model_cfg)
        
        # Get augmentation functions
        ops = augment_list()
        
        # Baseline (no augmentation)
        print(f"\n{'='*70}\nRunning: baseline\n{'='*70}")
        result = trainer.train(augmentation_name='baseline', augmentation_fn=None, magnitude=0.0)
        self.results.append(result)
        
        # All augmentations
        for aug_name in self.config.augmentations:
            if aug_name == 'baseline':
                continue
            
            # Find augmentation function
            aug_fn = None
            magnitude = 0.0
            
            for fn, min_mag, max_mag in ops:
                if fn.__name__ == aug_name:
                    aug_fn = fn
                    magnitude = (min_mag + max_mag) / 2
                    break
            
            if aug_fn is None:
                print(f"Warning: Augmentation {aug_name} not found, skipping")
                continue
            
            print(f"\n{'='*70}\nRunning: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
            result = trainer.train(aug_name, aug_fn, magnitude)
            self.results.append(result)
        
        return self.results
    
    def save_results(self, output_path: str = None):
        """Save benchmark results to JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.config.output_dir}/benchmark_{self.config.model_type}_{self.config.dataset_name}_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        output_data = {
            'config': self.config.to_dict(),
            'dataset_config': self.dataset_cfg,
            'model_config': self.model_cfg,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Results saved to: {output_path}")
        print(f"{'='*70}\n")
        
        return output_path
    
    def print_summary(self):
        """Print benchmark summary"""
        if not self.results:
            print("No results to summarize")
            return
        
        print(f"\n{'='*70}")
        print("Benchmark Summary")
        print(f"{'='*70}")
        print(f"Model: {self.config.model_type}")
        print(f"Dataset: {self.config.dataset_name}")
        print(f"Total augmentations tested: {len(self.results)}")
        
        # Determine metric type
        task_type = self.dataset_cfg.get('task_type', 'classification')
        
        if task_type == 'regression':
            # Sort by test Spearman
            sorted_results = sorted(
                self.results,
                key=lambda x: x.get('test_spearman', -1),
                reverse=True
            )
            print("\nTop 5 Augmentations by Test Spearman Correlation:")
            for i, r in enumerate(sorted_results[:5], 1):
                spearman = r.get('test_spearman', 0)
                print(f"  {i}. {r['augmentation']:20s} - Spearman: {spearman:.4f}")
        else:
            # Sort by test accuracy
            sorted_results = sorted(
                self.results,
                key=lambda x: x.get('test_acc', 0),
                reverse=True
            )
            print("\nTop 5 Augmentations by Test Accuracy:")
            for i, r in enumerate(sorted_results[:5], 1):
                acc = r.get('test_acc', 0)
                mcc = r.get('test_mcc', 0)
                print(f"  {i}. {r['augmentation']:20s} - Acc: {acc:.4f}, MCC: {mcc:.4f}")
        
        print(f"{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal EPA Benchmark Runner')
    parser.add_argument('--model', type=str, required=True,
                       help='Model type (lstm, random_forest, resnet, esm2)')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Dataset name')
    parser.add_argument('--augmentations', type=str, nargs='+',
                       default=['baseline'],
                       help='List of augmentation names (or "all" for all 23)')
    parser.add_argument('--epochs', type=int, default=30,
                       help='Number of epochs (for deep learning models)')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--quick-test', action='store_true',
                       help='Run quick test with subset of data')
    parser.add_argument('--output-dir', type=str, default='benchmark_results',
                       help='Output directory for results')
    args = parser.parse_args()
    
    # Expand "all" to all augmentation names
    if args.augmentations == ['all']:
        ops = augment_list()
        args.augmentations = ['baseline'] + [fn.__name__ for fn, _, _ in ops]
    
    # Create config
    config = BenchmarkConfig(
        model_type=args.model,
        dataset_name=args.dataset,
        augmentations=args.augmentations,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_subset=args.quick_test,
        subset_size=1000 if args.quick_test else None,
        output_dir=args.output_dir
    )
    
    # Run benchmark
    runner = BenchmarkRunner(config)
    results = runner.run()
    
    # Save and summarize
    runner.save_results()
    runner.print_summary()
