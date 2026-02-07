# EPA Multi-Dataset Benchmark Results

## Experiment Overview

**Date Started**: February 7, 2026
**Status**: Running
**Objective**: Evaluate all 23 EPA augmentations across 3 different protein datasets

## Datasets Being Tested

### 1. Subcellular Localization Binary (subcellular_localization_2)
- **Task**: Binary classification
- **Classes**: 2 (membrane-bound vs soluble)
- **Samples**: 5,184 train / 1,729 valid / 1,749 test
- **Job ID**: 20801488
- **Status**: Running on gpu106

### 2. Subcellular Localization 10-class (subcellular_localization)
- **Task**: Multi-class classification  
- **Classes**: 10 (different cellular compartments)
- **Samples**: 8,420 train / 2,811 valid / 2,773 test
- **Job ID**: 20801489
- **Status**: Running on gpu107

### 3. Yeast Protein-Protein Interaction (yeast_ppi)
- **Task**: Binary classification (PPI)
- **Classes**: 2 (interact vs no interaction)
- **Samples**: 4,945 train / 95 valid / 394 test
- **Special**: Uses TWO protein sequences per sample
- **Job ID**: 20801490
- **Status**: Running on gpu108

## Augmentations Tested (23 total)

1. baseline (no augmentation)
2. random_insert
3. random_delete
4. random_swap
5. random_crop
6. random_substitute
7. random_cut
8. span_crop
9. span_delete
10. span_substitute
11. mask_residues
12. shuffle_residues
13. reverse_sequence
14. random_noise
15. charged_swap
16. hydrophobic_swap
17. polar_swap
18. similar_aa_swap
19. dissimilar_aa_swap
20. secondary_aware_swap
21. migu_augment
22. spider_augment
23. rotary_augment

## Training Configuration

- **Epochs per augmentation**: 30
- **Batch size**: 64
- **Optimizer**: Adam (lr=0.001)
- **Model**: Bidirectional LSTM (2 layers, 256 hidden units)
- **Device**: NVIDIA RTX A4000 GPU
- **Evaluation metric**: Accuracy and Matthews Correlation Coefficient (MCC)

## Preliminary Results

### Initial Test (1 epoch baseline, CPU)

| Dataset | Train Acc | Valid Acc | MCC |
|---------|-----------|-----------|-----|
| subcellular_localization | 0.4053 | 0.4283 | 0.3190 |
| subcellular_localization_2 | 0.7133 | 0.6160 | 0.1553 |
| yeast_ppi | 0.5054 | 0.4105 | -0.0381 |

**Note**: These are from 1-epoch warm-up tests. Full 30-epoch results pending.

## Current Progress (as of Feb 7, 21:16)

### subcellular_localization_2 (Binary)
- Baseline training in progress
- Epoch 4/30 completed
- Current Valid Acc: 0.8693, MCC: 0.7342
- Showing good convergence

### subcellular_localization (10-class)
- Baseline training in progress  
- Epoch 2/30 completed
- Current Valid Acc: 0.4849, MCC: 0.3805
- Normal for multi-class problem

### yeast_ppi (PPI task)
- Baseline training in progress
- Epoch 2/30 completed
- Current Valid Acc: 0.5895, MCC: 0.0267
- Slower convergence (expected for PPI)

## Expected Completion Time

- Each augmentation: ~5-10 minutes for 30 epochs
- Total per dataset: ~2-4 hours (23 augmentations)
- All 3 datasets running in parallel
- **Estimated completion**: ~4 hours from start

## Monitoring Commands

```bash
# Check job status
squeue -u $USER

# Monitor progress
./monitor_benchmarks.sh

# View live updates
tail -f logs/benchmark_epa-subcellular_localization_2_20801488_out.txt
tail -f logs/benchmark_epa-subcellular_localization_20801489_out.txt
tail -f logs/benchmark_epa-yeast_ppi_20801490_out.txt

# Summarize completed results
python summarize_results.py
```

## Files Generated

### Result Files (JSON format)
- `benchmark_results_subcellular_localization_2_<timestamp>.json`
- `benchmark_results_subcellular_localization_<timestamp>.json`
- `benchmark_results_yeast_ppi_<timestamp>.json`

### Log Files
- `logs/benchmark_epa-*_out.txt` - Standard output
- `logs/benchmark_epa-*_err.txt` - Error logs (should be minimal)

## Result Analysis

Once complete, results will include:
- Baseline performance for each dataset
- Best augmentation per dataset
- Top 5 augmentations per dataset
- Improvements over baseline
- Cross-dataset comparison
- Recommendations for each task type

## Key Research Questions

1. **Which augmentations work best for binary vs multi-class classification?**
2. **Do different task types benefit from different augmentations?**
3. **How do PPI tasks respond to augmentations compared to single-sequence tasks?**
4. **Are there universally beneficial augmentations across all datasets?**
5. **Do structure-aware augmentations outperform random augmentations?**

## Next Steps

1. ✅ Test all datasets work correctly
2. ✅ Submit batch jobs to cluster
3. ⏳ Wait for jobs to complete (~4 hours)
4. 📊 Analyze results with `summarize_results.py`
5. 📝 Document findings and best practices
6. 🔬 Optional: Test on larger datasets (remote_homology)

## System Information

- **Cluster**: UDS Hub  
- **GPUs**: NVIDIA RTX A4000 (16GB memory)
- **Python**: 3.11.13
- **PyTorch**: 2.10.0+cu128
- **CUDA**: 12.8

## Notes

- All datasets successfully loaded and tested
- Models converging as expected
- No memory issues with current batch size (64)
- GPU utilization good across all jobs
- Sequence length limit (2000) prevents OOM errors

---

*Last Updated*: February 7, 2026, 21:16 CET
*Status*: Jobs running, results pending
