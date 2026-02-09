#!/usr/bin/env python3
"""
Model Configuration for EPA Benchmarks
Supports multiple model architectures: LSTM, Random Forest, ResNet, ESM-2, etc.
"""

from typing import Dict, Any, List

# Available model types
MODEL_TYPES = {
    'lstm': {
        'name': 'Bidirectional LSTM',
        'type': 'deep_learning',
        'requires_gpu': True,
        'supports_tasks': ['classification', 'regression', 'residue_classification'],
        'supports_ppi': True,
        'supports_augmentation': True,  # Can augment during training
        'default_params': {
            'embed_dim': 128,
            'hidden_dim': 256,
            'num_layers': 2,
            'dropout': 0.3,
            'bidirectional': True
        }
    },
    'random_forest': {
        'name': 'Random Forest',
        'type': 'traditional_ml',
        'requires_gpu': False,
        'supports_tasks': ['classification', 'regression'],
        'supports_ppi': True,
        'supports_augmentation': False,  # Augment beforehand, not during training
        'default_params': {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'n_jobs': -1,
            'random_state': 42
        }
    },
    'resnet': {
        'name': 'ResNet for Proteins',
        'type': 'deep_learning',
        'requires_gpu': True,
        'supports_tasks': ['classification', 'regression', 'residue_classification'],
        'supports_ppi': True,
        'supports_augmentation': True,
        'default_params': {
            'embed_dim': 128,
            'channels': [64, 128, 256, 512],
            'num_blocks': [2, 2, 2, 2],
            'dropout': 0.3
        }
    },
    'esm2': {
        'name': 'ESM-2 (35M parameters)',
        'type': 'pretrained_transformer',
        'requires_gpu': True,
        'supports_tasks': ['classification', 'regression'],
        'supports_ppi': False,  # Need special handling for dual sequences
        'supports_augmentation': True,
        'default_params': {
            'model_name': 'esm2_t12_35M_UR50D',
            'freeze_encoder': False,
            'dropout': 0.3
        }
    }
}


def get_model_config(model_type: str) -> Dict[str, Any]:
    """Get configuration for a specific model type"""
    if model_type not in MODEL_TYPES:
        available = ', '.join(MODEL_TYPES.keys())
        raise ValueError(f"Unknown model type: {model_type}. Available: {available}")
    return MODEL_TYPES[model_type].copy()


def list_available_models():
    """List all available models with their capabilities"""
    print("\n" + "="*70)
    print("Available Models for EPA Benchmarking")
    print("="*70)
    
    for model_id, config in MODEL_TYPES.items():
        print(f"\n{model_id}:")
        print(f"  Name: {config['name']}")
        print(f"  Type: {config['type']}")
        print(f"  GPU Required: {'Yes' if config['requires_gpu'] else 'No'}")
        print(f"  Tasks: {', '.join(config['supports_tasks'])}")
        print(f"  PPI Support: {'Yes' if config['supports_ppi'] else 'No'}")
        print(f"  Online Augmentation: {'Yes' if config['supports_augmentation'] else 'No'}")


def get_models_for_task(task_type: str) -> List[str]:
    """Get list of model types that support a given task"""
    supported = []
    for model_id, config in MODEL_TYPES.items():
        if task_type in config['supports_tasks']:
            supported.append(model_id)
    return supported


def validate_model_dataset_compatibility(model_type: str, dataset_config: Dict[str, Any]) -> bool:
    """Check if a model is compatible with a dataset"""
    model_cfg = get_model_config(model_type)
    task_type = dataset_config.get('task_type', 'classification')
    is_ppi = not dataset_config['has_single_sequence']
    
    # Check task support
    if task_type not in model_cfg['supports_tasks']:
        return False
    
    # Check PPI support
    if is_ppi and not model_cfg['supports_ppi']:
        return False
    
    return True


if __name__ == "__main__":
    list_available_models()
    
    print("\n" + "="*70)
    print("Models supporting classification:")
    print(get_models_for_task('classification'))
    
    print("\nModels supporting regression:")
    print(get_models_for_task('regression'))
    
    print("\nModels supporting residue_classification:")
    print(get_models_for_task('residue_classification'))
    print("="*70 + "\n")
