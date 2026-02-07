#!/usr/bin/env python3
"""
Flexible LMDB Dataset Handler for EPA
Supports multiple dataset types with different structures
"""

import os
import torch
import lmdb
import pickle
from torch.utils.data import Dataset
from dataset_config import get_dataset_config


class FlexibleLMDBDataset(Dataset):
    """
    Flexible LMDB Dataset that adapts to different dataset structures
    """
    def __init__(self, dataset_name, split='train', augment_fn=None, base_path='/home/hor20kud/aug/EPA'):
        """
        Args:
            dataset_name: Name of dataset (e.g., 'subcellular_localization', 'remote_homology_fold')
            split: 'train', 'valid', or 'test'
            augment_fn: Optional augmentation function
            base_path: Base path to EPA directory
        """
        self.dataset_name = dataset_name
        self.config = get_dataset_config(dataset_name)
        self.augment_fn = augment_fn
        
        # Build path to LMDB
        file_map = {
            'train': self.config['train_file'],
            'valid': self.config['valid_file'],
            'test': self.config['test_file']
        }
        
        lmdb_path = os.path.join(base_path, self.config['base_dir'], file_map[split])
        
        # Open LMDB
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False, readahead=False, meminit=False)
        self.keys = []
        
        # Pre-load all valid keys
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                try:
                    rec = pickle.loads(value)
                    if isinstance(rec, dict):
                        # Check if required fields exist
                        if self.config['has_single_sequence']:
                            if self.config['sequence_field'] in rec and self.config['label_field'] in rec:
                                self.keys.append(key)
                        else:
                            # Multiple sequences (e.g., PPI)
                            if all(field in rec for field in self.config['sequence_field']) and self.config['label_field'] in rec:
                                self.keys.append(key)
                except:
                    continue
    
    def __len__(self):
        return len(self.keys)
    
    def __getitem__(self, idx):
        with self.env.begin() as txn:
            data = pickle.loads(txn.get(self.keys[idx]))
        
        # Extract sequences
        if self.config['has_single_sequence']:
            sequence = list(data[self.config['sequence_field']])
            
            # Apply augmentation if provided
            if self.augment_fn:
                sequence = self.augment_fn(sequence.copy())
            
            # Encode sequence
            seq_tensor = self.encode_sequence(sequence)
            
        else:
            # Handle multiple sequences (e.g., protein-protein interaction)
            sequences = [list(data[field]) for field in self.config['sequence_field']]
            
            # Apply augmentation to both sequences
            if self.augment_fn:
                sequences = [self.augment_fn(seq.copy()) for seq in sequences]
            
            # Encode both sequences
            seq_tensor = [self.encode_sequence(seq) for seq in sequences]
        
        # Extract label
        label = int(data[self.config['label_field']])
        
        return seq_tensor, torch.tensor(label, dtype=torch.long)
    
    def encode_sequence(self, sequence):
        """Encode amino acid sequence to tensor"""
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq_tensor = torch.zeros(len(sequence), dtype=torch.long)
        for i, aa in enumerate(sequence):
            if aa in vocab:
                seq_tensor[i] = vocab.index(aa) + 1  # 0 is reserved for padding
        return seq_tensor


def get_collate_fn(dataset_name):
    """
    Get appropriate collate function for dataset
    """
    config = get_dataset_config(dataset_name)
    
    if config['has_single_sequence']:
        return collate_fn_single_sequence
    else:
        return collate_fn_ppi


def collate_fn_single_sequence(batch):
    """Collate function for single sequence datasets"""
    sequences, labels = zip(*batch)
    
    # Limit max sequence length to prevent OOM
    MAX_SEQ_LEN = 2000
    max_len = min(max(len(s) for s in sequences), MAX_SEQ_LEN)
    
    padded_seqs = torch.zeros(len(sequences), max_len, dtype=torch.long)
    for i, seq in enumerate(sequences):
        seq_len = min(len(seq), max_len)
        padded_seqs[i, :seq_len] = seq[:seq_len]
    
    return padded_seqs, torch.stack(labels)


def collate_fn_ppi(batch):
    """Collate function for PPI datasets (two sequences per sample)"""
    seq_pairs, labels = zip(*batch)
    
    # Separate the two sequences
    seqs1, seqs2 = zip(*seq_pairs)
    
    # Limit max sequence length
    MAX_SEQ_LEN = 1500
    max_len1 = min(max(len(s) for s in seqs1), MAX_SEQ_LEN)
    max_len2 = min(max(len(s) for s in seqs2), MAX_SEQ_LEN)
    
    # Pad first sequences
    padded_seqs1 = torch.zeros(len(seqs1), max_len1, dtype=torch.long)
    for i, seq in enumerate(seqs1):
        seq_len = min(len(seq), max_len1)
        padded_seqs1[i, :seq_len] = seq[:seq_len]
    
    # Pad second sequences
    padded_seqs2 = torch.zeros(len(seqs2), max_len2, dtype=torch.long)
    for i, seq in enumerate(seqs2):
        seq_len = min(len(seq), max_len2)
        padded_seqs2[i, :seq_len] = seq[:seq_len]
    
    return (padded_seqs1, padded_seqs2), torch.stack(labels)


# Test function
if __name__ == "__main__":
    from dataset_config import list_available_datasets
    
    print("Testing Flexible LMDB Dataset")
    print("="*60)
    
    list_available_datasets()
    
    print("\nTesting subcellular_localization dataset:")
    ds = FlexibleLMDBDataset('subcellular_localization', split='train')
    print(f"  Loaded {len(ds)} samples")
    seq, label = ds[0]
    print(f"  Sample 0: sequence length={len(seq)}, label={label}")
    
    print("\nTesting subcellular_localization_2 dataset:")
    ds2 = FlexibleLMDBDataset('subcellular_localization_2', split='train')
    print(f"  Loaded {len(ds2)} samples")
    seq, label = ds2[0]
    print(f"  Sample 0: sequence length={len(seq)}, label={label}")
    
    print("\nTesting yeast_ppi dataset:")
    ds3 = FlexibleLMDBDataset('yeast_ppi', split='train')
    print(f"  Loaded {len(ds3)} samples")
    seqs, label = ds3[0]
    print(f"  Sample 0: seq1 length={len(seqs[0])}, seq2 length={len(seqs[1])}, label={label}")
    
    print("\n✅ All tests passed!")
