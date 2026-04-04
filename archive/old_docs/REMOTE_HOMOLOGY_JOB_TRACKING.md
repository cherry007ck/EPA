# ResNet Remote Homology/Fold Job - Tracking

**Date Submitted**: March 31, 2026  
**Job ID**: 21699496  
**Status**: RUNNING (R)  
**Elapsed Time**: ~7 minutes 26 seconds  
**Expected Duration**: 12-20 hours  
**Expected Completion**: April 1-2, 2026  

---

## Job Details

**Script**: `scripts/slurm/resnet_remote_homology_fold.sbatch`

**Configuration**:
- Model: ResNet
- Dataset: remote_homology_fold
- Samples: ~12,000
- Classes: 1,195 (fold classification - large output layer)
- Batch Size: 32
- Epochs: 30
- GPU: 1x GPU
- CPU: 4 cores
- Memory: 48GB
- Time Limit: 24 hours

**Partition**: uds-hub  
**Nodes**: gpu101-105, gpu113-114, gpu117-118

---

## Expected Output

**Result File**: 
- `results/resnet_remote_homology_fold_[TIMESTAMP].json`

**Log Files**:
- stdout: `logs/resnet_remote_homology_fold_21699496_out.txt`
- stderr: `logs/resnet_remote_homology_fold_21699496_err.txt`

---

## Current Progress

**Baseline**: ✅ COMPLETE
- Validation Accuracy: 0.1250 (12.5%)
- Test Accuracy: 0.1142 (11.42%)
- 30/30 epochs completed

**Currently Running**: 
- Augmentation: random_insert (mag=0.25)
- Status: In progress (early epochs)

**Augmentations Remaining**: 23 (out of 24 total)

---

## Monitoring

**Check queue status**:
```bash
squeue -u hor20kud | grep resnet
```

**Check job details**:
```bash
scontrol show job 21699496
```

**Monitor logs**:
```bash
tail -f logs/resnet_remote_homology_fold_21699496_out.txt
tail -f logs/resnet_remote_homology_fold_21699496_err.txt
```

---

## What's Happening

This job will:
1. Load the remote_homology_fold dataset (~12K samples)
2. Train ResNet with 24 augmentation methods
3. Evaluate on test set
4. Generate comparison metrics
5. Save results to JSON

Because this is fold classification with 1,195 classes, the output layer is large and training is expensive. Estimated time: 12-20 hours.

---

## Impact on Presentation

**Current Status**: 10/14 benchmarks complete (71%)

**Missing Benchmarks**:
- ✗ Remote Homology Fold (ResNet) - **RUNNING NOW**
- ✗ Secondary Structure (ResNet)
- ✗ Human PPI (ResNet)
- ✗ Secondary Structure (LSTM)
- ✗ Human PPI (LSTM)
- ✗ Solubility (LSTM)
- ✗ Yeast PPI (LSTM)

**After this job completes**:
- Coverage: 10/14 (71%)
- New slide content: Fold classification results
- Paper comparison: Can complete Fold task comparison

---

## Next Steps

1. Monitor job completion
2. Once complete, verify results in `results/` folder
3. Update `generate_presentation_results.py` if needed
4. Run it to regenerate presentation_results.csv
5. Update presentation with new results

---

**Job submitted**: 2026-03-31 14:35 UTC  
**Expected completion**: 2026-04-01 to 2026-04-02 (12-20 hours from submission)

