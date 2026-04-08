# EPA Benchmark System - Documentation Index

## Quick Navigation

### Getting Started
1. [PRODUCTION_README.md](PRODUCTION_README.md) - Quick start guide and overview
2. [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md) - Complete configuration guide

### Core Code Files
- `config_loader.py` - Configuration loader
- `run_benchmark.py` - Production runner
- `scripts/generate_configs.py` - Config generator
- `test_config_system.py` - Test suite

### Configuration Files
All 23 YAML configurations are in the `configs/` directory:
- `lstm_*.yaml` - 8 LSTM configurations
- `random_forest_*.yaml` - 7 Random Forest configurations
- `resnet_*.yaml` - 8 ResNet configurations

## Common Tasks

### Running Benchmarks

```bash
# Basic usage
python run_benchmark.py --model MODEL --dataset DATASET

# With overrides
python run_benchmark.py --model MODEL --dataset DATASET --epochs N --batch-size N
```

### Managing Configurations

```bash
# List all configurations
python config_loader.py --list

# View specific configuration
python config_loader.py --load MODEL DATASET

# Generate new configurations
python scripts/generate_configs.py
```

### Testing

```bash
python test_config_system.py
```

## Find What You Need

**...understand the system**
→ Read [PRODUCTION_README.md](PRODUCTION_README.md)

**...learn about configuration files**
→ Read [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md)

**...run a benchmark**
→ See [PRODUCTION_README.md](PRODUCTION_README.md)

**...create new configurations**
→ See [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md) "Adding New Configurations"

**...understand model parameters**
→ See [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md) "Model-Specific Details"

**...verify the system works**
→ Run `python test_config_system.py`

**...use with SLURM**
→ See [PRODUCTION_README.md](PRODUCTION_README.md) "SLURM Integration"

**...troubleshoot issues**
→ See [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md) "Troubleshooting"

## Quick Stats

- Configuration files: 23
- Models: 3 (LSTM, Random Forest, ResNet)
- Datasets: 8

## Learning Path

### Beginner
1. Read [PRODUCTION_README.md](PRODUCTION_README.md) for an overview
2. Run `python test_config_system.py` to verify the system
3. Try `python config_loader.py --list` to see configurations
4. Run a benchmark

### Intermediate
1. Read [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md)
2. View configuration files in `configs/`
3. Modify parameters via CLI
4. Create custom configurations

### Advanced
1. Study `config_loader.py`
2. Study `run_benchmark.py`
3. Modify `scripts/generate_configs.py` to add datasets
4. Integrate new models

## Getting Help

### Testing
```bash
python test_config_system.py           # Full test suite
python config_loader.py --list          # List configurations
python config_loader.py --load MODEL DS # View configuration
```

### Troubleshooting
See the "Troubleshooting" section in [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md).
