# LSTM Solubility Job - Status Report

**Date Checked**: March 31, 2026 (~10 PM UTC)  
**Job ID**: 21691721  
**Status**: ✅ RUNNING (ACTIVE)  
**Elapsed Time**: ~30+ hours  
**Progress**: 17/24 augmentations (70.8% COMPLETE!)

---

## Current Progress

**Current Stage**: bootgen_augment (mag=0.25) - Epoch 22/30

**Augmentations Completed**: 17/24 ✅
- Baseline, random_insert (2), random_delete (2), random_swap (2)
- repeat_contraction (2), conservative_substitute
- nucleotide_augment, mask_residues, conservative_mask_residues
- imaen_simple, imaen_structure, imaen_hybrid
- +2 more

**Augmentations Remaining**: 7/24 (29.2%)

---

## Performance Metrics

**Sample Results from Log**:

| Augmentation | Val Accuracy | Test Accuracy | Status |
|---|---|---|---|
| repeat_contraction | 0.7450 | 0.6513 | ✅ Complete |
| conservative_substitute | 0.7489 | 0.7249 | ✅ Complete |
| nucleotide_augment | (in progress) | (in progress) | 🔄 Running |

**Expected Final Results**: Similar accuracy range with some augmentations showing 2-5% improvement over baseline

---

## Timeline

**Submitted**: March 30, 2026 ~14:36 UTC  
**Started Running**: March 30, 2026 ~14:37 UTC  
**Elapsed**: ~30+ hours  
**Pace**: ~1.765 hours per augmentation (17 completed ÷ 30 hours)  

**Remaining Calculation**:
- Augmentations left: 7
- Average time each: ~1 hour 46 minutes
- Estimated additional time: ~12-13 hours

**Expected Completion**: April 1, 2026 (11 AM - 1 PM UTC)  
**Time Limit**: 2 days (48 hours) - Plenty of buffer remaining

---

## Job Details

**Dataset**: Solubility (Binary Classification)
- Samples: ~62,000
- Task: Predict protein solubility
- Model: Bidirectional LSTM
- Batch Size: 32
- Epochs: 30 per augmentation
- GPU: 1x A4000 on gpu115
- CPU: 4 cores
- Memory: 48GB

---

## Impact on Benchmarks

**Current Coverage**: 9/14 (64%)

**After this job completes**: 11/14 (79%)
- ResNet Remote Homology: 1 new
- LSTM Solubility: 1 new (this job)

**Outstanding**: 3 more jobs for 100%
- ResNet: Secondary Structure, Human PPI
- LSTM: Secondary Structure, Human PPI, Yeast PPI

---

## Monitoring Commands

```bash
# Check job status
squeue -u hor20kud | grep 21691721

# Real-time output
tail -f /home/hor20kud/aug/EPA/logs/lstm_solubility_21691721_out.txt

# Check for errors
tail -f /home/hor20kud/aug/EPA/logs/lstm_solubility_21691721_err.txt
```

---

## What Happens When Complete

1. Result file saved: `results/lstm_solubility_[TIMESTAMP].json`
2. Run: `python generate_presentation_results.py`
3. Update: `presentation_results.csv`
4. Add to presentation: LSTM solubility results

---

**Status**: On track for completion tonight (March 31, 2026)

