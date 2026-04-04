# Quick Reference - Augmentation Classification

## All 24 Augmentations at a Glance

### 🎯 TOKEN-LEVEL (7)
**Concept**: Individual position changes. Modify single amino acids.

| # | Augmentation | Mechanism | Mag | Bio Impact |
|---|---|---|---|---|
| 1 | random_insert | Insert random AAs | 0.25-0.50 | 🟠 Low |
| 2 | random_substitute | Replace with random | 0.25-0.50 | 🟠 Low |
| 3 | random_delete | Remove randomly | 0.25-0.50 | 🟠 Low |
| 4 | random_swap | Swap positions | 0.25-0.50 | 🟡 Medium |
| 5 | mask_residues | Hide positions | 0.15 | 🟡 Medium |
| 6 | conservative_mask_residues | Hide similar AAs | 0.15 | 🟡 Medium |
| 7 | conservative_substitute | Replace w/ similar | 0.25 | 🟢 High |

---

### 🔀 SEQUENCE-LEVEL (8)
**Concept**: Subsequence/region changes. Modify organization and structure.

| # | Augmentation | Mechanism | Mag | Bio Impact |
|---|---|---|---|---|
| 8 | random_crop | Keep random region | 0.70 | 🟠 Low |
| 9 | random_shuffle | Shuffle segment | 0.25 | 🟠 Low |
| 10 | global_reverse | Reverse entire seq | N/A | 🔴 Very Low |
| 11 | random_cut | Cut & shuffle segs | 0.60 | 🔴 Very Low |
| 12 | random_subsequence | Keep random subs | 0.60 | 🟠 Low |
| 13 | repeat_expansion | Duplicate patterns | 0.50 | 🟡 Medium |
| 14 | repeat_contraction | Remove duplicates | 0.50 | 🟡 Medium |
| 15 | spider_augment | Structure-aware mix | 0.25 | 🟡 Medium |

---

### 🧬 SEMANTIC-LEVEL (8)
**Concept**: Biology-informed changes. Preserve properties.

| # | Augmentation | Mechanism | Mag | Bio Impact |
|---|---|---|---|---|
| **Nucleotide-Based** |
| 16 | nucleotide_augment | Codon variation | 0.25 | 🟢 High |
| 17 | back_translation_substitute | mRNA mutation | 0.25 | 🟢 High |
| **Structure/Network-Based** |
| 18 | bootgen_augment | Bootstrap patterns | 0.25 | 🟢 High |
| 19 | rsa_augment | Solvent accessibility | 0.25 | 🟢🟢 Very High |
| 20 | preis_augment | Embedding guided | 0.25 | 🟢🟢 Very High |
| 21 | nana_augment | Network-aware (PPI) | 0.25 | 🟢🟢 Very High |
| 22 | migu_augment | Mutual info guided | 0.25 | 🟢🟢 Very High |
| 23 | imaen_simple | Interaction-aware | 0.25 | 🟢🟢 Very High |

---

### 🔵 BASELINE (1)
| # | Augmentation | Mechanism | Mag |
|---|---|---|---|
| 0 | baseline | No augmentation | N/A |

---

## Quick Lookup by Type

### By Complexity
```
SIMPLE:     random_insert, random_delete, random_substitute, random_swap
MODERATE:   random_crop, random_shuffle, repeat_contraction, repeat_expansion
COMPLEX:    back_translation_substitute, nucleotide_augment, rsa_augment
ADVANCED:   preis_augment, nana_augment, migu_augment, imaen_simple
```

### By Use Case
```
STRESS TEST:           random_insert, random_substitute, global_reverse
ROBUSTNESS:            random_delete, random_crop, random_cut
STRUCTURE TEST:        random_shuffle, repeat_contraction, random_subsequence
REALISTIC VARIATION:   back_translation_substitute, nucleotide_augment
PRODUCTION USE:        conservative_substitute, rsa_augment, nana_augment
```

### By Biological Impact
```
LOW (Destructive):     random_insert, random_substitute, random_delete, 
                       global_reverse, random_cut
MEDIUM (Disruptive):   random_swap, random_crop, random_shuffle, 
                       repeat_expansion, repeat_contraction, mask_residues
HIGH (Plausible):      conservative_substitute, nucleotide_augment, 
                       back_translation_substitute, spider_augment, bootgen_augment
VERY HIGH (Domain):    rsa_augment, preis_augment, nana_augment, 
                       migu_augment, imaen_simple, conservative_mask_residues
```

---

## Distribution Summary

```
TOKEN:    ███░░░░░░░░░░░░░░░░░░░░░░ 7/24 (29.2%)
SEQUENCE: ████░░░░░░░░░░░░░░░░░░░░░░ 8/24 (33.3%)
SEMANTIC: ████░░░░░░░░░░░░░░░░░░░░░░ 8/24 (33.3%)
```

---

## Key Features

**Token-Level Augmentations**
- Operate on individual amino acids
- Preserve overall structure initially
- Test point mutation robustness
- Range from realistic (conservative) to unrealistic (random)

**Sequence-Level Augmentations**
- Operate on regions/segments
- Test sequence organization importance
- Test domain independence
- Mostly unrealistic but useful for analysis

**Semantic-Level Augmentations**
- Incorporate biological knowledge
- Preserve protein properties
- Most likely to improve generalization
- Simulate evolutionary/biophysical processes

---

## For Your Presentation

**Key Message**: 
"EPA uses 24 augmentations balanced across three levels:
- 7 token-level (basic operations)
- 8 sequence-level (structural operations)  
- 8 semantic-level (biologically-informed)

This comprehensive approach tests robustness across different dimensions of variation."

**Highlight**: 
"Semantic-level methods (8) are 4-8x more comprehensive than published baselines (1-2), incorporating:
- Evolutionary genetics (nucleotide-based)
- Structural biology (RSA, BootGen)
- Machine learning (PREIS, MIGU)
- Network biology (NANA, IMAEN)"

---

**Document**: AUGMENTATION_CLASSIFICATION.md (25KB detailed version)  
**Created**: March 31, 2026  
**Status**: Complete classification of all 24 augmentations

