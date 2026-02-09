#!/usr/bin/env python3
"""
Trainer for Traditional ML Models (Random Forest)
Handles offline augmentation (pre-augment data before training)
"""

import sys
import torch
import numpy as np
from tqdm import tqdm
from sklearn.metrics import accuracy_score, matthews_corrcoef
from scipy.stats import spearmanr

from scripts.flexible_dataset import FlexibleLMDBDataset
from models.random_forest_models import RandomForestModel


class TraditionalMLTrainer:
    """Trainer for traditional ML models with offline augmentation"""
    
    def __init__(self, config, dataset_cfg, model_cfg):
        self.config = config
        self.dataset_cfg = dataset_cfg
        self.model_cfg = model_cfg
        
        self.task_type = dataset_cfg.get('task_type', 'classification')
        self.is_ppi = not dataset_cfg['has_single_sequence']
    
    def train(self, augmentation_name, augmentation_fn, magnitude):
        """Train model with specific augmentation"""
        
        print(f"Loading and preprocessing data...")
        
        # Load datasets
        train_ds = FlexibleLMDBDataset(self.config.dataset_name, 'train')
        test_ds = FlexibleLMDBDataset(self.config.dataset_name, 'test')
        
        # Subset if needed
        if self.config.use_subset:
            train_ds.keys = train_ds.keys[:self.config.subset_size]
            test_ds.keys = test_ds.keys[:min(500, len(test_ds.keys))]
        
        # Load and augment training data
        X_train, y_train = self._load_and_augment_data(
            train_ds, augmentation_fn, magnitude, augmentation_name != "baseline"
        )
        
        # Load test data (no augmentation)
        X_test, y_test = self._load_and_augment_data(
            test_ds, None, 0.0, False
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Create and train Random Forest
        print("Training Random Forest...")
        rf_model = RandomForestModel(
            task_type=self.task_type,
            **self.model_cfg['default_params']
        )
        
        rf_model.fit(X_train, y_train, is_ppi=self.is_ppi)
        print("✓ Training complete")
        
        # Evaluate
        print("Evaluating...")
        y_pred = rf_model.predict(X_test, is_ppi=self.is_ppi)
        
        if self.task_type == 'regression':
            spearman, _ = spearmanr(y_test, y_pred)
            print(f"✅ {augmentation_name}: Test Spearman={spearman:.4f}")
            
            result = {
                'augmentation': augmentation_name,
                'magnitude': magnitude,
                'test_spearman': spearman,
                'best_valid_spearman': spearman,  # RF doesn't have separate validation
                'test_mcc': 0.0
            }
        else:
            accuracy = accuracy_score(y_test, y_pred)
            mcc = matthews_corrcoef(y_test, y_pred) if len(set(y_test)) > 1 else 0.0
            print(f"✅ {augmentation_name}: Test Acc={accuracy:.4f}, MCC={mcc:.4f}")
            
            result = {
                'augmentation': augmentation_name,
                'magnitude': magnitude,
                'test_acc': accuracy,
                'best_valid_acc': accuracy,  # RF doesn't have separate validation
                'test_mcc': mcc
            }
        
        return result
    
    def _load_and_augment_data(self, dataset, augmentation_fn, magnitude, apply_augmentation):
        """Load data from dataset and optionally augment it"""
        sequences = []
        labels = []
        
        for i in tqdm(range(len(dataset)), desc="Loading data"):
            seq_tensor, label = dataset[i]
            
            # Decode sequence
            if isinstance(seq_tensor, list):
                # PPI dataset
                seq1 = self._decode_sequence(seq_tensor[0])
                seq2 = self._decode_sequence(seq_tensor[1])
                
                # Apply augmentation if needed
                if apply_augmentation and augmentation_fn is not None:
                    seq1 = ''.join(augmentation_fn(list(seq1), magnitude))
                    seq2 = ''.join(augmentation_fn(list(seq2), magnitude))
                
                sequences.append((seq1, seq2))
            else:
                # Single sequence
                seq = self._decode_sequence(seq_tensor)
                
                # Apply augmentation if needed
                if apply_augmentation and augmentation_fn is not None:
                    seq = ''.join(augmentation_fn(list(seq), magnitude))
                
                sequences.append(seq)
            
            # Handle label
            if isinstance(label, tuple):
                # Residue-level classification - not supported by RF
                raise ValueError("Random Forest does not support residue-level classification")
            elif isinstance(label, torch.Tensor):
                labels.append(label.item())
            else:
                labels.append(label)
        
        return sequences, np.array(labels)
    
    def _decode_sequence(self, tensor):
        """Convert tensor back to amino acid sequence"""
        vocab = "ACDEFGHIKLMNPQRSTVWY"
        seq = []
        for idx in tensor:
            if idx > 0:  # Skip padding (0)
                seq.append(vocab[idx - 1])
        return ''.join(seq)
