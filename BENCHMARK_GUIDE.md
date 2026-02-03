# EPA Augmentation Benchmark Guide

## Overview

This benchmark tests **each of the 23 augmentation techniques individually** to determine which ones provide the most benefit for your specific task.

## What It Does

1. **Trains a baseline model** (no augmentation) - 30 epochs
2. **Trains 23 models**, each with a different augmentation - 30 epochs each
3. **Compares all results** and ranks by performance
4. **Saves detailed JSON output** with all metrics
5. **Shows improvements** over baseline

## Running the Benchmark

### Quick Start

```bash
cd EPA
./run_benchmark.sh
```

### Manual Run

```bash
cd EPA
../venv/bin/python benchmark_all_augmentations.py
```

## Expected Runtime

- **Per augmentation**: ~10-15 minutes (30 epochs)
- **Total (24 runs)**: ~4-6 hours
- **With GPU**: ~2-3 hours
- **CPU only**: ~8-12 hours

## Configuration

Edit `benchmark_all_augmentations.py` to adjust:

```python
EPOCHS = 30  # Training epochs per augmentation
MAGNITUDE = 0.15  # Augmentation intensity (0.0-1.0)
```

## Output Files

### 1. Results JSON
`benchmark_results_final_YYYYMMDD_HHMMSS.json`

Contains:
- Configuration used
- All results sorted by performance
- Test accuracy, MCC, validation accuracy

Example structure:
```json
{
  "config": {
    "epochs": 30,
    "magnitude": 0.15,
    "seed": 42
  },
  "results": [
    {
      "augmentation": "conservative_substitute",
      "magnitude": 0.15,
      "best_valid_acc": 0.8234,
      "test_acc": 0.8156,
      "test_mcc": 0.6312
    },
    ...
  ]
}
```

### 2. Log File
`benchmark_log_YYYYMMDD_HHMMSS.txt`

Complete training output with:
- Per-epoch metrics
- Best validation accuracy
- Final test results

## Visualizing Results

After benchmark completes:

```bash
../venv/bin/python visualize_benchmark.py benchmark_results_final_*.json
```

This creates:
- Bar charts of test accuracy
- Improvement over baseline
- MCC vs Accuracy scatter plot
- Top 10 and Bottom 5 comparison

## Interpreting Results

### Metrics Explained

- **Test Accuracy**: Final model performance on held-out test set
- **Test MCC**: Matthews Correlation Coefficient (better for imbalanced data)
- **Valid Acc**: Best validation accuracy during training

### What to Look For

1. **Positive improvements**: Augmentations that beat baseline
2. **Consistent performers**: Similar valid and test accuracy
3. **High MCC**: Particularly important if dataset is imbalanced

### Example Output

```
Rank  Augmentation                    Test Acc   Test MCC   Valid Acc
-------------------------------------------------------------------
1     conservative_substitute          0.8156     0.6312     0.8234
2     nucleotide_augment              0.8142     0.6287     0.8219
3     spider_augment                  0.8128     0.6251     0.8198
...
24    random_delete                   0.7823     0.5646     0.7912
```

## Tips for Better Results

### 1. Adjust Magnitude

Different augmentations work better at different intensities:

```python
# In benchmark_all_augmentations.py
# Instead of fixed MAGNITUDE, use adaptive:
aug_magnitude = (low_mag + high_mag) / 2  # Already implemented
```

### 2. Increase Epochs

For more stable results:

```python
EPOCHS = 50  # More training
```

### 3. Multiple Runs

Average over multiple random seeds:

```python
for seed in [42, 123, 456]:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    # ... run benchmark
```

### 4. Ensemble Top Performers

After finding best augmentations, test combinations:
- Top 3 augmentations together
- Top 5 augmentations together
- Policy search over top 10

## Next Steps After Benchmark

1. **Identify top 5-10 augmentations** that improve performance
2. **Run policy search** using only these effective augmentations
3. **Create optimized config** with best performers
4. **Test on other tasks** to see if patterns hold

## Troubleshooting

### Out of Memory

Reduce batch size in config:
```yaml
train:
  batch_size: 32  # Reduce from 64
```

### Too Slow

- Use GPU if available
- Reduce epochs to 20 for quick test
- Run overnight

### Inconsistent Results

- Lock random seeds (already done)
- Increase epochs
- Use learning rate scheduling

## Example Workflow

```bash
# 1. Run benchmark (takes 4-6 hours)
cd EPA
./run_benchmark.sh

# 2. Visualize results
../venv/bin/python visualize_benchmark.py benchmark_results_final_*.json

# 3. Analyze top performers
cat benchmark_results_final_*.json | jq '.results[:5]'

# 4. Update config with best augmentations
# Edit config/LSTM/binloc_LSTM.yaml

# 5. Run policy search with top augmentations
../venv/bin/python epa/EnhancedProteinAugment.py -c config/LSTM/binloc_LSTM.yaml
```

## Questions?

- Check log files for detailed training output
- Verify dataset paths in config
- Ensure all dependencies installed
