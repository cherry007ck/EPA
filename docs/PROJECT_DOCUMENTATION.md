# EPA Project Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & File Structure](#2-architecture--file-structure)
3. [Augmentation Techniques - Detailed Reference](#3-augmentation-techniques---detailed-reference)
4. [Training Pipeline](#4-training-pipeline)
5. [Configuration System](#5-configuration-system)
6. [Models & Datasets](#6-models--datasets)
7. [Paper Relevancy Analysis](#7-paper-relevancy-analysis)
8. [Known Issues & Fixes Applied](#8-known-issues--fixes-applied)
9. [Future Work & Roadmap](#9-future-work--roadmap)

---

## 1. Project Overview

**EPA (Enhanced Protein Augmentation)** is a benchmarking framework for evaluating protein sequence data augmentation strategies to improve predictive modeling in computational biology. The project implements techniques from:

> Sun et al. (2024) "Enhancing Protein Predictive Models via Proteins Data Augmentation: A Benchmark and New Directions" ([arXiv:2403.00875](https://arxiv.org/abs/2403.00875))

**Goal**: Enhance generalization performance by increasing training data diversity through sequence-level and semantic-level transformations.

**Requirements**: Python 3.11+, PyTorch 2.10+

**Core Capabilities**:
- 23 augmentation methods across 3 levels (token, sequence, semantic)
- Automated policy search for optimal augmentation strategy
- Multi-model benchmarking (LSTM, Random Forest, ResNet)
- 8 protein datasets covering classification, regression, PPI, and residue-level tasks

---

## 2. Architecture & File Structure

```
EPA/
├── README.md                         # Project overview and quick start
├── requirements.txt                  # Python dependencies
│
├── epa/                              # *** CORE AUGMENTATION LIBRARY ***
│   ├── __init__.py                   # Package init (version 0.1.0)
│   ├── epa_augmentations.py          # Central augmentation hub (23 methods)
│   ├── EnhancedProteinAugment.py     # Two-phase training with policy search
│   ├── util.py                       # Config loading, logging, directory utils
│   └── aug_implementations/          # 9 specialized augmentation modules
│       ├── __init__.py               # Exports all augmentation functions
│       ├── nta_augmentation.py       # Nucleotide Augmentation (333 lines)
│       ├── residue_masking.py        # MLM-style masking (238 lines)
│       ├── bootgen.py                # Bootstrap generation (432 lines)
│       ├── spider_augmentation.py    # Spider random augmentation (206 lines)
│       ├── rsa_augmentation.py       # Retrieved Sequence Augmentation (201 lines)
│       ├── preis_augmentation.py     # PreIS self-mixing (239 lines)
│       ├── nana_augmentation.py      # NaNa biophysical augmentation (329 lines)
│       ├── migu_augmentation.py      # MiGu context-aware augmentation (373 lines)
│       └── imaen.py                  # IMAEN property-aware augmentation (335 lines)
│
├── trainers/                         # Model training implementations
│   ├── deep_learning_trainer.py      # LSTM, ResNet, ESM-2 training
│   └── traditional_ml_trainer.py     # Random Forest training
│
├── models/                           # Model architecture definitions
├── configs/                          # YAML configuration files
├── datasets/                         # LMDB dataset files
├── scripts/                          # Utility scripts
│   ├── benchmark_runner.py           # Benchmark execution
│   ├── flexible_dataset.py           # LMDB dataset loader
│   └── generate_configs.py           # Config file generator
│
├── docs/                             # Documentation
│   ├── PROJECT_DOCUMENTATION.md      # This file
│   ├── CONFIGURATION_SYSTEM.md       # Config system details
│   ├── PRODUCTION_README.md          # Deployment guide
│   └── INDEX.md                      # Documentation index
│
├── results/                          # Benchmark output results
├── logs/                             # Job execution logs
├── archive/                          # Old files, benchmarks, docs
│
├── config_loader.py                  # YAML config loader with validation
├── benchmark_config.py               # Benchmark configuration classes
├── dataset_config.py                 # Dataset metadata definitions
├── model_config.py                   # Model registry
├── run_benchmark.py                  # Production benchmark runner
└── test_config_system.py             # Config system tests
```

### Module Dependency Flow

```
epa_augmentations.py  <-- Central hub, imports from aug_implementations/
       |
       v
EnhancedProteinAugment.py  <-- Uses augment_list() and apply_augment()
       |
       v
run_benchmark.py / trainers/  <-- Uses augmentation pipeline in training loop
```

---

## 3. Augmentation Techniques - Detailed Reference

### 3.1 Token-Level Augmentations (7 methods)

These operate on individual amino acid residues.

| # | Method | Function | Magnitude Range | Description |
|---|--------|----------|----------------|-------------|
| 1 | Random Insert | `random_insert(seq, m)` | 0.0 - 0.5 | Inserts random amino acids at random positions. `m` controls fraction of sequence length to insert. |
| 2 | Random Substitute | `random_substitute(seq, m)` | 0.0 - 0.5 | Replaces residues at random positions with random amino acids. `m` = fraction to substitute. |
| 3 | Random Swap | `random_swap(seq, m)` | 0.0 - 0.5 | Swaps pairs of randomly selected positions. `m` controls number of swaps. |
| 4 | Random Delete | `random_delete(seq, m)` | 0.0 - 0.5 | Removes residues with probability `m`. Guarantees at least 1 residue remains. |
| 5 | Mask Residues | `mask_residues(seq, m)` | 0.0 - 0.3 | MLM-style masking: 80% mask token 'X', 10% random AA, 10% unchanged. Based on BERT/ProtBERT. |
| 6 | Conservative Mask | `conservative_mask_residues(seq, m)` | 0.0 - 0.3 | Replaces residues with biochemically similar amino acids from the same property group. |
| 7 | Conservative Substitute | `conservative_substitute(seq, m)` | 0.0 - 0.5 | Like random_substitute but restricted to biochemically similar amino acids (e.g., K->R, D->E). |

### 3.2 Sequence-Level Augmentations (8 methods)

These operate on sequence structure and arrangement.

| # | Method | Function | Magnitude Range | Description |
|---|--------|----------|----------------|-------------|
| 8 | Random Crop | `random_crop(seq, m)` | 0.4 - 1.0 | Extracts a contiguous subsequence of length `m * len(seq)`. |
| 9 | Random Shuffle | `random_shuffle(seq, m)` | 0.0 - 0.5 | Shuffles a local segment of length `m * len(seq)`. |
| 10 | Global Reverse | `global_reverse(seq, m)` | 0.0 - 0.0 | Reverses entire sequence. `m` is unused (binary operation). |
| 11 | Random Cut | `random_cut(seq, m)` | 0.2 - 1.0 | Cuts sequence at random points, shuffles segments, reassembles. |
| 12 | Random Subsequence | `random_subsequence(seq, m)` | 0.2 - 1.0 | Cuts and randomly selects a subset of segments. |
| 13 | Repeat Expansion | `repeat_expansion(seq, m)` | 0.0 - 1.0 | Finds tandem repeats and duplicates them with probability `m`. |
| 14 | Repeat Contraction | `repeat_contraction(seq, m)` | 0.0 - 1.0 | Finds tandem repeats and removes one copy with probability `m`. |
| 15 | Back-Translation | `back_translation_substitute(seq, m)` | 0.0 - 0.5 | Translates to mRNA codons, mutates nucleotides, translates back. Avoids stop codons. |

### 3.3 Semantic-Level Augmentations (8 methods)

These use domain knowledge from published papers.

#### 3.3.1 Nucleotide Augmentation (NTA)
- **File**: `nta_augmentation.py`
- **Function**: `nucleotide_augment(seq, substitution_rate)`
- **Paper**: Minot & Reddy (2022) "Nucleotide augmentation for machine learning-guided protein engineering"
- **How it works**: Back-translates amino acids to DNA codons, applies synonymous codon substitutions (same amino acid, different codon), then forward-translates back. Creates diversity at the nucleotide level while preserving amino acid identity.
- **Best for**: Models that operate on nucleotide-level representations or when preserving exact protein function is critical.
- **Magnitude**: 0.0 - 0.5 (fraction of codons to substitute)

#### 3.3.2 BootGen
- **File**: `bootgen.py`
- **Function**: `bootgen_augment(seq, intensity)`
- **Paper**: NeurIPS 2023 "Bootstrapped Training of Score-Conditioned Generator for Offline Design of Biological Sequences"
- **How it works**: Generates multiple candidate sequences through conservative substitutions, scores each candidate using a proxy function (composition similarity + property similarity + length preservation), then selects the best via rank-based probabilistic sampling.
- **Key components**: `compute_composition_similarity()`, `compute_property_similarity()`, `rank_based_selection()`
- **Magnitude**: 0.0 - 0.5 (controls substitution count and candidate pool size)

#### 3.3.3 Spider Augmentation
- **File**: `spider_augmentation.py`
- **Function**: `spider_augment(seq, intensity)`
- **Paper**: "A Deep Learning Approach with Data Augmentation to Predict Novel Spider Neurotoxic Peptides"
- **How it works**: Combines random amino acid substitution (50% of intensity) with random insertion (50% of intensity). Originally includes BLAST-based filtering for biological plausibility (not implemented here for speed).
- **Note**: This augmentation can change sequence length due to insertions.
- **Magnitude**: 0.0 - 0.5

#### 3.3.4 RSA (Retrieved Sequence Augmentation)
- **File**: `rsa_augmentation.py`
- **Functions**: `rsa_augment(seq, intensity)`, `rsa_augment_with_original(seq, intensity)`
- **Paper**: Chang et al. (2023) "Retrieved Sequence Augmentation for Protein Representation Learning"
- **How it works**: Simplified version that generates "pseudo-homologous" sequences through conservative mutations (biochemically similar substitutions). The full RSA uses FAISS indexing to retrieve similar sequences from Pfam/UniRef databases.
- **Variant**: `rsa_augment_with_original` has 50% chance of returning the original (simulating retrieval of an identical match).
- **Magnitude**: 0.0 - 0.5

#### 3.3.5 PreIS (Supervised Data Augmentation)
- **File**: `preis_augmentation.py`
- **Function**: `preis_augment(seq, intensity)`
- **Paper**: "PreIS: A Novel Data Augmentation Approach Using Protein Language Models for Influenza A Subtype Prediction"
- **How it works**: Self-mixing augmentation with two operations:
  1. **Global segment swapping** (`gamma_g=0.4*intensity`): Swaps two non-overlapping segments
  2. **Local token shuffling** (`gamma_l=0.1*intensity`): Shuffles amino acids at random positions
- **Key property**: Preserves sequence length and amino acid composition (multiset).
- **Note**: The original PreIS does cross-sequence mixing with label awareness. This simplified version performs self-mixing within a single sequence.
- **Magnitude**: 0.0 - 0.5

#### 3.3.6 NaNa (Novel Augmentation of New Node Attributes)
- **File**: `nana_augmentation.py`
- **Function**: `nana_augment(seq, substitution_rate, similarity_threshold=0.65, use_groups=True)`
- **Paper**: "NaNa and MiGu: Semantic Data Augmentation Techniques to Enhance Protein Classification in Graph Neural Networks"
- **How it works**: Substitutes amino acids with biophysically and structurally similar alternatives using multi-dimensional similarity scoring:
  - Kyte-Doolittle hydrophobicity (15% weight)
  - Charge at pH 7.4 (25% weight)
  - Van der Waals volume (10% weight)
  - Chou-Fasman secondary structure propensities: alpha-helix (20%), beta-sheet (20%), turn (10%)
- **Two modes**: Fast lookup via pre-defined biophysical groups, or full similarity calculation with weighted scoring.
- **Magnitude**: 0.0 - 0.5

#### 3.3.7 MiGu (Molecular Interactions and Geometric Upgrading)
- **File**: `migu_augmentation.py`
- **Function**: `migu_augment(seq, substitution_rate, context_window=3, preserve_interactions=True)`
- **Paper**: Same as NaNa (NaNa/MiGu paper)
- **How it works**: Extends NaNa with molecular interaction awareness:
  1. **Context analysis**: Examines local k-mer context (hydrophobic, charged, polar, aromatic neighbors)
  2. **Context-aware substitution**: Selects replacements based on dominant local context
  3. **Interaction preservation**: Enforces three rules:
     - Preserve cysteine pairs (potential disulfide bonds)
     - Maintain charge complementarity in salt bridges (K/R/H near D/E)
     - Keep aromatic clusters intact (pi-stacking)
- **Magnitude**: 0.0 - 0.5

#### 3.3.8 IMAEN (Interpretable Molecular Augmentation)
- **File**: `imaen.py`
- **Functions**: `imaen_simple(seq, intensity)`, `imaen_augment(seq, intensity, property_bias, conservative, noise_level)`
- **Paper**: "IMAEN: An interpretable molecular augmentation model for drug-target interaction prediction"
- **How it works**: Three-step process:
  1. **Property-aware position selection**: Biased selection of positions based on amino acid properties (hydrophobic, polar, charged, aromatic, or random)
  2. **Conservative substitution**: Replaces with biochemically similar amino acids using BLOSUM-inspired groups
  3. **Controlled noise**: Adds small amount of interpretable noise (10% of intensity)
- **Note**: The original IMAEN paper focuses on drug-target interaction (architectural augmentation), not data augmentation. This adaptation extracts the property-aware concept for sequence augmentation.
- **Magnitude**: 0.0 - 0.5

### 3.4 Augmentation Interface

All augmentations follow a unified interface:

```python
def augment_function(sequence: List[str], magnitude: float) -> List[str]:
    """
    Args:
        sequence: List of single-letter amino acid codes (e.g., ['M', 'E', 'T'])
        magnitude: Intensity parameter (0.0 to 1.0)
    Returns:
        Augmented sequence (same format)
    """
```

### 3.5 Policy System

The EPA policy system allows combining multiple augmentations:

```python
# A policy is a list of sub-policies
# Each sub-policy is a list of (augmentation_name, probability, level)
policy = [
    [('random_crop', 0.72, 0.45), ('random_substitute', 0.58, 0.31)],
    [('nana_augment', 0.85, 0.40), ('random_swap', 0.60, 0.25)],
]

# Apply: randomly picks one sub-policy, applies each op with its probability
augmented_seq = apply_augment(sequence, policy)
```

---

## 4. Training Pipeline

### Two-Phase Training (EnhancedProteinAugment.py)

**Phase 1: Baseline Training**
- Trains an LSTM model without augmentation
- Saves best checkpoint based on validation accuracy
- Tracks accuracy and MCC metrics

**Phase 2: Policy Search** (if `search: true`)
- Generates random augmentation policies
- Each policy has `num_subpolicy` sub-policies, each with `num_op` operations
- Fine-tunes the baseline model with each policy
- Selects the policy with highest validation accuracy
- Saves the best policy as JSON

**Phase 3: Final Evaluation**
- Evaluates on the held-out test set

### Model Architecture

```python
class LSTMModel(nn.Module):
    # Bidirectional LSTM with embedding layer
    # embed_dim -> LSTM(hidden_dim, bidirectional=True) -> Linear(hidden*2, 64) -> ReLU -> Dropout(0.3) -> Linear(64, num_classes)
```

### Data Pipeline

- **LMDB** datasets with `pickle`-serialized records
- Each record: `{'primary': amino_acid_sequence, 'localization': label}`
- Online augmentation: applied per-sample in `__getitem__` with configurable probability (default 0.7)
- Vocabulary: 20 standard amino acids + padding token (index 0)

---

## 5. Configuration System

### YAML Config Structure

```yaml
model:
  class: LSTMModel
  embed_dim: 64
  hidden_dim: 128
  num_classes: 2

dataset:
  class: subcellular_localization_2
  train_path: /path/to/train.lmdb
  valid_path: /path/to/valid.lmdb
  test_path: /path/to/test.lmdb

train:
  batch_size: 64

optimizer:
  lr: 0.001

epa:
  search: true
  baseline_epochs: 10
  finetune_num: 10
  finetune_epoch: 3
  num_subpolicy: 4
  num_op: 2

device:
  gpus: [0]

output_dir: results
```

### Config Loader

`config_loader.py` provides:
- YAML loading with validation
- Hierarchical fallback resolution
- Cached loading (3x performance boost)
- Dataset-specific and model-specific metadata

---

## 6. Models & Datasets

### Supported Models

| Model | Parameters | Augmentation | Status | Task Support |
|-------|-----------|--------------|--------|--------------|
| LSTM | ~500K | Online | Working | Classification, Regression |
| Random Forest | N/A | Offline | Working | Classification, Regression |
| ResNet | 1-4M | Online | Experimental | All |
| ESM-2 | 8M-650M | Online | Planned | All |

### Supported Datasets

| Dataset | Task | Classes | Samples | Metric |
|---------|------|---------|---------|--------|
| subcellular_localization_2 | Classification | 2 | 5,910 | Accuracy |
| subcellular_localization | Classification | 10 | 8,945 | Accuracy |
| remote_homology_fold | Classification | 1,195 | 12,313 | Accuracy |
| yeast_ppi | PPI | 2 | 11,264 | Accuracy |
| human_ppi | PPI | 2 | 35,670 | Accuracy |
| solubility | Classification | 2 | 62,479 | Accuracy |
| beta_lactamase | Regression | 1 | 4,158 | Spearman |
| secondary_structure | Residue-level | 3 | 8,679 | Accuracy |

---

## 7. Paper Relevancy Analysis

The following papers were evaluated for relevancy to this project. They were provided as additional resources for potential integration.

### 7.1 NTA - Nucleotide Augmentation (HIGH Relevancy)
- **Paper**: Minot & Reddy (2022) "Nucleotide Augmentation For Machine Learning-Guided Protein Engineering"
- **Repository**: [github.com/minotm/NTA](https://github.com/minotm/NTA)
- **Status**: Already integrated as `nucleotide_augment()` in `nta_augmentation.py`
- **What it does**: Exploits codon degeneracy (multiple DNA codons encode the same amino acid) to create augmented representations. Back-translates protein sequences to nucleotide sequences using different codon choices, generating multiple distinct representations encoding the same protein.
- **Why relevant**: Pure protein data augmentation technique with clear benchmarking on multiple protein engineering datasets (GB1, AAV, Trastuzumab). Clean separation between augmentation logic and model training.
- **Integration notes**: Framework-agnostic augmentation functions (pure Python/NumPy). Trivially integratable into any pipeline.

### 7.2 NaNa and MiGu (HIGH Relevancy)
- **Paper**: "NaNa and MiGu: Semantic Data Augmentation Techniques to Enhance Protein Classification in Graph Neural Networks"
- **Repository**: [github.com/r08b46009/Code_for_MIGU_NANA](https://github.com/r08b46009/Code_for_MIGU_NANA)
- **Status**: Already integrated as `nana_augment()` and `migu_augment()` in `nana_augmentation.py` and `migu_augmentation.py`
- **What it does**: NaNa enriches protein graph representations with biophysical features (atom coordinates, hydrogen bonds). MiGu extends this with edge attributes for molecular interaction modeling.
- **Why relevant**: Directly about protein data augmentation for improving protein classification. Targets the same domain and evaluates on standard protein benchmarks (EC, SCOPe). Built on PyTorch Geometric.
- **Integration notes**: The original operates on 3D protein structure graphs. Our implementation adapts the biophysical property-aware substitution concept to sequence-based augmentation, preserving the core semantic principles.

### 7.3 BootGen (MEDIUM Relevancy)
- **Paper**: NeurIPS 2023 "Bootstrapped Training of Score-Conditioned Generator for Offline Design of Biological Sequences"
- **Repository**: [github.com/kaist-silab/bootgen](https://github.com/kaist-silab/bootgen)
- **Status**: Already integrated as `bootgen_augment()` in `bootgen.py`
- **What it does**: Uses bootstrapped training of a score-conditioned LSTM generator to produce high-fitness biological sequences (GFP proteins, UTRs, RNA). The generator is iteratively improved by generating candidates, scoring them, and adding the best to the training set.
- **Why relevant**: While BootGen's primary goal is sequence *design/optimization* (not augmentation), the bootstrapping mechanism (expanding training data with synthetic samples) is conceptually related. The proxy scoring and rank-based selection are useful augmentation quality controls.
- **Limitations**: The framing and evaluation are different from augmentation benchmarking. Requires adaptation from the design-bench framework.

### 7.4 NT_estimation / Spider Augmentation (MEDIUM Relevancy)
- **Paper**: "A Deep Learning Approach with Data Augmentation to Predict Novel Spider Neurotoxic Peptides"
- **Repository**: [github.com/bzlee-bio/NT_estimation](https://github.com/bzlee-bio/NT_estimation)
- **Status**: Already integrated as `spider_augment()` in `spider_augmentation.py`
- **What it does**: Provides a data augmentation tool for peptide data. Generates random mutant sequences using biochemical group-based substitution, random insertions, and BLAST-based validation for biological plausibility.
- **Why relevant**: Legitimate protein/peptide augmentation strategy. The mutation + BLAST filtering concept is a useful paradigm for biologically-grounded augmentation.
- **Limitations**: Narrow scope (spider neurotoxic peptides). Depends on external NCBI BLAST tool. The codebase is not built on modern ML frameworks. Our implementation simplifies away the BLAST dependency.

### 7.5 IMAEN (LOW Relevancy)
- **Paper**: "IMAEN: An interpretable molecular augmentation model for drug-target interaction prediction"
- **Repository**: [github.com/zhangjing-dmu/IMAEN](https://github.com/zhangjing-dmu/IMAEN)
- **Status**: Adapted concept as `imaen_simple()` in `imaen.py`
- **What it does**: Despite having "augmentation" in its name, IMAEN is about a GNN *model architecture* for drug-target interaction prediction. The "molecular augmentation" refers to an internal neighborhood aggregation mechanism within the GNN, not data augmentation.
- **Why relevant**: Low relevancy to data augmentation benchmarking. The domain (drug-target interaction) is adjacent but different from protein predictive modeling. However, the property-aware concept inspired our interpretable augmentation implementation.
- **Limitations**: The "augmentation" is architectural, not a data augmentation strategy. There is little to extract for an augmentation benchmarking framework.

### Summary Table

| Paper | Augmentation Type | Relevancy | Integrated? | PyTorch Compatible |
|-------|------------------|-----------|------------|-------------------|
| NTA | Codon degeneracy-based | **HIGH** | Yes | Yes (framework-agnostic) |
| NaNa/MiGu | Graph semantic / biophysical | **HIGH** | Yes (adapted) | Yes (PyTorch Geometric) |
| BootGen | Generative bootstrapping | MEDIUM | Yes (simplified) | Yes (native PyTorch) |
| Spider/NT_estimation | Random mutation + BLAST | MEDIUM | Yes (without BLAST) | Partially (BLAST dependency) |
| IMAEN | Architectural (not data aug) | LOW | Concept adapted | N/A |

---

## 8. Known Issues & Fixes Applied

### 8.1 Critical Issues Fixed

#### Import Path Hardcoding (FIXED)
- **File**: `epa/epa_augmentations.py`
- **Issue**: Line 6 had `sys.path.insert(0, '/home/EPA/epa')` - a hardcoded absolute path that would fail on any other machine.
- **Fix**: Replaced with dynamic path resolution using `os.path.dirname(os.path.abspath(__file__))`.

#### Broken Metrics Import (FIXED)
- **File**: `epa/EnhancedProteinAugment.py`
- **Issue**: Imported `from metrics import accuracy, mcc` which required an external `metrics` module that may not exist.
- **Fix**: Replaced with inline implementations using `sklearn.metrics.matthews_corrcoef` and `accuracy_score`.

#### Hardcoded Dataset Path (FIXED)
- **File**: `epa/EnhancedProteinAugment.py`
- **Issue**: `DATASET_BASE = "/home/hor20kud/aug/EPA/datasets/"` - hardcoded to a specific user's home directory.
- **Fix**: Replaced with relative path derived from `__file__` location.

#### Corrupted README (FIXED)
- **File**: `README.md`
- **Issue**: Two separate README files had been merged line-by-line, making the document unreadable.
- **Fix**: Rewrote README.md with clean, organized content.

### 8.2 Documentation Cleanup

- **Moved to `archive/old_docs/`**: 10 scattered presentation, tracking, and redundant documentation files that cluttered the project root.
- **Kept in root**: Only `README.md` (clean, authoritative).
- **Kept in `docs/`**: `PROJECT_DOCUMENTATION.md` (this file), `CONFIGURATION_SYSTEM.md`, `PRODUCTION_README.md`, `INDEX.md`.

### 8.3 Code Quality Fixes

- **Docstring formatting**: Fixed missing space in `aug_implementations/__init__.py` (`-MiGu` -> `- MiGu`).
- **Invalid amino acid in examples**: All docstring examples referenced `'O'` (pyrrolysine, not in the standard 20). Replaced with valid amino acids across 6 files.

### 8.4 Remaining Known Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| No `setup.py`/`pyproject.toml` | Medium | Project lacks proper Python packaging. Install requires manual path setup. |
| ResNet trainer import errors | Medium | ResNet training fails due to missing module imports in some environments. |
| ESM-2 trainer incomplete | Low | ESM-2 model support is planned but not yet implemented. |
| No unit tests for augmentations | Low | Augmentation functions lack automated test coverage. Tests exist in `archive/test_files/` but are not integrated into CI. |
| NTA produces identical output | Info | `nucleotide_augment` does synonymous substitution - output amino acid sequence is identical to input. This is by design (augments at nucleotide representation level), but has no effect for amino-acid-level models. |

---

## 9. Future Work & Roadmap

### Short Term
- [ ] Add `setup.py` or `pyproject.toml` for proper Python packaging
- [ ] Fix ResNet trainer import issues
- [ ] Add unit tests for all 23 augmentation methods
- [ ] Run complete benchmarks across all model-dataset-augmentation combinations

### Medium Term
- [ ] Implement ESM-2 model support
- [ ] Add cross-sequence mixing for PreIS (requires dataset-aware augmentation interface)
- [ ] Implement BLAST-based filtering for Spider augmentation (optional)
- [ ] Add full RSA with FAISS-based sequence retrieval from UniRef/Pfam
- [ ] Multi-GPU training support

### Long Term
- [ ] Hyperparameter tuning framework (beyond random policy search)
- [ ] Integration with protein structure prediction models
- [ ] Support for multi-task learning across datasets
- [ ] Web-based dashboard for benchmark visualization

---

*Document generated: 2026-04-04*
*Project: EPA (Enhanced Protein Augmentation) v0.1.0*
