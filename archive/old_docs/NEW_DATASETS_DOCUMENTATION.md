# New Datasets Added to EPA Benchmark

## Summary
Added 4 new diverse protein datasets to expand EPA augmentation evaluation across different task types and challenges.

**Date Added:** February 8, 2026  
**Status:** ✅ All datasets tested and benchmarks submitted

---

## Dataset Details

### 1. Beta-Lactamase (Regression)
- **Task Type:** Regression
- **Dataset Size:** 4,158 sequences
- **Metric:** Spearman Correlation
- **Target:** `scaled_effect1` - quantitative enzyme activity
- **Challenge:** Predicting continuous values of protein fitness
- **Job ID:** 20808638
- **Node:** gpu106
- **Batch File:** `run_beta_lactamase.sbatch`

### 2. Secondary Structure (Residue Classification)
- **Task Type:** Residue-level 3-class classification  
- **Dataset Size:** 8,679 sequences
- **Metric:** Per-residue accuracy, MCC
- **Classes:** 3 (H=helix, E=sheet, C=coil)
- **Target:** `ss3` - per-residue secondary structure labels
- **Features:** Variable-length sequences with valid masks
- **Challenge:** Per-position classification with masking
- **Job ID:** 20808639
- **Node:** gpu107
- **Batch File:** `run_secondary_structure.sbatch`

### 3. Human PPI (Protein-Protein Interaction)
- **Task Type:** Binary classification (dual-sequence)
- **Dataset Size:** 35,670 sequence pairs
- **Metric:** Accuracy, MCC
- **Classes:** 2 (interaction / no interaction)
- **Target:** `interaction` - binary label
- **Features:** Two protein sequences per sample
- **Challenge:** Larger PPI dataset than yeast_ppi
- **Job ID:** 20808640
- **Node:** gpu108
- **Batch File:** `run_human_ppi.sbatch`

### 4. Solubility (Binary Classification)
- **Task Type:** Binary classification
- **Dataset Size:** 62,479 sequences
- **Metric:** Accuracy, MCC
- **Classes:** 2 (soluble / insoluble)
- **Target:** `solubility` - binary label
- **Challenge:** Largest dataset, tests augmentation on scale
- **Job ID:** 20808641
- **Node:** gpu109
- **Batch File:** `run_solubility.sbatch`

---

## Code Updates

### 1. Dataset Configuration (`dataset_config.py`)
Added 4 new dataset configurations with:
- Task type specification (regression, residue_classification, classification)
- Label field names
- Class counts
- Metric types

### 2. Flexible Dataset Handler (`flexible_dataset.py`)
**New Features:**
- Regression label handling (float tensors)
- Residue-level classification with masking
- Support for per-residue label arrays
- New collate function: `collate_fn_residue()`

**Key Changes:**
- `__getitem__` now checks task_type and returns appropriate data:
  - Regression: float labels
  - Residue classification: (labels, mask) tuples
  - Standard classification: integer labels
- Added numpy import for array handling

### 3. Universal Benchmark (`universal_benchmark.py`)
**New Model Classes:**
- `RegressionModel`: LSTM with single output for regression
- `ResidueLSTMModel`: LSTM with per-residue classification outputs

**Updated Functions:**
- `train_epoch()`: Now handles regression, residue classification, and standard classification
  - Regression: MSE loss, no accuracy tracking
  - Residue: Masked loss and accuracy
  - Standard: Cross-entropy as before
  
- `evaluate()`: Updated for all task types
  - Regression: Computes Spearman correlation
  - Residue: Masked accuracy and MCC
  - Standard: Accuracy and MCC

- `train_with_augmentation()`: Auto-selects model and criterion based on task_type

**New Import:**
- `scipy.stats.spearmanr` for regression metric

---

## Testing

### Test Script: `test_new_datasets.py`
Comprehensive testing for all 4 datasets:
- ✅ Configuration loading
- ✅ Dataset loading (train split)
- ✅ Single sample access
- ✅ Batch collation
- ✅ Model initialization
- ✅ Forward pass

**Results:** All 4 datasets passed all tests

---

## Benchmark Jobs

### Submission Commands
```bash
sbatch run_beta_lactamase.sbatch      # Job 20808638
sbatch run_secondary_structure.sbatch # Job 20808639
sbatch run_human_ppi.sbatch           # Job 20808640
sbatch run_solubility.sbatch          # Job 20808641
```

### Resource Allocation
- **beta_lactamase:** 32GB RAM, 12h time limit
- **secondary_structure:** 32GB RAM, 12h time limit
- **human_ppi:** 48GB RAM, 24h time limit (larger dataset)
- **solubility:** 48GB RAM, 24h time limit (largest dataset)

### Expected Runtime
- **beta_lactamase:** ~6-8 hours
- **secondary_structure:** ~6-8 hours
- **human_ppi:** ~12-18 hours
- **solubility:** ~12-20 hours

---

## Monitoring

### All Benchmarks
```bash
./monitor_all_benchmarks.sh
```
Shows status of all 5 running benchmarks (fold + 4 new)

### Individual Job Logs
```bash
# Beta-lactamase
tail -f logs/beta_lactamase_20808638_out.txt

# Secondary structure
tail -f logs/secondary_structure_20808639_out.txt

# Human PPI
tail -f logs/human_ppi_20808640_out.txt

# Solubility
tail -f logs/solubility_20808641_out.txt
```

---

## Current Status (Feb 8, 2026 16:11)

### Active Jobs
| Job ID | Dataset | Node | Runtime | Status |
|--------|---------|------|---------|--------|
| 20807682 | remote_homology_fold | gpu104 | 2h 15m | Running (15/24 augs) |
| 20808638 | beta_lactamase | gpu106 | 4m | Running (baseline done) |
| 20808639 | secondary_structure | gpu107 | 4m | Running (baseline in progress) |
| 20808640 | human_ppi | gpu108 | 1m | Running (baseline starting) |
| 20808641 | solubility | gpu109 | 1m | Running (baseline starting) |

### Early Results

**Beta-lactamase (Regression):**
- Baseline Spearman: 0.3011 (valid), 0.3309 (test)
- Currently on: random_insert augmentation

**Secondary Structure (Residue Classification):**
- Baseline accuracy: ~72.7% (valid)
- Per-residue 3-class classification working correctly

---

## Task Type Comparison

| Task Type | Datasets | Challenge | Metric |
|-----------|----------|-----------|--------|
| **Binary Classification** | subcellular_localization_2, yeast_ppi, human_ppi, solubility | Standard 2-class | Accuracy, MCC |
| **Multi-class Classification** | subcellular_localization (10 classes), remote_homology_fold (1195 classes) | Many classes | Accuracy, MCC |
| **Regression** | beta_lactamase | Continuous values | Spearman correlation |
| **Residue Classification** | secondary_structure | Per-residue prediction | Per-residue accuracy, MCC |

---

## Files Modified/Created

### Modified
1. `dataset_config.py` - Added 4 dataset configurations
2. `flexible_dataset.py` - Added regression + residue support
3. `universal_benchmark.py` - Added new models and task handling

### Created
1. `test_new_datasets.py` - Comprehensive test suite
2. `run_beta_lactamase.sbatch` - SLURM batch script
3. `run_secondary_structure.sbatch` - SLURM batch script
4. `run_human_ppi.sbatch` - SLURM batch script
5. `run_solubility.sbatch` - SLURM batch script
6. `monitor_all_benchmarks.sh` - Multi-job monitoring
7. `NEW_DATASETS_DOCUMENTATION.md` - This file

---

## Next Steps

1. ⏳ Wait for all benchmarks to complete (~12-20 hours)
2. 📊 Analyze results across all 8 datasets
3. 📝 Update `BENCHMARK_COMPLETED_SUMMARY.md` with all results
4. 🔬 Compare augmentation effectiveness across task types
5. 📈 Create visualizations for different task types
6. 🎯 Identify best augmentations for each task category

---

## Technical Notes

### Regression Implementation
- Uses MSE loss instead of CrossEntropy
- Model outputs single value per sequence
- Evaluation uses Spearman correlation (rank-based)
- No accuracy tracking during training

### Residue-Level Implementation
- Sequences have variable lengths
- Each position has its own class label
- Valid masks handle padding/missing positions
- Loss computed only on valid positions
- Accuracy is per-residue average

### Memory Considerations
- Larger datasets (human_ppi, solubility) use batch_size=32
- Smaller datasets use batch_size=64
- Max sequence length capping prevents OOM
- Residue-level tasks have higher memory usage

---

## Dataset Sources
All datasets are standard protein benchmarks from the TAPE/ProteinGym repositories.
