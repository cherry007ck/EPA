"""
Protein Sequence Augmentation Techniques

This package contains various augmentation methods for protein sequences,
designed to work with the PyTorch-based protein data framework.

Available augmentation techniques:
- NTA (Nucleotide Augmentation): Synonymous codon substitution
- Residue Masking: MLM-style and conservative masking  
- BootGen: Bootstrapped generation with rank-based selection
- Spider: Random substitution + insertion
- RSA: Retrieved Sequence Augmentation (conservative mutations)
- PreIS: Supervised Data Augmentation (self-mixing)
- NaNa: Novel Augmentation of New Node Attributes
- MiGu: Molecular Interactions and Geometric Upgrading
- IMAEN: Interpretable Molecular Augmentation
"""

from .nta_augmentation import nucleotide_augment
from .residue_masking import mask_residues, simple_mask_residues, conservative_mask_residues
from .bootgen import bootgen_augment
from .spider_augmentation import spider_augment
from .rsa_augmentation import rsa_augment, rsa_augment_with_original
from .preis_augmentation import preis_augment
from .nana_augmentation import nana_augment
from .migu_augmentation import migu_augment
from .imaen import imaen_simple, imaen_augment

__all__ = [
    'nucleotide_augment',
    'mask_residues',
    'simple_mask_residues',
    'conservative_mask_residues',
    'bootgen_augment',
    'spider_augment',
    'rsa_augment',
    'rsa_augment_with_original',
    'preis_augment',
    'nana_augment',
    'migu_augment',
    'imaen_simple',
    'imaen_augment'
]
