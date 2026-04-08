# EPA: Enhanced Protein Augmentation

> Automated augmentation policy search and benchmarking for protein prediction tasks.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.10+](https://img.shields.io/badge/pytorch-2.10+-red.svg)](https://pytorch.org/)

---

## Overview

EPA (Enhanced Protein Augmentation) implements automated policy search to discover optimal data augmentation strategies for protein-related tasks. Built with a modular architecture following the APA framework design from:

> Sun et al. (2024) "Enhancing Protein Predictive Models via Proteins Data Augmentation: A Benchmark and New Directions"

### Key Features

- **23 Augmentation Methods** across token, sequence, and semantic levels
- **Automated Policy Search** with random search baseline + policy trials
- **Multi-Model Support**: LSTM, Random Forest, ResNet (ESM-2 planned)
- **8 Datasets**: Classification, regression, PPI, residue-level tasks
- **LMDB Dataset Support** with direct loading
- **YAML Configuration** for all parameters

---

## Installation

```bash
cd EPA
python -m venv epa_venv
source epa_venv/bin/activate
pip install -r requirements.txt
```

### Verify Dataset Paths

Update paths in your config YAML (e.g., `config/LSTM/binloc_LSTM.yaml`):

```yaml
dataset:
  train_path: /path/to/your/subcellular_localization_2_train.lmdb
  valid_path: /path/to/your/subcellular_localization_2_valid.lmdb
  test_path: /path/to/your/subcellular_localization_2_test.lmdb
```

---

## Usage

### Quick Test

```bash
python epa/EnhancedProteinAugment.py -c config/LSTM/binloc_LSTM.yaml --seed 0
```

### Run Benchmark

```bash
python run_benchmark.py --model lstm --dataset subcellular_localization_2
```

### Configuration Management

```bash
python config_loader.py --list
python config_loader.py --load lstm subcellular_localization_2
```

---

## Training Phases

EPA runs in 3 phases:

1. **Baseline Training** (no augmentation) - trains for `baseline_epochs`, saves best checkpoint
2. **Policy Search** (if `search: true`) - generates `finetune_num` random policies, fine-tunes each, selects best
3. **Final Evaluation** - tests on held-out test set

### Configuration

```yaml
epa:
  search: true
  baseline_epochs: 10
  finetune_num: 10
  finetune_epoch: 3
  num_subpolicy: 4
  num_op: 2
```

---

## Project Structure

```
EPA/
├── epa/                              # Core augmentation library
│   ├── __init__.py
│   ├── epa_augmentations.py          # 23 augmentation functions (central hub)
│   ├── EnhancedProteinAugment.py     # Two-phase training with policy search
│   ├── util.py                       # Config loading, logging utilities
│   └── aug_implementations/          # 9 specialized augmentation modules
│       ├── nta_augmentation.py       # Nucleotide Augmentation (codon back-translation)
│       ├── residue_masking.py        # MLM-style and conservative masking
│       ├── bootgen.py                # Bootstrap generation with rank-based selection
│       ├── spider_augmentation.py    # Random substitution + insertion
│       ├── rsa_augmentation.py       # Retrieved Sequence Augmentation
│       ├── preis_augmentation.py     # Self-mixing via segment swapping
│       ├── nana_augmentation.py      # Biophysical property-aware substitution
│       ├── migu_augmentation.py      # Context-aware with interaction preservation
│       └── imaen.py                  # Interpretable property-aware augmentation
├── trainers/                         # Model training implementations
├── models/                           # Model architectures
├── configs/                          # YAML configuration files
├── datasets/                         # LMDB datasets
├── scripts/                          # Utility scripts
├── docs/                             # Additional documentation
├── results/                          # Benchmark results
├── archive/                          # Old files and benchmarks
└── requirements.txt
```

---

## Augmentations (23 Total)

### Token-Level (7)
| Method | Description |
|--------|-------------|
| `random_insert` | Insert random amino acids |
| `random_substitute` | Replace with random amino acids |
| `random_delete` | Remove amino acids |
| `random_swap` | Exchange positions |
| `mask_residues` | MLM-style masking (80% mask, 10% random, 10% keep) |
| `conservative_mask_residues` | Semantic masking within biochemical groups |
| `conservative_substitute` | Replace with biochemically similar amino acids |

### Sequence-Level (7)
| Method | Description |
|--------|-------------|
| `random_crop` | Subsequence selection |
| `random_shuffle` | Local segment shuffling |
| `global_reverse` | Reverse entire sequence |
| `random_cut` | Segment cutting & reassembly |
| `random_subsequence` | Non-contiguous selection |
| `repeat_expansion` | Pattern duplication |
| `repeat_contraction` | Pattern removal |

### Semantic-Level (9)
| Method | Source Paper | Description |
|--------|-------------|-------------|
| `nucleotide_augment` | Minot & Reddy 2022 | Synonymous codon substitution via NTA |
| `bootgen_augment` | NeurIPS 2023 | Bootstrap generation with quality ranking |
| `rsa_augment` | Chang et al. 2023 | Conservative homolog simulation |
| `preis_augment` | PreIS/SDA | Self-mixing via segment swapping |
| `nana_augment` | NaNa/MiGu paper | Biophysical property-aware substitution |
| `migu_augment` | NaNa/MiGu paper | Context-aware with interaction preservation |
| `imaen_simple` | IMAEN | Interpretable property-based augmentation |
| `spider_augment` | Spider NT paper | Random substitution + insertion |
| `back_translation_substitute` | mRNA-level mutation via codon back-translation |

---

## Models

| Model | Status | Augmentation | GPU |
|-------|--------|--------------|-----|
| LSTM | Working | Online | Yes |
| Random Forest | Working | Offline | No |
| ResNet | Experimental | Online | Yes |
| ESM-2 | Planned | Online | Yes |

---

## Results

### LSTM Results

| Dataset | Accuracy | MCC |
|---------|----------|-----|
| subcellular_localization_2 | 89.31% | 0.79 |
| subcellular_localization | 69.13% | 0.65 |
| yeast_ppi | 60.15% | 0.20 |

### Random Forest Results

| Dataset | Performance |
|---------|-------------|
| solubility | 77.0% accuracy |
| beta_lactamase | 0.40 Spearman |

---

## SLURM Cluster Integration

```bash
sbatch --export=MODEL=lstm,DATASET=subcellular_localization_2 \
    scripts/slurm/run_benchmark.sbatch
```

---

## Reference

Based on:
- **Paper**: Sun et al. (2024) [Enhancing Protein Predictive Models via Proteins Data Augmentation](https://arxiv.org/abs/2403.00875)
- **Framework**: APA (Automated Protein Augmentation)

---

## License

This project is licensed under the MIT License.
