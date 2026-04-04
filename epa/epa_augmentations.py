"""
EPA Augmentations Module

Central hub for all protein sequence augmentation techniques.
Provides 23 augmentation operations across three levels:
  - Token-level (7): insert, substitute, swap, delete, mask, conservative mask/substitute
  - Sequence-level (8): crop, shuffle, reverse, cut, subsequence, repeat expand/contract, back-translation
  - Semantic-level (8): NTA, BootGen, RSA, PreIS, NaNa, MiGu, IMAEN, Spider

Reference:
    Sun et al. (2024) "Enhancing Protein Predictive Models via Proteins
    Data Augmentation: A Benchmark and New Directions"
"""

import os
import sys

# Use relative path based on this file's location (portable across environments)
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Import all research augmentations
from aug_implementations.nta_augmentation import nucleotide_augment
from aug_implementations.residue_masking import mask_residues, conservative_mask_residues
from aug_implementations.bootgen import bootgen_augment
from aug_implementations.spider_augmentation import spider_augment
from aug_implementations.rsa_augmentation import rsa_augment
from aug_implementations.preis_augmentation import preis_augment
from aug_implementations.migu_augmentation import migu_augment
from aug_implementations.imaen import imaen_simple
from aug_implementations.nana_augmentation import nana_augment

import random

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# Genetic code for back-translation
genetic_code_protein2mRNA = {
    "F": ["TTT", "TTC"], "L": ["TTA", "TTG", "CTT", "CTC", "CTA", "CTG"],
    "I": ["ATT", "ATC", "ATA"], "M": ["ATG"],
    "V": ["GTT", "GTC", "GTA", "GTG"], "S": ["TCT", "TCC", "TCA", "TCG", "AGT", "AGC"],
    "P": ["CCT", "CCC", "CCA", "CCG"], "T": ["ACT", "ACC", "ACA", "ACG"],
    "A": ["GCT", "GCC", "GCA", "GCG"], "Y": ["TAT", "TAC"],
    "H": ["CAT", "CAC"], "Q": ["CAA", "CAG"],
    "N": ["AAT", "AAC"], "K": ["AAA", "AAG"],
    "D": ["GAT", "GAC"], "E": ["GAA", "GAG"],
    "C": ["TGT", "TGC"], "W": ["TGG"],
    "R": ["CGT", "CGC", "CGA", "CGG", "AGA", "AGG"],
    "G": ["GGT", "GGC", "GGA", "GGG"],
    "Stop": ["TAA", "TAG", "TGA"]
}
genetic_code_mRNA2protein = {codon: aa for aa, codons in genetic_code_protein2mRNA.items() for codon in codons}

# Core augmentations (10)
def random_insert(seq, m):
    seq_len = len(seq)
    if seq_len == 0: return seq
    for _ in range(min(int(m * seq_len), seq_len)):
        seq.insert(random.randint(0, len(seq)), random.choice(list(AMINO_ACIDS)))
    return seq

def random_substitute(seq, m):
    seq_len = len(seq)
    if seq_len == 0: return seq
    for pos in random.sample(range(seq_len), min(int(m * seq_len), seq_len)):
        seq[pos] = random.choice(list(AMINO_ACIDS))
    return seq

def random_swap(seq, m):
    seq_len = len(seq)
    if seq_len < 2: return seq
    for _ in range(min(int(m * seq_len), seq_len // 2)):
        i, j = random.sample(range(seq_len), 2)
        seq[i], seq[j] = seq[j], seq[i]
    return seq

def random_delete(seq, m):
    seq = [r for r in seq if random.random() > m]
    return seq if len(seq) > 0 else [random.choice(list(AMINO_ACIDS))]

def random_crop(seq, m):
    seq_len = len(seq)
    if seq_len == 0: return seq
    crop_len = max(1, int(m * seq_len))
    if crop_len >= seq_len: return seq
    start = random.randint(0, seq_len - crop_len)
    return seq[start:start + crop_len]

def random_shuffle(seq, m):
    seq_len = len(seq)
    if seq_len < 2: return seq
    seg_len = max(1, int(m * seq_len))
    if seg_len >= seq_len:
        random.shuffle(seq)
        return seq
    start = random.randint(0, seq_len - seg_len)
    segment = seq[start:start + seg_len]
    random.shuffle(segment)
    seq[start:start + seg_len] = segment
    return seq

def global_reverse(seq, m):
    seq.reverse()
    return seq

def random_cut(seq, m):
    seq_len = len(seq)
    if seq_len < 2: return seq
    num_cuts = max(1, int(m * 10))
    if num_cuts >= seq_len: num_cuts = seq_len - 1
    cuts = sorted(random.sample(range(1, seq_len), min(num_cuts, seq_len - 1))) + [seq_len]
    segs = [seq[s:e] for s, e in zip([0] + cuts[:-1], cuts)]
    random.shuffle(segs)
    return [r for seg in segs for r in seg]

def random_subsequence(seq, m):
    seq_len = len(seq)
    if seq_len < 2: return seq
    num_parts = max(1, int(m * 10))
    if num_parts >= seq_len: num_parts = seq_len - 1
    cuts = sorted(random.sample(range(1, seq_len), min(num_parts, seq_len - 1))) + [seq_len]
    segs = [seq[s:e] for s, e in zip([0] + cuts[:-1], cuts)]
    selected = random.sample(segs, min(len(segs), max(1, int(m * len(segs)))))
    return [r for seg in selected for r in seg]

def back_translation_substitute(seq, m):
    seq_len = len(seq)
    if seq_len == 0: return seq
    mRNA = []
    for r in seq:
        if r in genetic_code_protein2mRNA:
            mRNA.extend(list(random.choice(genetic_code_protein2mRNA[r])))
    if not mRNA: return seq
    for _ in range(min(int(m * len(mRNA)), len(mRNA))):
        pos = random.randint(0, len(mRNA) - 1)
        old = mRNA[pos]
        mRNA[pos] = random.choice(['T', 'C', 'A', 'G'])
        codon_start = pos - (pos % 3)
        codon = "".join(mRNA[codon_start:codon_start + 3])
        if len(codon) == 3 and codon in genetic_code_protein2mRNA.get("Stop", []):
            mRNA[pos] = old
    result = []
    for i in range(0, len(mRNA), 3):
        codon = "".join(mRNA[i:i + 3])
        if len(codon) == 3 and codon in genetic_code_mRNA2protein:
            aa = genetic_code_mRNA2protein[codon]
            if aa != "Stop" and aa in AMINO_ACIDS:
                result.append(aa)
    return result if result else seq

# Simple additions (3)
def repeat_expansion(seq, m):
    seq_len = len(seq)
    if seq_len < 4: return seq
    for length in [2, 3]:
        for i in range(seq_len - length):
            pattern = seq[i:i+length]
            if i + 2 * length <= seq_len and seq[i+length:i+2*length] == pattern:
                if random.random() < m:
                    return seq[:i+2*length] + pattern + seq[i+2*length:]
    return seq

def repeat_contraction(seq, m):
    seq_len = len(seq)
    if seq_len < 4: return seq
    for length in [2, 3]:
        for i in range(seq_len - length):
            pattern = seq[i:i+length]
            if i + 2 * length <= seq_len and seq[i+length:i+2*length] == pattern:
                if random.random() < m:
                    return seq[:i+length] + seq[i+2*length:]
    return seq

def conservative_substitute(seq, m):
    groups = {
        'A': ['G', 'S', 'T'], 'V': ['I', 'L', 'M'], 'I': ['V', 'L', 'M'],
        'L': ['I', 'V', 'M'], 'M': ['I', 'V', 'L'], 'F': ['Y', 'W'],
        'Y': ['F', 'W'], 'W': ['F', 'Y'], 'K': ['R', 'H'],
        'R': ['K', 'H'], 'H': ['K', 'R'], 'D': ['E', 'N'],
        'E': ['D', 'Q'], 'N': ['D', 'Q', 'S'], 'Q': ['E', 'N'],
        'S': ['T', 'A', 'N'], 'T': ['S', 'A'], 'G': ['A'],
        'C': ['S'], 'P': ['A']
    }
    seq_len = len(seq)
    if seq_len == 0: return seq
    for pos in random.sample(range(seq_len), min(int(m * seq_len), seq_len)):
        if seq[pos] in groups and groups[seq[pos]]:
            seq[pos] = random.choice(groups[seq[pos]])
    return seq

# Augmentation list
def augment_list():
    return [
        (random_insert, 0.0, 0.5), (random_substitute, 0.0, 0.5),
        (random_swap, 0.0, 0.5), (random_delete, 0.0, 0.5),
        (random_crop, 0.4, 1.0), (random_shuffle, 0.0, 0.5),
        (global_reverse, 0.0, 0.0), (random_cut, 0.2, 1.0),
        (random_subsequence, 0.2, 1.0), (back_translation_substitute, 0.0, 0.5),
        (repeat_expansion, 0.0, 1.0), (repeat_contraction, 0.0, 1.0),
        (conservative_substitute, 0.0, 0.5),
        (nucleotide_augment, 0.0, 0.5), (mask_residues, 0.0, 0.3),
        (conservative_mask_residues, 0.0, 0.3), (bootgen_augment, 0.0, 0.5),
        (spider_augment, 0.0, 0.5), (rsa_augment, 0.0, 0.5),
        (preis_augment, 0.0, 0.5), (nana_augment, 0.0, 0.5),
        (migu_augment, 0.0, 0.5), (imaen_simple, 0.0, 0.5),
    ]

augment_dict = {fn.__name__: (fn, v1, v2) for fn, v1, v2 in augment_list()}

def get_augment(name):
    return augment_dict[name]

def random_augment(seq, aug_list=None):
    if aug_list is None:
        fn, low, high = random.choice(augment_list())
    else:
        fn, low, high = random.choice([augment_dict[n] for n in aug_list])
    level = random.random()
    magnitude = level * (high - low) + low
    return fn(seq, magnitude)

def apply_augment(seq, policy):
    sub_policy = random.choice(policy)
    for name, pr, level in sub_policy:
        if random.random() > pr:
            continue
        fn, low, high = get_augment(name)
        magnitude = level * (high - low) + low
        seq = fn(seq, magnitude)
    return seq
