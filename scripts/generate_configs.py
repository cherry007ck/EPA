#!/usr/bin/env python3
"""
Generate all configuration files for EPA benchmarks
Creates configs for LSTM, Random Forest, and ResNet on all 8 datasets
"""

import yaml
from pathlib import Path


def get_base_config(model_type, dataset_name, dataset_info):
    """Get base configuration template for a model-dataset pair"""
    
    config = {
        'model': {
            'type': model_type,
            'architecture': None,
            'parameters': {}
        },
        'training': {},
        'augmentation': {},
        'dataset': {
            'name': dataset_name,
            'task_type': dataset_info['task_type'],
            'num_classes': dataset_info['num_classes'],
            'metric': dataset_info['metric'],
            'secondary_metric': dataset_info.get('secondary_metric', 'mcc')
        },
        'compute': {},
        'output': {
            'save_model': True,
            'save_best_only': True,
            'log_interval': 100
        }
    }
    
    # Model-specific configuration
    if model_type == 'lstm':
        config['model']['architecture'] = dataset_info.get('lstm_arch', 'LSTMModel')
        config['model']['parameters'] = {
            'embed_dim': 128,
            'hidden_dim': 256,
            'num_layers': 2,
            'dropout': 0.3,
            'bidirectional': True
        }
        config['training'] = {
            'epochs': 30,
            'batch_size': dataset_info.get('batch_size', 64),
            'learning_rate': 0.001,
            'optimizer': 'adam',
            'weight_decay': 0.0,
            'gradient_clip': 1.0,
            'patience': 10,
            'min_delta': 0.0001
        }
        config['augmentation'] = {
            'strategy': 'online',
            'all_augmentations': True
        }
        config['compute'] = {
            'device': 'cuda',
            'num_workers': 4,
            'pin_memory': True,
            'mixed_precision': False
        }
    
    elif model_type == 'random_forest':
        config['model']['architecture'] = 'RandomForestModel'
        config['model']['parameters'] = {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'n_jobs': -1,
            'random_state': 42
        }
        config['training'] = {
            'epochs': 1,  # RF doesn't use epochs
            'max_samples': dataset_info.get('rf_max_samples', None),
            'feature_type': 'aa_composition'  # aa_composition, dipeptide, etc.
        }
        config['augmentation'] = {
            'strategy': 'offline',  # Pre-augment data
            'all_augmentations': True
        }
        config['compute'] = {
            'device': 'cpu',
            'n_jobs': -1
        }
    
    elif model_type == 'resnet':
        config['model']['architecture'] = dataset_info.get('resnet_arch', 'ProteinResNet')
        config['model']['parameters'] = {
            'embed_dim': 128,
            'channels': [64, 128, 256, 512],
            'num_blocks': [2, 2, 2, 2],
            'dropout': 0.3
        }
        config['training'] = {
            'epochs': 30,
            'batch_size': dataset_info.get('resnet_batch_size', 32),
            'learning_rate': 0.001,
            'optimizer': 'adam',
            'weight_decay': 0.0001,  # ResNet benefits from weight decay
            'gradient_clip': 1.0,
            'patience': 10,
            'min_delta': 0.0001
        }
        config['augmentation'] = {
            'strategy': 'online',
            'all_augmentations': True
        }
        config['compute'] = {
            'device': 'cuda',
            'num_workers': 4,
            'pin_memory': True,
            'mixed_precision': True  # ResNet can benefit from mixed precision
        }
    
    return config


# Dataset information
DATASETS = {
    'subcellular_localization_2': {
        'task_type': 'classification',
        'num_classes': 2,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 5910,
        'lstm_arch': 'LSTMModel',
        'resnet_arch': 'ProteinResNet',
        'batch_size': 64,
        'resnet_batch_size': 32,
        'rf_max_samples': None
    },
    'subcellular_localization': {
        'task_type': 'classification',
        'num_classes': 10,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 8945,
        'lstm_arch': 'LSTMModel',
        'resnet_arch': 'ProteinResNet',
        'batch_size': 64,
        'resnet_batch_size': 32,
        'rf_max_samples': None
    },
    'remote_homology_fold': {
        'task_type': 'classification',
        'num_classes': 1195,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 12313,
        'lstm_arch': 'LSTMModel',
        'resnet_arch': 'ProteinResNet',
        'batch_size': 32,  # Smaller due to large number of classes
        'resnet_batch_size': 16,
        'rf_max_samples': 10000  # Limit for RF due to large dataset
    },
    'yeast_ppi': {
        'task_type': 'classification',
        'num_classes': 2,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 11264,
        'lstm_arch': 'PPIModel',
        'resnet_arch': 'ProteinResNetPPI',
        'batch_size': 32,  # PPI needs more memory
        'resnet_batch_size': 16,
        'rf_max_samples': None
    },
    'beta_lactamase': {
        'task_type': 'regression',
        'num_classes': 1,
        'metric': 'spearman',
        'secondary_metric': 'mse',
        'samples': 4158,
        'lstm_arch': 'RegressionModel',
        'resnet_arch': 'ProteinResNetRegression',
        'batch_size': 64,
        'resnet_batch_size': 32,
        'rf_max_samples': None
    },
    'secondary_structure': {
        'task_type': 'residue_classification',
        'num_classes': 3,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 8679,
        'lstm_arch': 'ResidueLSTMModel',
        'resnet_arch': 'ProteinResNetResidue',
        'batch_size': 32,  # Residue-level needs more memory
        'resnet_batch_size': 16,
        'rf_max_samples': None  # RF doesn't support residue-level
    },
    'human_ppi': {
        'task_type': 'classification',
        'num_classes': 2,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 35670,
        'lstm_arch': 'PPIModel',
        'resnet_arch': 'ProteinResNetPPI',
        'batch_size': 32,
        'resnet_batch_size': 16,
        'rf_max_samples': 15000  # Limit for large dataset
    },
    'solubility': {
        'task_type': 'classification',
        'num_classes': 2,
        'metric': 'accuracy',
        'secondary_metric': 'mcc',
        'samples': 62479,
        'lstm_arch': 'LSTMModel',
        'resnet_arch': 'ProteinResNet',
        'batch_size': 32,  # Large dataset, smaller batches
        'resnet_batch_size': 16,
        'rf_max_samples': 15000
    }
}


def generate_all_configs(output_dir='configs'):
    """Generate all configuration files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    models = ['lstm', 'random_forest', 'resnet']
    
    print("Generating configuration files...")
    print("="*70)
    
    generated_count = 0
    skipped_count = 0
    
    for model_type in models:
        print(f"\n{model_type.upper()}:")
        
        # Create model subdirectory
        model_dir = output_path / model_type
        model_dir.mkdir(exist_ok=True)
        
        for dataset_name, dataset_info in DATASETS.items():
            # Skip RF for residue-level tasks
            if model_type == 'random_forest' and dataset_info['task_type'] == 'residue_classification':
                print(f"   - {dataset_name} (not supported)")
                skipped_count += 1
                continue
            
            config = get_base_config(model_type, dataset_name, dataset_info)
            
            # Save to file in model subdirectory
            filename = f"{model_type}_{dataset_name}.yaml"
            filepath = model_dir / filename
            
            with open(filepath, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            print(f"   - {dataset_name}")
            generated_count += 1

    print("\n" + "="*70)
    print(f"Generated {generated_count} configuration files")
    print(f"Skipped {skipped_count} incompatible combinations")
    print(f"Location: {output_path.absolute()}")
    print(f"Organized in subdirectories: lstm/, random_forest/, resnet/")
    print("="*70 + "\n")


if __name__ == "__main__":
    generate_all_configs()
