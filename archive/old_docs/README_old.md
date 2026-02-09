# EPA: Enhanced Protein Augmentation

Automated augmentation policy search for protein prediction tasks.

## Overview

EPA (Enhanced Protein Augmentation) implements automated policy search to discover optimal data augmentation strategies for protein-related tasks. Built with a clean, modular architecture following the APA framework design.

### Key Features

- ✅ **10 Core Augmentations** (from APA)
- ✅ **Automated Policy Search** (random search baseline + policy trials)
- ✅ **Simple LSTM Integration** (from your benchmark code)
- ✅ **LMDB Dataset Support** (direct loading)
- ✅ **Clean Architecture** (augmentations, util, main script)

## Installation

### 1. Install Dependencies

```bash
cd EPA
pip install -r requirements.txt
```

### 2. Verify Dataset Paths

Update paths in `config/LSTM/binloc_LSTM.yaml`:
```yaml
dataset:
  train_path: /path/to/your/subcellular_localization_2_train.lmdb
  valid_path: /path/to/your/subcellular_localization_2_valid.lmdb  
  test_path: /path/to/your/subcellular_localization_2_test.lmdb
```

## Usage

### Quick Test

```bash
python epa/EnhancedProteinAugment.py -c config/LSTM/binloc_LSTM.yaml --seed 0
```

### Training Phases

EPA runs in 3 phases:

1. **Baseline Training** (no augmentation)
   - Trains for `baseline_epochs`
   - Saves best model checkpoint

2. **Policy Search** (if `search: true`)
   - Generates `finetune_num` random policies
   - Each policy: `num_subpolicy` sub-policies × `num_op` operations
   - Fine-tunes for `finetune_epoch` epochs per policy
   - Selects best performing policy

3. **Final Evaluation**
   - Tests on held-out test set

### Configuration

Edit `config/LSTM/binloc_LSTM.yaml`:

```yaml
epa:
  search: true              # Enable/disable policy search
  baseline_epochs: 10       # Baseline epochs
  finetune_num: 10          # Policy trials (25 in paper)
  finetune_epoch: 3         # Epochs per trial (5 in paper)
  num_subpolicy: 4          # Sub-policies
  num_op: 2                 # Ops per sub-policy
```

## Architecture

```
EPA/
├── epa/
│   ├── __init__.py
│   ├── augmentations.py          # 10 augmentation functions
│   ├── util.py                   # Config loading utilities
│   └── EnhancedProteinAugment.py # Main training script
├── config/
│   └── LSTM/
│       └── binloc_LSTM.yaml      # Example configuration
├── requirements.txt
└── README.md
```

## Augmentations

### Implemented (10)

1. `random_insert` - Insert random amino acids
2. `random_substitute` - Substitute amino acids  
3. `random_swap` - Swap positions
4. `random_delete` - Delete residues
5. `random_crop` - Crop segment
6. `random_shuffle` - Shuffle segment
7. `global_reverse` - Reverse entire sequence
8. `random_cut` - Cut and reassemble
9. `random_subsequence` - Select random subsequences
10. `back_translation_substitute` - mRNA mutation

### Magnitude Ranges

Each augmentation has a range `(low, high)`:
```python
'random_insert': (0.0, 0.5)          # Insert 0%-50%
'random_crop': (0.4, 1.0)            # Crop 40%-100%
'random_shuffle': (0.0, 0.5)         # Shuffle 0%-50%
```

## Example Output

```
================================================================================
EPA: Enhanced Protein Augmentation
================================================================================
Train: 5184, Valid: 1729, Test: 1749

================================================================================
PHASE 1: BASELINE TRAINING (No Augmentation)
================================================================================
Epoch 1/10: Train Acc=0.5234, Val Acc=0.5567
...
Baseline Best: Epoch 8, Val Acc = 0.6123

================================================================================
POLICY SEARCH: 10 trials × 3 epochs
================================================================================

--- Trial 1/10 ---
Policy: [[('random_crop', 0.72, 0.45), ('random_substitute', 0.58, 0.31)], ...]
  Epoch 2/3: Train Acc=0.5891, Val Acc=0.6089
  Final Val Acc: 0.6089

--- Trial 2/10 ---
...
  Final Val Acc: 0.6287
  ✓ New best! Acc = 0.6287
...

Search Complete! Best Score: 0.6287

================================================================================
PHASE 3: FINAL EVALUATION
================================================================================
Test Acc: 0.6195

EPA Training Complete!
```

## Comparison with APA

| Feature | APA | EPA |
|---------|-----|-----|
| Augmentations | 13 | 10 (core) |
| Architecture | TorchDrug | PyTorch native |
| Policy Search | ✓ | ✓ |
| LMDB Support | ✓ | ✓ |
| Simple LSTM | ✓ | ✓ |

## Next Steps

1. ✅ Core implementation
2. ✅ Policy search
3. ✅ Example config
4. ⏳ Add more augmentations (13 additional from your techniques)
5. ⏳ Multi-task support
6. ⏳ Advanced models (ResNet, ESM-2)

## Reference

Based on:
- **Paper**: [Enhancing Protein Predictive Models via Proteins Data Augmentation](https://arxiv.org/abs/2403.00875)
- **Authors**: Sun et al., 2024
- **Your Benchmark**: `lstm_binloc_all_augmentations_benchmark.py`
