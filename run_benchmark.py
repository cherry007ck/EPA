#!/usr/bin/env python3
"""
Production-Grade Benchmark Runner
Uses YAML configuration files for all settings
"""

import sys
import os
import argparse
import json
import random
import numpy as np
import torch
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

sys.path.insert(0, 'epa')
from epa_augmentations import augment_list

from dataset_config import get_dataset_config
from model_config import get_model_config, validate_model_dataset_compatibility
from config_loader import get_config_loader


class ProductionBenchmarkRunner:
    """Production-grade benchmark runner using YAML configurations"""
    
    def __init__(self, model_type: str, dataset_name: str, config_override: Dict = None):
        """
        Initialize benchmark runner
        
        Args:
            model_type: Model type (lstm, random_forest, resnet)
            dataset_name: Dataset name
            config_override: Override specific config values
        """
        # Load configuration from YAML
        config_loader = get_config_loader()
        self.config = config_loader.load_model_config(model_type, dataset_name)
        
        # Apply overrides if provided
        if config_override:
            self._apply_overrides(self.config, config_override)
        
        self.model_type = model_type
        self.dataset_name = dataset_name
        self.results = []
        
        # Load dataset and model info
        self.dataset_cfg = get_dataset_config(dataset_name)
        self.model_cfg = get_model_config(model_type)
        
        # Validate compatibility
        if not validate_model_dataset_compatibility(model_type, self.dataset_cfg):
            raise ValueError(
                f"Model {model_type} not compatible with dataset {dataset_name}\n"
                f"Task: {self.dataset_cfg['task_type']}"
            )
        
        # Set random seeds
        self._set_seeds(42)
        
        # Print configuration
        self._print_config()
    
    def _apply_overrides(self, config: Dict, overrides: Dict):
        """Recursively apply config overrides"""
        for key, value in overrides.items():
            if isinstance(value, dict) and key in config:
                self._apply_overrides(config[key], value)
            else:
                config[key] = value
    
    def _set_seeds(self, seed: int):
        """Set random seeds for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
    
    def _print_config(self):
        """Print configuration summary"""
        print(f"\n{'='*80}")
        print(f"🚀 PRODUCTION BENCHMARK RUNNER")
        print(f"{'='*80}")
        print(f"📋 Model:        {self.model_cfg['name']} ({self.model_type})")
        print(f"📊 Dataset:      {self.dataset_cfg['name']}")
        print(f"🎯 Task:         {self.dataset_cfg['task_type']}")
        print(f"📈 Metric:       {self.config['dataset']['metric']}")
        
        training_cfg = self.config['training']
        print(f"\n⚙️  Training Configuration:")
        print(f"   Epochs:       {training_cfg.get('epochs', 'N/A')}")
        print(f"   Batch Size:   {training_cfg.get('batch_size', 'N/A')}")
        print(f"   Learning Rate: {training_cfg.get('learning_rate', 'N/A')}")
        print(f"   Optimizer:    {training_cfg.get('optimizer', 'N/A')}")
        
        aug_cfg = self.config['augmentation']
        print(f"\n🔄 Augmentation Strategy: {aug_cfg['strategy']}")
        
        compute_cfg = self.config['compute']
        print(f"\n💻 Compute:")
        print(f"   Device:       {compute_cfg.get('device', 'cpu')}")
        if 'num_workers' in compute_cfg:
            print(f"   Workers:      {compute_cfg['num_workers']}")
        
        print(f"{'='*80}\n")
    
    def run(self) -> List[Dict[str, Any]]:
        """Run the benchmark based on augmentation strategy"""
        strategy = self.config['augmentation']['strategy']
        
        if strategy == 'online':
            return self._run_online_augmentation()
        elif strategy == 'offline':
            return self._run_offline_augmentation()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _run_online_augmentation(self) -> List[Dict[str, Any]]:
        """Run with online augmentation (LSTM, ResNet)"""
        from trainers.deep_learning_trainer import DeepLearningTrainer
        
        # Convert config to legacy format for trainer (temporary)
        from benchmark_config import BenchmarkConfig
        legacy_config = self._create_legacy_config()
        
        trainer = DeepLearningTrainer(legacy_config, self.dataset_cfg, self.model_cfg)
        
        # Get augmentation functions
        ops = augment_list()
        augmentations = ['baseline'] + [fn.__name__ for fn, _, _ in ops]
        
        # Baseline
        print(f"\n{'='*70}\nRunning: baseline\n{'='*70}")
        result = trainer.train(augmentation_name='baseline', augmentation_fn=None, magnitude=0.0)
        self.results.append(result)
        
        # All augmentations
        for aug_name in augmentations[1:]:  # Skip baseline
            # Find augmentation function
            aug_fn = None
            magnitude = 0.0
            
            for fn, min_mag, max_mag in ops:
                if fn.__name__ == aug_name:
                    aug_fn = fn
                    magnitude = (min_mag + max_mag) / 2
                    break
            
            if aug_fn is None:
                continue
            
            print(f"\n{'='*70}\nRunning: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
            result = trainer.train(aug_name, aug_fn, magnitude)
            self.results.append(result)
        
        return self.results
    
    def _run_offline_augmentation(self) -> List[Dict[str, Any]]:
        """Run with offline augmentation (Random Forest)"""
        from trainers.traditional_ml_trainer import TraditionalMLTrainer
        
        # Convert config to legacy format for trainer (temporary)
        from benchmark_config import BenchmarkConfig
        legacy_config = self._create_legacy_config()
        
        trainer = TraditionalMLTrainer(legacy_config, self.dataset_cfg, self.model_cfg)
        
        # Get augmentation functions
        ops = augment_list()
        augmentations = ['baseline'] + [fn.__name__ for fn, _, _ in ops]
        
        # Baseline
        print(f"\n{'='*70}\nRunning: baseline\n{'='*70}")
        result = trainer.train(augmentation_name='baseline', augmentation_fn=None, magnitude=0.0)
        self.results.append(result)
        
        # All augmentations
        for aug_name in augmentations[1:]:
            aug_fn = None
            magnitude = 0.0
            
            for fn, min_mag, max_mag in ops:
                if fn.__name__ == aug_name:
                    aug_fn = fn
                    magnitude = (min_mag + max_mag) / 2
                    break
            
            if aug_fn is None:
                continue
            
            print(f"\n{'='*70}\nRunning: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
            result = trainer.train(aug_name, aug_fn, magnitude)
            self.results.append(result)
        
        return self.results
    
    def _create_legacy_config(self):
        """Create legacy BenchmarkConfig from YAML config (temporary bridge)"""
        from benchmark_config import BenchmarkConfig
        
        ops = augment_list()
        augmentations = [fn.__name__ for fn, _, _ in ops]
        
        return BenchmarkConfig(
            model_type=self.model_type,
            dataset_name=self.dataset_name,
            augmentations=augmentations,
            epochs=self.config['training'].get('epochs', 30),
            batch_size=self.config['training'].get('batch_size', 32),
            device=self.config['training'].get('device', 'cuda')
        )
    
    def save_results(self, output_dir: str = 'results'):
        """Save results to JSON file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.model_type}_{self.dataset_name}_{timestamp}.json"
        filepath = output_path / filename
        
        results_data = {
            'model_type': self.model_type,
            'dataset_name': self.dataset_name,
            'config': self.config,
            'results': self.results,
            'timestamp': timestamp
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ Results saved to: {filepath}")
        print(f"{'='*70}\n")
        
        return str(filepath)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run EPA benchmark with YAML config')
    parser.add_argument('--model', type=str, required=True,
                       choices=['lstm', 'random_forest', 'resnet'],
                       help='Model type')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Dataset name')
    parser.add_argument('--epochs', type=int,
                       help='Override epochs')
    parser.add_argument('--batch-size', type=int,
                       help='Override batch size')
    parser.add_argument('--lr', type=float,
                       help='Override learning rate')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Build config overrides
    config_override = {}
    if args.epochs:
        config_override.setdefault('training', {})['epochs'] = args.epochs
    if args.batch_size:
        config_override.setdefault('training', {})['batch_size'] = args.batch_size
    if args.lr:
        config_override.setdefault('training', {})['learning_rate'] = args.lr
    
    # Run benchmark
    runner = ProductionBenchmarkRunner(
        model_type=args.model,
        dataset_name=args.dataset,
        config_override=config_override if config_override else None
    )
    
    results = runner.run()
    runner.save_results(args.output_dir)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"✅ Benchmark Complete!")
    print(f"{'='*70}")
    print(f"Total runs: {len(results)}")
    
    # Find best result
    if results:
        metric = results[0]['metric']
        best = max(results, key=lambda x: x[metric])
        print(f"\nBest {metric}: {best[metric]:.4f} (augmentation: {best['augmentation']})")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
