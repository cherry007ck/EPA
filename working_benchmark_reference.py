#!/usr/bin/env python3
"""
Comprehensive LSTM Benchmark - ALL 20 Augmentations
Binary Subcellular Localization Dataset
"""

import os
import sys
import lmdb
import pickle
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import json
from datetime import datetime

# Add augmentation path
sys.path.insert(0, '/home/luffy/dsa_project/merged/protein_augmentation/protein_augmentation')

# Import all augmentations
from augmentations.nta_augmentation import nucleotide_augment
from augmentations.residue_masking import mask_residues, conservative_mask_residues
from augmentations.bootgen import bootgen_augment
from augmentations.spider_augmentation import spider_augment
from augmentations.rsa_augmentation import rsa_augment
from augmentations.preis_augmentation import preis_augment
from augmentations.nana_augmentation import nana_augment
from augmentations.migu_augmentation import migu_augment
from augmentations.imaen import imaen_simple

# Dataset paths
BASE_DIR = "/home/luffy/dsa_project/merged/protein_augmentation/protein_augmentation/datasets/subcellular_localization_2"
TRAIN_PATH = f"{BASE_DIR}/subcellular_localization_2_train.lmdb"
VALID_PATH = f"{BASE_DIR}/subcellular_localization_2_valid.lmdb"
TEST_PATH = f"{BASE_DIR}/subcellular_localization_2_test.lmdb"

VOCAB_SIZE = 21
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

# Amino acids and codon mappings
AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
AMINO_ACID_TO_CODONS = {
    'A': ['GCU', 'GCC', 'GCA', 'GCG'], 'R': ['CGU', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
    'N': ['AAU', 'AAC'], 'D': ['GAU', 'GAC'], 'C': ['UGU', 'UGC'], 'Q': ['CAA', 'CAG'],
    'E': ['GAA', 'GAG'], 'G': ['GGU', 'GGC', 'GGA', 'GGG'], 'H': ['CAU', 'CAC'],
    'I': ['AUU', 'AUC', 'AUA'], 'L': ['UUA', 'UUG', 'CUU', 'CUC', 'CUA', 'CUG'],
    'K': ['AAA', 'AAG'], 'M': ['AUG'], 'F': ['UUU', 'UUC'],
    'P': ['CCU', 'CCC', 'CCA', 'CCG'], 'S': ['UCU', 'UCC', 'UCA', 'UCG', 'AGU', 'AGC'],
    'T': ['ACU', 'ACC', 'ACA', 'ACG'], 'W': ['UGG'], 'Y': ['UAU', 'UAC'],
    'V': ['GUU', 'GUC', 'GUA', 'GUG'], '*': ['UAA', 'UAG', 'UGA'],
}
CODON_TO_AMINO_ACID = {codon: aa for aa, codons in AMINO_ACID_TO_CODONS.items() for codon in codons}

# Simple augmentation functions
def crop_random_segment(sequence, residue_len):
    seq_len = len(sequence)
    if seq_len == 0: return sequence
    crop_len = max(1, int(residue_len * seq_len))
    start = random.randint(0, max(0, seq_len - crop_len))
    return sequence[start:start + crop_len]

def delete_random_residues(sequence, residue_len):
    return [res for res in sequence if random.random() > residue_len]

def reverse_sequence(sequence, residue_len=None):
    return list(reversed(sequence))

def shuffle_random_segment(sequence, residue_len):
    seq_len = len(sequence)
    if seq_len < 2: return sequence
    seg_len = max(1, int(residue_len * seq_len))
    start = random.randint(0, max(0, seq_len - seg_len))
    segment = sequence[start:start + seg_len]
    random.shuffle(segment)
    sequence = sequence.copy()
    sequence[start:start + seg_len] = segment
    return sequence

def cut_and_shuffle(sequence, residue_len):
    seq_len = len(sequence)
    if seq_len < 2: return sequence
    num_cuts = max(1, int(residue_len * 10))
    cut_points = sorted(random.sample(range(1, seq_len), min(num_cuts, seq_len-1))) + [seq_len]
    segments = [sequence[start:end] for start, end in zip([0] + cut_points[:-1], cut_points)]
    random.shuffle(segments)
    return [res for seg in segments for res in seg]

def subsequence_shuffle(sequence, residue_len):
    seq_len = len(sequence)
    if seq_len < 2: return sequence
    num_parts = max(1, int(residue_len * 10))
    cut_points = sorted(random.sample(range(1, seq_len), min(num_parts, seq_len-1))) + [seq_len]
    segments = [sequence[start:end] for start, end in zip([0] + cut_points[:-1], cut_points)]
    selected_segments = random.sample(segments, min(len(segments), num_parts))
    return [res for seg in selected_segments for res in seg]

def insert_random_residues(sequence, residue_len):
    sequence = sequence.copy()
    seq_len = len(sequence)
    num_insertions = max(0, int(residue_len * seq_len))
    for _ in range(num_insertions):
        pos = random.randint(0, len(sequence))
        sequence.insert(pos, random.choice(AMINO_ACIDS))
    return sequence

def substitute_random_residues(sequence, residue_len):
    sequence = sequence.copy()
    seq_len = len(sequence)
    num_subs = max(0, int(residue_len * seq_len))
    for _ in range(num_subs):
        pos = random.randint(0, seq_len - 1)
        sequence[pos] = random.choice(AMINO_ACIDS)
    return sequence

def swap_random_residues(sequence, residue_len):
    sequence = sequence.copy()
    seq_len = len(sequence)
    num_swaps = max(0, int(residue_len * seq_len))
    for _ in range(num_swaps):
        if seq_len < 2: break
        i, j = random.sample(range(seq_len), 2)
        sequence[i], sequence[j] = sequence[j], sequence[i]
    return sequence

def back_translation_substitute(seq, residue_len):
    mRNA = []
    for aa in seq:
        if aa in AMINO_ACID_TO_CODONS:
            mRNA.extend(list(random.choice(AMINO_ACID_TO_CODONS[aa])))
    if not mRNA: return seq
    mRNA_len = len(mRNA)
    num_subs = max(0, int(residue_len * mRNA_len))
    for _ in range(num_subs):
        pos = random.randint(0, mRNA_len - 1)
        mRNA[pos] = random.choice(['A', 'U', 'C', 'G'])
    codons = ["".join(mRNA[i:i+3]) for i in range(0, len(mRNA), 3)]
    aa_seq = []
    for c in codons:
        if len(c) == 3:
            aa = CODON_TO_AMINO_ACID.get(c, 'X')
            if aa in AMINO_ACIDS:
                aa_seq.append(aa)
    return aa_seq

# All augmentations
AUGMENTATIONS = {
    'baseline': None,
    'crop_random_segment': crop_random_segment,
    'delete_random_residues': delete_random_residues,
    'reverse_sequence': reverse_sequence,
    'shuffle_random_segment': shuffle_random_segment,
    'cut_and_shuffle': cut_and_shuffle,
    'subsequence_shuffle': subsequence_shuffle,
    'insert_random_residues': insert_random_residues,
    'substitute_random_residues': substitute_random_residues,
    'swap_random_residues': swap_random_residues,
    'back_translation_substitute': back_translation_substitute,
    'nucleotide_augment': nucleotide_augment,
    'mask_residues': mask_residues,
    'conservative_mask_residues': conservative_mask_residues,
    'bootgen_augment': bootgen_augment,
    'spider_augment': spider_augment,
    'rsa_augment': rsa_augment,
    'preis_augment': preis_augment,
    'nana_augment': nana_augment,
    'migu_augment': migu_augment,
    'imaen_simple': imaen_simple,
}


# LSTM Model
class LSTMModel(nn.Module):
    def __init__(self, embed=64, hidden=128):
        super().__init__()
        self.emb = nn.Embedding(VOCAB_SIZE, embed, padding_idx=0)
        self.lstm = nn.LSTM(embed, hidden, batch_first=True, bidirectional=True)
        self.head = nn.Sequential(
            nn.Linear(hidden * 2, 64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 1), nn.Sigmoid()
        )
    
    def forward(self, x):
        x = self.emb(x)
        _, (h, _) = self.lstm(x)
        h = torch.cat([h[-2], h[-1]], dim=1)
        return self.head(h).squeeze(1)


class BinLocDataset(Dataset):
    def __init__(self, lmdb_path, max_len=512, augment_fn=None, p=0.7, intensity=0.15):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False)
        self.max_len, self.augment_fn, self.p, self.intensity = max_len, augment_fn, p, intensity
        self.keys = []
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                try:
                    rec = pickle.loads(value)
                    if isinstance(rec, dict) and 'primary' in rec and 'localization' in rec:
                        self.keys.append(key)
                except Exception:
                    continue
    
    def __len__(self): return len(self.keys)
    
    def encode(self, seq):
        vocab = {aa: i + 1 for i, aa in enumerate(AMINO_ACIDS)}
        encoded = [vocab.get(aa, 0) for aa in seq[:self.max_len]]
        encoded += [0] * (self.max_len - len(encoded))
        return torch.tensor(encoded, dtype=torch.long)
    
    def __getitem__(self, idx):
        key = self.keys[idx]
        with self.env.begin() as txn:
            rec = pickle.loads(txn.get(key))
        seq, label = list(rec['primary']), float(rec['localization'])
        
        if self.augment_fn and random.random() < self.p:
            try:
                augmented = self.augment_fn(seq, self.intensity)
                if len(augmented) >= 5:
                    seq = augmented
            except Exception:
                pass
        
        return self.encode(''.join(seq)), torch.tensor(label, dtype=torch.float)


def collate(batch):
    seqs, labs = zip(*batch)
    return torch.stack(seqs), torch.stack(labs)


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for seqs, labels in loader:
        seqs, labels = seqs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(seqs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        preds = (outputs > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    return total_loss / len(loader), correct / total


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    with torch.no_grad():
        for seqs, labels in loader:
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            preds = (outputs > 0.5).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return total_loss / len(loader), correct / total


def train_and_evaluate(aug_name, aug_fn, epochs=10, batch_size=32):
    print(f"\n{'='*80}\nTesting: {aug_name}\n{'='*80}")
    start_time = datetime.now()
    
    train_ds = BinLocDataset(TRAIN_PATH, augment_fn=aug_fn)
    valid_ds = BinLocDataset(VALID_PATH)
    test_ds = BinLocDataset(TEST_PATH)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate)
    valid_loader = DataLoader(valid_ds, batch_size=batch_size, collate_fn=collate)
    test_loader = DataLoader(test_ds, batch_size=batch_size, collate_fn=collate)
    
    model = LSTMModel().to(DEVICE)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    best_val_acc, best_model_state = 0, None
    
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc = evaluate(model, valid_loader, criterion, DEVICE)
        print(f"Epoch {epoch+1}/{epochs} | Train: {train_acc:.4f} | Val: {val_acc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()
    
    model.load_state_dict(best_model_state)
    test_loss, test_acc = evaluate(model, test_loader, criterion, DEVICE)
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Test Acc: {test_acc:.4f} | Best Val: {best_val_acc:.4f} | Time: {duration:.1f}s")
    
    return {
        'augmentation': aug_name,
        'test_acc': float(test_acc),
        'best_val_acc': float(best_val_acc),
        'training_time_seconds': duration
    }


def main():
    print("="*80)
    print("Comprehensive LSTM Benchmark - ALL 20 Augmentations - Binary Localization")
    print("="*80)
    
    all_results = []
    for aug_name, aug_fn in AUGMENTATIONS.items():
        try:
            results = train_and_evaluate(aug_name, aug_fn, epochs=10, batch_size=32)
            all_results.append(results)
        except Exception as e:
            print(f"\nERROR with {aug_name}: {e}")
            import traceback
            traceback.print_exc()
    
    output_file = "lstm_binloc_all_augmentations_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}\nBenchmark Complete!\n{'='*80}")
    print(f"Results saved to: {output_file}\n")
    
    print("="*80)
    print("SUMMARY TABLE - ALL 20 AUGMENTATIONS WITH LSTM")
    print("="*80)
    print(f"{'Augmentation':<35} {'Test Acc':<12} {'Time (s)':<10}")
    print("-"*80)
    
    all_results_sorted = sorted(all_results, key=lambda x: x['test_acc'], reverse=True)
    baseline_acc = next((r['test_acc'] for r in all_results if r['augmentation'] == 'baseline'), None)
    
    for result in all_results_sorted:
        improvement = ""
        if baseline_acc and result['augmentation'] != 'baseline':
            diff = result['test_acc'] - baseline_acc
            improvement = f" ({diff:+.2%})"
        print(f"{result['augmentation']:<35} {result['test_acc']:<12.4f} {result['training_time_seconds']:<10.1f}{improvement}")
    
    print("="*80)


if __name__ == "__main__":
    main()
