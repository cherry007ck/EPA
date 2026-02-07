# Multi-Dataset Support for EPA

## Overview
The EPA benchmark system now supports multiple datasets with different structures and task types.

## Available Datasets

### 1. **Subcellular Localization Binary** (`subcellular_localization_2`)
- **Task**: Binary classification (2 classes)
- **Samples**: 5,184 train
- **Description**: Predict if protein is membrane-bound or soluble
- **Best for**: Quick testing, binary classification tasks

### 2. **Subcellular Localization 10-class** (`subcellular_localization`)
- **Task**: Multi-class classification (10 classes)
- **Samples**: 8,420 train
- **Description**: Predict subcellular location (10 compartments)
- **Best for**: Multi-class classification evaluation

### 3. **Yeast Protein-Protein Interaction** (`yeast_ppi`)
- **Task**: Binary classification (2 classes, 2 sequences)
- **Samples**: 4,945 train
- **Description**: Predict if two proteins interact
- **Special**: Uses TWO sequences per sample
- **Best for**: Testing augmentation on interaction tasks

### 4. **Remote Homology - Fold** (`remote_homology_fold`)
- **Task**: Multi-class classification (1,195 classes)
- **Samples**: Large dataset
- **Description**: Predict protein fold
- **Warning**: Requires significant compute resources

### 5. **Remote Homology - Superfamily** (`remote_homology_superfamily`)
- **Task**: Multi-class classification (2,056 classes)
- **Samples**: Large dataset
- **Description**: Predict protein superfamily

### 6. **Remote Homology - Family** (`remote_homology_family`)
- **Task**: Multi-class classification (4,254 classes)
- **Samples**: Large dataset
- **Description**: Predict protein family

## Key Components

### 1. `dataset_config.py`
- Defines configuration for each dataset
- Specifies paths, number of classes, label fields, etc.
- Easy to extend with new datasets

### 2. `flexible_dataset.py`
- Flexible LMDB dataset loader
- Automatically adapts to different dataset structures
- Supports single-sequence and multi-sequence tasks
- Handles different label fields

### 3. `universal_benchmark.py`
- Universal benchmark script
- Works with any configured dataset
- Automatically selects appropriate model architecture
- Supports both single-sequence and PPI tasks

## Usage

### List Available Datasets
```bash
python universal_benchmark.py --dataset dummy --list
```

### Run Benchmark on Specific Dataset
```bash
# On compute node (CPU/GPU)
python universal_benchmark.py --dataset subcellular_localization_2 --epochs 30 --batch_size 64
```

### Submit to Cluster
```bash
# Single dataset
sbatch run_universal_benchmark.sbatch subcellular_localization_2

# Multiple datasets
./submit_all_benchmarks.sh
```

## Changes from Original Code

### Before (benchmark_corrected.py)
- Hardcoded for subcellular_localization_2
- Fixed label field: 'localization'
- Fixed sequence field: 'primary'
- Only single-sequence tasks

### After (universal_benchmark.py)
- Works with ANY configured dataset
- Dynamic label/sequence field detection
- Supports both single and multi-sequence tasks
- Automatic model selection (LSTM vs PPI)
- Flexible collate functions

## Dataset Structure Requirements

To add a new dataset, it must be:
1. LMDB format
2. Pickled Python dictionaries
3. Have a primary sequence field
4. Have a label field (integer)

Then add configuration to `dataset_config.py`:
```python
'new_dataset': {
    'name': 'Display Name',
    'base_dir': 'datasets/new_dataset',
    'train_file': 'new_dataset_train.lmdb',
    'valid_file': 'new_dataset_valid.lmdb',
    'test_file': 'new_dataset_test.lmdb',
    'num_classes': 5,
    'task_type': 'classification',
    'label_field': 'label',
    'sequence_field': 'sequence',
    'has_single_sequence': True,
}
```

## Performance Considerations

- **Batch Size**: 64 works well for most datasets
- **Sequence Length Limit**: 2000 for single-seq, 1500 for PPI
- **GPU Memory**: ~6-8GB for standard datasets
- **Training Time**: ~2-4 hours for 23 augmentations × 30 epochs

## Testing

All datasets tested and working:
- ✅ subcellular_localization (10 classes)
- ✅ subcellular_localization_2 (2 classes)
- ✅ yeast_ppi (2 classes, PPI)
- ✅ remote_homology (multiple label types)

## Files Created

1. `dataset_config.py` - Dataset configurations
2. `flexible_dataset.py` - Flexible dataset loader
3. `universal_benchmark.py` - Universal benchmark script
4. `run_universal_benchmark.sbatch` - SLURM job script
5. `submit_all_benchmarks.sh` - Multi-dataset submission

## Next Steps

1. Run benchmarks on subcellular_localization (10-class)
2. Test on yeast_ppi (interaction task)
3. Compare augmentation effectiveness across datasets
4. Analyze which augmentations work best for which task types
