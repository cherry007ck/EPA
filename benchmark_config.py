#!/usr/bin/env python3
"""
Benchmark Configuration System
Central configuration for running EPA benchmarks across models and datasets
"""

from typing import Dict, Any, List, Optional

# Benchmark execution strategies
BENCHMARK_STRATEGIES = {
    'lstm': 'online_augmentation',      # Augment during training
    'random_forest': 'offline_augmentation',  # Pre-augment data
    'resnet': 'online_augmentation',    # Augment during training
    'esm2': 'online_augmentation'       # Augment during training
}


class BenchmarkConfig:
    """Configuration for a benchmark run"""
    
    def __init__(
        self,
        model_type: str,
        dataset_name: str,
        augmentations: List[str] = None,
        epochs: int = 30,
        batch_size: int = 64,
        n_jobs: int = -1,  # For traditional ML models
        use_subset: bool = False,  # For quick testing
        subset_size: int = 5000,
        output_dir: str = 'benchmark_results',
        device: str = 'cuda'
    ):
        self.model_type = model_type
        self.dataset_name = dataset_name
        self.augmentations = augmentations or ['baseline']
        self.epochs = epochs
        self.batch_size = batch_size
        self.n_jobs = n_jobs
        self.use_subset = use_subset
        self.subset_size = subset_size
        self.output_dir = output_dir
        self.device = device
        
        # Determine strategy
        self.strategy = BENCHMARK_STRATEGIES.get(model_type, 'online_augmentation')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'model_type': self.model_type,
            'dataset_name': self.dataset_name,
            'augmentations': self.augmentations,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'n_jobs': self.n_jobs,
            'use_subset': self.use_subset,
            'subset_size': self.subset_size,
            'output_dir': self.output_dir,
            'device': self.device,
            'strategy': self.strategy
        }
    
    def __repr__(self):
        return f"BenchmarkConfig(model={self.model_type}, dataset={self.dataset_name}, augs={len(self.augmentations)})"


def get_default_config(model_type: str, dataset_name: str, quick_test: bool = False) -> BenchmarkConfig:
    """Get default configuration for a model-dataset pair"""
    
    # Default parameters based on model type
    if model_type == 'lstm':
        config = BenchmarkConfig(
            model_type=model_type,
            dataset_name=dataset_name,
            epochs=30,
            batch_size=64,
            device='cuda'
        )
    elif model_type == 'random_forest':
        config = BenchmarkConfig(
            model_type=model_type,
            dataset_name=dataset_name,
            epochs=1,  # RF doesn't use epochs
            batch_size=None,  # RF doesn't use batches
            n_jobs=-1,
            device='cpu'
        )
    elif model_type == 'resnet':
        config = BenchmarkConfig(
            model_type=model_type,
            dataset_name=dataset_name,
            epochs=30,
            batch_size=32,  # ResNet typically needs smaller batches
            device='cuda'
        )
    elif model_type == 'esm2':
        config = BenchmarkConfig(
            model_type=model_type,
            dataset_name=dataset_name,
            epochs=10,  # Pretrained models need fewer epochs
            batch_size=16,  # ESM-2 is memory intensive
            device='cuda'
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Quick test mode
    if quick_test:
        config.use_subset = True
        config.subset_size = 1000
        config.epochs = min(5, config.epochs)
        config.augmentations = ['baseline', 'random_deletion', 'random_insertion']
    
    return config


# Predefined benchmark suites
BENCHMARK_SUITES = {
    'quick_test': {
        'description': 'Quick test with 3 augmentations on small subset',
        'models': ['lstm', 'random_forest'],
        'datasets': ['solubility'],
        'augmentations': ['baseline', 'random_deletion', 'random_insertion'],
        'use_subset': True,
        'subset_size': 1000,
        'epochs': 5
    },
    
    'full_benchmark': {
        'description': 'Full benchmark with all 23 augmentations',
        'models': ['lstm', 'random_forest', 'resnet', 'esm2'],
        'datasets': [
            'subcellular_localization_2',
            'subcellular_localization',
            'remote_homology_fold',
            'yeast_ppi',
            'beta_lactamase',
            'secondary_structure',
            'human_ppi',
            'solubility'
        ],
        'augmentations': 'all',  # Will be expanded to all 23
        'use_subset': False,
        'epochs': 30
    },
    
    'classification_only': {
        'description': 'Binary and multi-class classification tasks',
        'models': ['lstm', 'random_forest'],
        'datasets': [
            'subcellular_localization_2',
            'subcellular_localization',
            'yeast_ppi',
            'human_ppi',
            'solubility'
        ],
        'augmentations': 'all',
        'use_subset': False,
        'epochs': 30
    },
    
    'regression_only': {
        'description': 'Regression tasks',
        'models': ['lstm', 'random_forest', 'resnet'],
        'datasets': ['beta_lactamase'],
        'augmentations': 'all',
        'use_subset': False,
        'epochs': 30
    },
    
    'rf_vs_lstm': {
        'description': 'Compare Random Forest vs LSTM on all datasets',
        'models': ['lstm', 'random_forest'],
        'datasets': 'all',
        'augmentations': 'all',
        'use_subset': False,
        'epochs': 30
    }
}


def get_benchmark_suite(suite_name: str) -> Dict[str, Any]:
    """Get a predefined benchmark suite configuration"""
    if suite_name not in BENCHMARK_SUITES:
        available = ', '.join(BENCHMARK_SUITES.keys())
        raise ValueError(f"Unknown suite: {suite_name}. Available: {available}")
    return BENCHMARK_SUITES[suite_name].copy()


def list_benchmark_suites():
    """List all available benchmark suites"""
    print("\n" + "="*70)
    print("Available Benchmark Suites")
    print("="*70)
    
    for suite_name, config in BENCHMARK_SUITES.items():
        print(f"\n{suite_name}:")
        print(f"  Description: {config['description']}")
        print(f"  Models: {config['models']}")
        if isinstance(config['datasets'], list):
            print(f"  Datasets: {len(config['datasets'])} datasets")
        else:
            print(f"  Datasets: {config['datasets']}")
        print(f"  Augmentations: {config['augmentations']}")
        if config['use_subset']:
            print(f"  Using subset: {config['subset_size']} samples")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark Configuration')
    parser.add_argument('--list-suites', action='store_true',
                       help='List available benchmark suites')
    parser.add_argument('--suite', type=str,
                       help='Show details of a specific suite')
    args = parser.parse_args()
    
    if args.list_suites:
        list_benchmark_suites()
    elif args.suite:
        suite = get_benchmark_suite(args.suite)
        print(f"\nSuite: {args.suite}")
        print("="*70)
        for key, value in suite.items():
            print(f"{key}: {value}")
    else:
        # Show example usage
        print("\nExample configurations:")
        print("="*70)
        
        # LSTM config
        lstm_config = get_default_config('lstm', 'solubility')
        print(f"\nLSTM config: {lstm_config}")
        
        # RF config
        rf_config = get_default_config('random_forest', 'beta_lactamase')
        print(f"RF config: {rf_config}")
        
        # Quick test
        quick_config = get_default_config('lstm', 'solubility', quick_test=True)
        print(f"Quick test config: {quick_config}")
