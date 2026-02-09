#!/usr/bin/env python3
"""EPA Benchmark - based on working lstm_binloc benchmark"""
import os, sys, torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import lmdb, pickle, random, numpy as np, json
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import matthews_corrcoef

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'epa'))
from epa_augmentations import augment_list
from util import load_config

class LMDBDataset(Dataset):
    def __init__(self, lmdb_path, augment_fn=None):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False)
        self.augment_fn = augment_fn
        self.keys = []
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                try:
                    rec = pickle.loads(value)
                    if isinstance(rec, dict) and 'primary' in rec and 'localization' in rec:
                        self.keys.append(key)
                except: continue
    
    def __len__(self): 
        return len(self.keys)
    
    def __getitem__(self, idx):
        with self.env.begin() as txn:
            data =pickle.loads(txn.get(self.keys[idx]))
        
        sequence = list(data['primary'])
        label = int(data['localization'])
        
        if self.augment_fn is not None:
            sequence = self.augment_fn(sequence.copy())
        
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq_tensor = torch.zeros(len(sequence), dtype=torch.long)
        for i, aa in enumerate(sequence):
            if aa in vocab:
                seq_tensor[i] = vocab.index(aa)
        
        return seq_tensor, torch.tensor(label, dtype=torch.long)

def collate_fn(batch):
    sequences, labels = zip(*batch)
    max_len = max(len(s) for s in sequences)
    padded_seqs = torch.zeros(len(sequences), max_len, dtype=torch.long)
    for i, seq in enumerate(sequences):
        padded_seqs[i, :len(seq)] = seq
    return padded_seqs, torch.stack(labels)

class LSTM Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(20, 128, padding_idx=0)
        self.lstm = nn.LSTM(128, 256, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(512, 2)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        x = x.mean(dim=1)
        return self.fc(self.dropout(x))

print("✅ Script loaded. Run with: python benchmark_corrected.py")
