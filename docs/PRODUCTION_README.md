# EPA Benchmark System

## Quick Start

```bash
# Activate environment
source epa_venv/bin/activate

# Run a benchmark
python run_benchmark.py --model lstm --dataset subcellular_localization_2

# List all configurations
python config_loader.py --list

# Test the system
python test_config_system.py
```

## System Overview

Benchmarking system with 23 YAML configurations for 3 models across 8 datasets.

### Models
- LSTM (~500K params): Online augmentation, bidirectional, 2-layer
- Random Forest (feature-based): Offline augmentation, 25 features
- ResNet (1-4M params): Online augmentation, 4 stages

### Datasets
1. `subcellular_localization_2` - Binary classification (2 classes)
2. `subcellular_localization` - Multi-class (10 classes)
3. `remote_homology_fold` - Large-scale classification (1195 classes)
4. `yeast_ppi` - Protein-protein interaction
5. `beta_lactamase` - Regression (Spearman)
6. `secondary_structure` - Residue-level classification (3 classes)
7. `human_ppi` - Large PPI dataset (35K samples)
8. `solubility` - Binary classification (62K samples)

## File Structure

```
aug/EPA/
├── configs/                         # 23 YAML configuration files
│   ├── lstm_*.yaml                 # 8 LSTM configs
│   ├── random_forest_*.yaml        # 7 RF configs
│   └── resnet_*.yaml               # 8 ResNet configs
│
├── models/                          # Model implementations
│   ├── lstm_models.py              # 4 LSTM variants
│   ├── random_forest_models.py     # RF with feature extraction
│   └── resnet_models.py            # 4 ResNet variants
│
├── trainers/                        # Training implementations
│   ├── deep_learning_trainer.py    # LSTM/ResNet trainer
│   └── traditional_ml_trainer.py   # RF trainer
│
├── config_loader.py                 # Configuration loader with validation
├── run_benchmark.py                 # Main production runner
├── generate_configs.py              # Config generator
├── test_config_system.py            # Test suite
└── CONFIGURATION_SYSTEM.md          # Full documentation
```

## Features

- Modular architecture separating models, trainers, and configs
- YAML-based configuration with validation on load
- CLI overrides for quick experimentation
- Model and dataset registries
- Online and offline augmentation strategies
- Fixed seeds for reproducibility
- Automatic JSON result saving

## Configuration Examples

### LSTM Configuration
```yaml
model:
  type: lstm
  architecture: LSTMModel
  parameters:
    embed_dim: 128
    hidden_dim: 256
    num_layers: 2
    dropout: 0.3

training:
  epochs: 30
  batch_size: 64
  learning_rate: 0.001
```

### Random Forest Configuration
```yaml
model:
  type: random_forest
  architecture: RandomForestModel
  parameters:
    n_estimators: 100
    n_jobs: -1

training:
  epochs: 1
  feature_type: aa_composition
```

### ResNet Configuration
```yaml
model:
  type: resnet
  architecture: ProteinResNet
  parameters:
    channels: [64, 128, 256, 512]
    num_blocks: [2, 2, 2, 2]

training:
  epochs: 30
  batch_size: 32
  weight_decay: 0.0001
```

## Usage Examples

### Basic Usage

```bash
# Run LSTM benchmark
python run_benchmark.py --model lstm --dataset subcellular_localization_2

# Run Random Forest benchmark
python run_benchmark.py --model random_forest --dataset solubility

# Run ResNet benchmark
python run_benchmark.py --model resnet --dataset yeast_ppi
```

### With Overrides

```bash
# Override epochs
python run_benchmark.py --model lstm --dataset human_ppi --epochs 50

# Override batch size and learning rate
python run_benchmark.py --model resnet --dataset solubility \
    --batch-size 16 --lr 0.0005

# Custom output directory
python run_benchmark.py --model lstm --dataset beta_lactamase \
    --output-dir results/beta_lactamase/
```

### Configuration Management

```bash
# List all configurations
python config_loader.py --list

# List model-specific configs
python config_loader.py --list --model lstm
python config_loader.py --list --model random_forest
python config_loader.py --list --model resnet

# View specific configuration
python config_loader.py --load lstm subcellular_localization_2
python config_loader.py --load resnet yeast_ppi
```

### Testing

```bash
python test_config_system.py
```

## SLURM Integration

### Running on Cluster

```bash
#!/bin/bash
#SBATCH --job-name=epa_benchmark
#SBATCH --partition=uds-gpu
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

source epa_venv/bin/activate

python run_benchmark.py \
    --model $MODEL \
    --dataset $DATASET \
    --output-dir results/$MODEL/
```

### Submit Multiple Jobs

```bash
# Submit all LSTM jobs
for dataset in subcellular_localization_2 yeast_ppi solubility; do
    sbatch --export=MODEL=lstm,DATASET=$dataset run_benchmark.sbatch
done

# Submit all ResNet jobs
for dataset in subcellular_localization_2 yeast_ppi solubility; do
    sbatch --export=MODEL=resnet,DATASET=$dataset run_benchmark.sbatch
done
```

## Performance Metrics

### By Model Type

| Model | Parameters | Training Speed | Inference Speed |
|-------|-----------|----------------|-----------------|
| LSTM | ~500K | Medium | Fast |
| Random Forest | N/A | Fast (CPU) | Very Fast |
| ResNet | 1-4M | Slow | Medium |

### By Dataset Size

| Dataset | Samples | LSTM Batch | ResNet Batch |
|---------|---------|------------|--------------|
| beta_lactamase | 4,158 | 64 | 32 |
| subcellular_localization_2 | 5,910 | 64 | 32 |
| subcellular_localization | 8,945 | 64 | 32 |
| secondary_structure | 8,679 | 32 | 16 |
| yeast_ppi | 11,264 | 32 | 16 |
| remote_homology_fold | 12,313 | 32 | 16 |
| human_ppi | 35,670 | 32 | 16 |
| solubility | 62,479 | 32 | 16 |

## Troubleshooting

### Configuration Errors

```bash
# Verify configuration exists
python config_loader.py --list | grep my_dataset

# Check configuration format
python config_loader.py --load lstm my_dataset
```

### CUDA Out of Memory

```bash
# Reduce batch size
python run_benchmark.py --model resnet --dataset human_ppi --batch-size 8

# Or edit config file directly
vim configs/resnet_human_ppi.yaml
```

### Import Errors

```bash
# Ensure virtual environment is activated
source epa_venv/bin/activate

# Verify dependencies
pip list | grep -E 'torch|sklearn|yaml'
```

## Documentation

- `CONFIGURATION_SYSTEM.md` - Complete configuration guide
- `model_config.py` - Model registry and capabilities
- `benchmark_config.py` - Benchmark suite definitions
- `config_loader.py` - Configuration loader implementation

## Quick Reference

```bash
# System check
python test_config_system.py

# List configs
python config_loader.py --list

# View config
python config_loader.py --load MODEL DATASET

# Run benchmark
python run_benchmark.py --model MODEL --dataset DATASET

# With overrides
python run_benchmark.py --model MODEL --dataset DATASET \
    --epochs N --batch-size N --lr FLOAT
```
