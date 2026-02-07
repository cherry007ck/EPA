#!/usr/bin/env python3
"""Comprehensive LSTM Benchmark -  Working Version"""
import os, sys, torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import lmdb, pickle, random, numpy as np, json
from datetime import datetime
from tqdm import tqdm
from sklearn.metrics import matthews_corrcoef

sys.path.insert(0, 'epa')
from epa_augmentations import augment_list
from util import load_config

class LMDBDataset(Dataset):
    """Fixed LMDB dataset - pre-loads all keys"""
    def __init__(self, lmdb_path, augment_fn=None):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False, readahead=False, meminit=False)
        self.augment_fn = augment_fn
        self.keys = []
        # Pre-load all valid keys
        with self.env.begin() as txn:
            for key, value in txn.cursor():
                try:
                    rec = pickle.loads(value)
                    if isinstance(rec, dict) and 'primary' in rec and 'localization' in rec:
                        self.keys.append(key)
                except: 
                    continue
    
    def __len__(self): 
        return len(self.keys)
    
    def __getitem__(self, idx):
        with self.env.begin() as txn:
            data = pickle.loads(txn.get(self.keys[idx]))
        
        sequence = list(data['primary'])
        label = int(data['localization'])
        
        if self.augment_fn:
            sequence = self.augment_fn(sequence.copy())
        
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq_tensor = torch.zeros(len(sequence), dtype=torch.long)
        for i, aa in enumerate(sequence):
            if aa in vocab:
                seq_tensor[i] = vocab.index(aa)
        
        return seq_tensor, torch.tensor(label, dtype=torch.long)

def collate_fn(batch):
    sequences, labels = zip(*batch)
    # Limit max sequence length to prevent OOM with augmentations that insert
    MAX_SEQ_LEN = 2000
    max_len = min(max(len(s) for s in sequences), MAX_SEQ_LEN)
    padded_seqs = torch.zeros(len(sequences), max_len, dtype=torch.long)
    for i, seq in enumerate(sequences):
        seq_len = min(len(seq), max_len)
        padded_seqs[i, :seq_len] = seq[:seq_len]
    return padded_seqs, torch.stack(labels)

class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Embedding(20, 128, padding_idx=0)
        self.lstm = nn.LSTM(128, 256, 2, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(512, 2)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(self.dropout(x.mean(dim=1)))

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for seqs, labels in tqdm(loader, desc="Training", leave=False):
        seqs, labels = seqs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(seqs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
    return total_loss / len(loader), correct / total

def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for seqs, labels in tqdm(loader, desc="Evaluating", leave=False):
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return correct / total, matthews_corrcoef(all_labels, all_preds)

def train_with_aug(aug_name, aug_fn, magnitude, config, device, epochs=30):
    print(f"\n{'='*70}\nTraining: {aug_name} (mag={magnitude:.2f})\n{'='*70}")
    
    def augment(seq):
        return aug_fn(seq, magnitude)
    
    train_ds = LMDBDataset(config.dataset.train_path, augment_fn=augment if aug_name != "baseline" else None)
    valid_ds = LMDBDataset(config.dataset.valid_path)
    test_ds = LMDBDataset(config.dataset.test_path)
    
    # Conservative batch size to handle variable-length augmented sequences
    # num_workers=0 due to LMDB limitations with multiprocessing
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True, collate_fn=collate_fn, num_workers=0, pin_memory=True)
    valid_loader = DataLoader(valid_ds, batch_size=64, shuffle=False, collate_fn=collate_fn, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, collate_fn=collate_fn, num_workers=0, pin_memory=True)
    
    model = LSTMModel().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    best_valid_acc, best_state = 0, None
    
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        valid_acc, valid_mcc = evaluate(model, valid_loader, device)
        print(f"Epoch {epoch+1}/{epochs}: Loss={train_loss:.4f}, Train={train_acc:.4f}, Valid={valid_acc:.4f}, MCC={valid_mcc:.4f}")
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_state = model.state_dict().copy()
    
    model.load_state_dict(best_state)
    test_acc, test_mcc = evaluate(model, test_loader, device)
    print(f"✅ {aug_name}: Valid={best_valid_acc:.4f}, Test={test_acc:.4f}, MCC={test_mcc:.4f}")
    
    # Clear GPU memory after each augmentation training
    del model, criterion, optimizer, train_loader, valid_loader, test_loader
    del train_ds, valid_ds, test_ds
    torch.cuda.empty_cache()
    
    return {'augmentation': aug_name, 'magnitude': magnitude, 'best_valid_acc': best_valid_acc, 'test_acc': test_acc, 'test_mcc': test_mcc}

def main():
    config = load_config("config/LSTM/binloc_LSTM.yaml")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}\n")
    
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    EPOCHS, MAGNITUDE = 30, 0.15
    augs = augment_list()
    
    print(f"{'='*70}\nBENCHMARK: {len(augs)} augmentations × {EPOCHS} epochs\n{'='*70}\n")
    
    results = []
    
    # Baseline
    results.append(train_with_aug("baseline", lambda seq, m: seq, 0.0, config, device, EPOCHS))
    
    # All augmentations
    for fn, low, high in augs:
        mag = MAGNITUDE if low <= MAGNITUDE <= high else (low + high) / 2
        results.append(train_with_aug(fn.__name__, fn, mag, config, device, EPOCHS))
        # Save intermediate
        with open(f"benchmark_intermediate_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
            json.dump(results, f, indent=2)
    
    # Final summary
    sorted_results = sorted(results, key=lambda x: x['test_acc'], reverse=True)
    print(f"\n{'='*70}\nFINAL RESULTS\n{'='*70}")
    print(f"{'Rank':<6} {'Augmentation':<35} {'Test Acc':<12} {'Test MCC':<12}")
    print("-" * 70)
    for rank, r in enumerate(sorted_results, 1):
        print(f"{rank:<6} {r['augmentation']:<35} {r['test_acc']:.4f}       {r['test_mcc']:.4f}")
    
    final_file = f"benchmark_results_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(final_file, 'w') as f:
        json.dump({'config': {'epochs': EPOCHS, 'magnitude': MAGNITUDE}, 'results': sorted_results}, f, indent=2)
    print(f"\n✅ Saved to: {final_file}")

if __name__ == "__main__":
    main()
