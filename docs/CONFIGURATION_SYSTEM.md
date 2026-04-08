# Production-Grade Configuration System

## Overview

This project uses a YAML-based configuration system for managing all benchmarking parameters. All settings are externalized to configuration files, making the code modular, maintainable, and production-ready.

## Directory Structure

```
aug/EPA/
├── configs/                      # Configuration files
│   ├── lstm_*.yaml              # LSTM configs (8 files)
│   ├── random_forest_*.yaml     # Random Forest configs (7 files)
│   └── resnet_*.yaml            # ResNet configs (8 files)
├── models/                       # Model implementations
│   ├── lstm_models.py
│   ├── random_forest_models.py
│   └── resnet_models.py
├── trainers/                     # Training implementations
│   ├── deep_learning_trainer.py
│   └── traditional_ml_trainer.py
├── config_loader.py              # Configuration loader
├── run_benchmark.py              # Main runner (YAML-based)
└── generate_configs.py           # Config generator
```

## Configuration Files

### Total Configurations

- **23 configuration files** covering:
  - **3 models**: LSTM, Random Forest, ResNet
  - **8 datasets**: subcellular_localization_2, subcellular_localization, remote_homology_fold, yeast_ppi, beta_lactamase, secondary_structure, human_ppi, solubility
  - **Note**: Random Forest doesn't support residue-level tasks (secondary_structure)

### Configuration Structure

Each YAML file contains 6 main sections:

```yaml
model:                     # Model architecture and parameters
  type: lstm
  architecture: LSTMModel
  parameters:
    embed_dim: 128
    hidden_dim: 256
    num_layers: 2
    dropout: 0.3
    bidirectional: true

training:                  # Training hyperparameters
  epochs: 30
  batch_size: 64
  learning_rate: 0.001
  optimizer: adam
  weight_decay: 0.0
  gradient_clip: 1.0
  patience: 10
  min_delta: 0.0001

augmentation:              # Augmentation strategy
  strategy: online         # 'online' or 'offline'
  all_augmentations: true

dataset:                   # Dataset information
  name: subcellular_localization_2
  task_type: classification
  num_classes: 2
  metric: accuracy
  secondary_metric: mcc

compute:                   # Compute configuration
  device: cuda
  num_workers: 4
  pin_memory: true
  mixed_precision: false

output:                    # Output configuration
  save_model: true
  save_best_only: true
  log_interval: 100
```

## Usage

### 1. Running Benchmarks

#### Basic Usage

```bash
# Run LSTM on subcellular_localization_2
python run_benchmark.py --model lstm --dataset subcellular_localization_2

# Run Random Forest on solubility
python run_benchmark.py --model random_forest --dataset solubility

# Run ResNet on yeast_ppi
python run_benchmark.py --model resnet --dataset yeast_ppi
```

#### With Overrides

```bash
# Override epochs
python run_benchmark.py --model lstm --dataset human_ppi --epochs 50

# Override batch size and learning rate
python run_benchmark.py --model resnet --dataset solubility \
    --batch-size 16 --lr 0.0005
```

### 2. Listing Configurations

```bash
# List all configurations
python config_loader.py --list

# List only LSTM configurations
python config_loader.py --list --model lstm
```

### 3. Viewing Configuration Details

```bash
# View specific configuration
python config_loader.py --load lstm subcellular_localization_2

# View ResNet configuration
python config_loader.py --load resnet yeast_ppi
```

### 4. Testing the System

```bash
# Test all configurations
python test_config_system.py
```

## Configuration Loader API

### Loading Configurations

```python
from config_loader import get_config_loader

# Get loader instance (singleton)
loader = get_config_loader()

# Load specific configuration
config = loader.load_model_config('lstm', 'subcellular_localization_2')

# List available configurations
configs = loader.list_available_configs()
print(f"Found {len(configs)} configurations")

# List LSTM configurations only
lstm_configs = loader.list_available_configs('lstm')
```

### Configuration Validation

The loader automatically validates that all required sections are present:
- `model` - Model type, architecture, parameters
- `training` - Training hyperparameters
- `augmentation` - Augmentation strategy
- `dataset` - Dataset metadata
- `compute` - Compute resources
- `output` - Output settings

## Model-Specific Details

### LSTM Configuration

```yaml
model:
  type: lstm
  architecture: LSTMModel | PPIModel | RegressionModel | ResidueLSTMModel
  parameters:
    embed_dim: 128
    hidden_dim: 256
    num_layers: 2
    dropout: 0.3
    bidirectional: true

training:
  epochs: 30
  batch_size: 32-64    # Depends on task
  learning_rate: 0.001
  optimizer: adam
```

### Random Forest Configuration

```yaml
model:
  type: random_forest
  architecture: RandomForestModel
  parameters:
    n_estimators: 100
    max_depth: null     # Unlimited
    n_jobs: -1          # All cores
    random_state: 42

training:
  epochs: 1             # RF doesn't use epochs
  max_samples: null     # Optional: limit training samples
```

### ResNet Configuration

```yaml
model:
  type: resnet
  architecture: ProteinResNet | ProteinResNetPPI | ProteinResNetRegression | ProteinResNetResidue
  parameters:
    embed_dim: 128
    channels: [64, 128, 256, 512]
    num_blocks: [2, 2, 2, 2]
    dropout: 0.3

training:
  epochs: 30
  batch_size: 16-32     # Smaller than LSTM
  learning_rate: 0.001
  weight_decay: 0.0001  # ResNet benefits from weight decay
```

## Dataset-Specific Details

### Task Types

1. **Classification**: subcellular_localization_2, subcellular_localization, remote_homology_fold, yeast_ppi, human_ppi, solubility
2. **Regression**: beta_lactamase
3. **Residue Classification**: secondary_structure

### Batch Sizes by Dataset

| Dataset | LSTM | ResNet | RF |
|---------|------|--------|----|
| subcellular_localization_2 | 64 | 32 | N/A |
| subcellular_localization | 64 | 32 | N/A |
| remote_homology_fold | 32 | 16 | 10K limit |
| yeast_ppi | 32 | 16 | N/A |
| beta_lactamase | 64 | 32 | N/A |
| secondary_structure | 32 | 16 | Not supported |
| human_ppi | 32 | 16 | 15K limit |
| solubility | 32 | 16 | 15K limit |

## Adding New Configurations

### Method 1: Manual Creation

1. Create a new YAML file in `configs/`:
   ```bash
   cp configs/lstm_subcellular_localization_2.yaml configs/lstm_my_dataset.yaml
   ```

2. Edit the file with your parameters

3. Verify it loads:
   ```bash
   python config_loader.py --load lstm my_dataset
   ```

### Method 2: Programmatic Generation

1. Edit `generate_configs.py` and add your dataset:
   ```python
   DATASETS = {
       'my_dataset': {
           'task_type': 'classification',
           'num_classes': 5,
           'metric': 'accuracy',
           # ... other fields
       }
   }
   ```

2. Regenerate configs:
   ```bash
   python generate_configs.py
   ```

## Best Practices

### 1. Version Control

- Always commit configuration files with code changes
- Use meaningful config names: `{model}_{dataset}.yaml`
- Keep a backup before regenerating configs

### 2. Parameter Tuning

- Start with default configs
- Override specific parameters via CLI for experimentation
- Once optimal parameters found, update YAML file

### 3. Production Deployment

```bash
# Test configuration
python test_config_system.py

# Verify specific config
python config_loader.py --load lstm my_dataset

# Run benchmark
python run_benchmark.py --model lstm --dataset my_dataset
```

### 4. Monitoring

- Check output logs for loaded configuration
- Verify all parameters are as expected
- Monitor GPU memory usage vs configured batch sizes

## SLURM Integration

### Create SLURM Script

```bash
#!/bin/bash
#SBATCH --job-name=epa_lstm
#SBATCH --partition=uds-gpu
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --output=logs/lstm_%j.out
#SBATCH --error=logs/lstm_%j.err

source epa_venv/bin/activate

python run_benchmark.py \
    --model lstm \
    --dataset subcellular_localization_2 \
    --output-dir results/
```

### Submit Jobs

```bash
# Submit single job
sbatch run_lstm.sbatch

# Submit multiple jobs
for dataset in subcellular_localization_2 yeast_ppi solubility; do
    sbatch --export=DATASET=$dataset run_model.sbatch
done
```

## Troubleshooting

### Configuration Not Found

```bash
# List available configs
python config_loader.py --list

# Check if file exists
ls configs/lstm_my_dataset.yaml
```

### Invalid Configuration

```python
# The loader validates required sections
# Error messages will indicate missing fields
```

### CUDA Out of Memory

```bash
# Reduce batch size in config or via CLI
python run_benchmark.py --model resnet --dataset human_ppi --batch-size 8
```

## Performance Tips

1. **Batch Size**: Start with config defaults, adjust based on GPU memory
2. **Workers**: Use 4 workers per GPU for optimal data loading
3. **Mixed Precision**: Enable for ResNet to save memory (disabled by default for stability)
4. **Caching**: Configurations are cached after first load (3x speedup)

## Architecture Benefits

- Modular: models, trainers, and configs are separate
- Maintainable: all parameters in YAML, easy to update
- Reproducible: configurations are versioned with code
- Scalable: easy to add new models and datasets
- Validation, caching, and error handling
- CLI overrides for quick experimentation

## Summary

- 23 configurations for 3 models across 8 datasets
- YAML-based external configuration
- Validated on load with clear error messages
- Cached after first load
- CLI-friendly with override support
