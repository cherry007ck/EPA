#!/usr/bin/env python3
"""Quick test of all datasets"""
import torch
from torch.utils.data import DataLoader
from flexible_dataset import FlexibleLMDBDataset, get_collate_fn
from dataset_config import get_dataset_config

datasets = [
    'subcellular_localization',
    'subcellular_localization_2',
    'yeast_ppi',
]

print("="*60)
print("Quick Dataset Test")
print("="*60)

for ds_name in datasets:
    print(f"\n{ds_name}:")
    try:
        config = get_dataset_config(ds_name)
        ds = FlexibleLMDBDataset(ds_name, 'train')
        collate = get_collate_fn(ds_name)
        loader = DataLoader(ds, batch_size=4, collate_fn=collate)
        
        # Get one batch
        batch = next(iter(loader))
        if config['has_single_sequence']:
            seqs, labels = batch
            print(f"  ✅ Loaded: {len(ds)} samples")
            print(f"  Batch shape: {seqs.shape}")
            print(f"  Labels shape: {labels.shape}")
        else:
            (seqs1, seqs2), labels = batch
            print(f"  ✅ Loaded: {len(ds)} samples (PPI)")
            print(f"  Batch seq1 shape: {seqs1.shape}")
            print(f"  Batch seq2 shape: {seqs2.shape}")
            print(f"  Labels shape: {labels.shape}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("All tests complete!")
print("="*60)
