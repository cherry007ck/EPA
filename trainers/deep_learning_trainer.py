#!/usr/bin/env python3
"""
Trainer for Deep Learning Models (LSTM, ResNet, ESM-2)
Handles online augmentation during training
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.metrics import matthews_corrcoef
from scipy.stats import spearmanr

from scripts.flexible_dataset import FlexibleLMDBDataset, get_collate_fn
from models import (
    LSTMModel, PPIModel, RegressionModel, ResidueLSTMModel,
    ProteinResNet, ProteinResNetPPI, ProteinResNetRegression, ProteinResNetResidue
)


class DeepLearningTrainer:
    """Trainer for deep learning models with online augmentation"""
    
    def __init__(self, config, dataset_cfg, model_cfg):
        self.config = config
        self.dataset_cfg = dataset_cfg
        self.model_cfg = model_cfg
        
        self.device = torch.device(config.device if torch.cuda.is_available() else 'cpu')
        self.task_type = dataset_cfg.get('task_type', 'classification')
        self.is_ppi = not dataset_cfg['has_single_sequence']
    
    def train(self, augmentation_name, augmentation_fn, magnitude):
        """Train model with specific augmentation"""
        
        # Create augmentation wrapper
        def augment(seq):
            if augmentation_fn is None:
                return seq
            return augmentation_fn(seq, magnitude)
        
        # Load datasets
        train_ds = FlexibleLMDBDataset(
            self.config.dataset_name,
            'train',
            augment_fn=augment if augmentation_name != "baseline" else None
        )
        valid_ds = FlexibleLMDBDataset(self.config.dataset_name, 'valid')
        test_ds = FlexibleLMDBDataset(self.config.dataset_name, 'test')
        
        # Subset if needed
        if self.config.use_subset:
            train_ds.keys = train_ds.keys[:self.config.subset_size]
            valid_ds.keys = valid_ds.keys[:min(500, len(valid_ds.keys))]
            test_ds.keys = test_ds.keys[:min(500, len(test_ds.keys))]
        
        # Create dataloaders
        collate = get_collate_fn(self.config.dataset_name)
        train_loader = DataLoader(
            train_ds,
            batch_size=self.config.batch_size,
            shuffle=True,
            collate_fn=collate,
            num_workers=0,
            pin_memory=True
        )
        valid_loader = DataLoader(
            valid_ds,
            batch_size=self.config.batch_size,
            shuffle=False,
            collate_fn=collate,
            num_workers=0,
            pin_memory=True
        )
        test_loader = DataLoader(
            test_ds,
            batch_size=self.config.batch_size,
            shuffle=False,
            collate_fn=collate,
            num_workers=0,
            pin_memory=True
        )
        
        # Create model
        model = self._create_model().to(self.device)
        
        # Create loss and optimizer
        if self.task_type == 'regression':
            criterion = nn.MSELoss()
        else:
            criterion = nn.CrossEntropyLoss()
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        best_valid_metric = -float('inf')
        best_state = None
        
        for epoch in range(self.config.epochs):
            train_loss, train_acc = self._train_epoch(
                model, train_loader, criterion, optimizer
            )
            valid_metric, valid_mcc = self._evaluate(model, valid_loader)
            
            metric_name = 'Spearman' if self.task_type == 'regression' else 'Acc'
            print(f"Epoch {epoch+1}/{self.config.epochs}: "
                  f"Loss={train_loss:.4f}, Train={train_acc:.4f}, "
                  f"Valid {metric_name}={valid_metric:.4f}, MCC={valid_mcc:.4f}")
            
            if valid_metric > best_valid_metric:
                best_valid_metric = valid_metric
                best_state = model.state_dict().copy()
        
        # Test with best model
        model.load_state_dict(best_state)
        test_metric, test_mcc = self._evaluate(model, test_loader)
        
        print(f"{augmentation_name}: "
              f"Valid {metric_name}={best_valid_metric:.4f}, "
              f"Test {metric_name}={test_metric:.4f}, MCC={test_mcc:.4f}")
        
        # Clear memory
        del model, criterion, optimizer, train_loader, valid_loader, test_loader
        torch.cuda.empty_cache()
        
        # Return results
        result = {
            'augmentation': augmentation_name,
            'magnitude': magnitude,
            'test_mcc': test_mcc
        }
        
        if self.task_type == 'regression':
            result['best_valid_spearman'] = best_valid_metric
            result['test_spearman'] = test_metric
        else:
            result['best_valid_acc'] = best_valid_metric
            result['test_acc'] = test_metric
        
        return result
    
    def _create_model(self):
        """Create appropriate model based on task type"""
        model_type = self.config.model_type
        
        # Get model parameters
        params = self.model_cfg['default_params'].copy()
        
        if self.task_type == 'regression':
            if model_type == 'resnet':
                return ProteinResNetRegression(**params)
            else:  # lstm
                return RegressionModel(**params)
        
        elif self.task_type == 'residue_classification':
            if model_type == 'resnet':
                return ProteinResNetResidue(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
            else:  # lstm
                return ResidueLSTMModel(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
        
        elif self.is_ppi:
            if model_type == 'resnet':
                return ProteinResNetPPI(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
            else:  # lstm
                return PPIModel(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
        
        else:
            if model_type == 'resnet':
                return ProteinResNet(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
            else:  # lstm
                return LSTMModel(
                    num_classes=self.dataset_cfg['num_classes'],
                    **params
                )
    
    def _train_epoch(self, model, loader, criterion, optimizer):
        """Train for one epoch"""
        model.train()
        total_loss = 0
        
        if self.task_type == 'regression':
            for batch in tqdm(loader, desc="Training", leave=False):
                seqs, labels = batch
                seqs, labels = seqs.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(seqs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            return total_loss / len(loader), 0.0
        
        elif self.task_type == 'residue_classification':
            correct, total = 0, 0
            for batch in tqdm(loader, desc="Training", leave=False):
                seqs, (labels, masks) = batch
                seqs = seqs.to(self.device)
                labels, masks = labels.to(self.device), masks.to(self.device)
                
                outputs = model(seqs)
                
                # Flatten and mask
                outputs_flat = outputs.reshape(-1, outputs.size(-1))
                labels_flat = labels.reshape(-1)
                masks_flat = masks.reshape(-1)
                
                outputs_masked = outputs_flat[masks_flat]
                labels_masked = labels_flat[masks_flat]
                
                optimizer.zero_grad()
                loss = criterion(outputs_masked, labels_masked)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                _, predicted = outputs_masked.max(1)
                correct += predicted.eq(labels_masked).sum().item()
                total += labels_masked.size(0)
            
            return total_loss / len(loader), correct / total if total > 0 else 0.0
        
        else:
            correct, total = 0, 0
            for batch in tqdm(loader, desc="Training", leave=False):
                if self.is_ppi:
                    (seqs1, seqs2), labels = batch
                    seqs1, seqs2 = seqs1.to(self.device), seqs2.to(self.device)
                    labels = labels.to(self.device)
                    outputs = model((seqs1, seqs2))
                else:
                    seqs, labels = batch
                    seqs, labels = seqs.to(self.device), labels.to(self.device)
                    outputs = model(seqs)
                
                optimizer.zero_grad()
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                correct += predicted.eq(labels).sum().item()
                total += labels.size(0)
            
            return total_loss / len(loader), correct / total
    
    def _evaluate(self, model, loader):
        """Evaluate model"""
        model.eval()
        
        if self.task_type == 'regression':
            all_preds, all_labels = [], []
            with torch.no_grad():
                for batch in tqdm(loader, desc="Evaluating", leave=False):
                    seqs, labels = batch
                    seqs, labels = seqs.to(self.device), labels.to(self.device)
                    outputs = model(seqs)
                    
                    all_preds.extend(outputs.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())
            
            spearman, _ = spearmanr(all_labels, all_preds)
            return spearman, 0.0
        
        elif self.task_type == 'residue_classification':
            correct, total = 0, 0
            all_preds, all_labels = [], []
            
            with torch.no_grad():
                for batch in tqdm(loader, desc="Evaluating", leave=False):
                    seqs, (labels, masks) = batch
                    seqs = seqs.to(self.device)
                    labels, masks = labels.to(self.device), masks.to(self.device)
                    outputs = model(seqs)
                    
                    outputs_flat = outputs.reshape(-1, outputs.size(-1))
                    labels_flat = labels.reshape(-1)
                    masks_flat = masks.reshape(-1)
                    
                    outputs_masked = outputs_flat[masks_flat]
                    labels_masked = labels_flat[masks_flat]
                    
                    _, predicted = outputs_masked.max(1)
                    correct += predicted.eq(labels_masked).sum().item()
                    total += labels_masked.size(0)
                    
                    all_preds.extend(predicted.cpu().numpy())
                    all_labels.extend(labels_masked.cpu().numpy())
            
            acc = correct / total if total > 0 else 0.0
            mcc = matthews_corrcoef(all_labels, all_preds) if len(set(all_labels)) > 1 else 0.0
            return acc, mcc
        
        else:
            correct, total = 0, 0
            all_preds, all_labels = [], []
            
            with torch.no_grad():
                for batch in tqdm(loader, desc="Evaluating", leave=False):
                    if self.is_ppi:
                        (seqs1, seqs2), labels = batch
                        seqs1, seqs2 = seqs1.to(self.device), seqs2.to(self.device)
                        labels = labels.to(self.device)
                        outputs = model((seqs1, seqs2))
                    else:
                        seqs, labels = batch
                        seqs, labels = seqs.to(self.device), labels.to(self.device)
                        outputs = model(seqs)
                    
                    _, predicted = outputs.max(1)
                    correct += predicted.eq(labels).sum().item()
                    total += labels.size(0)
                    all_preds.extend(predicted.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())
            
            acc = correct / total
            mcc = matthews_corrcoef(all_labels, all_labels) if len(set(all_labels)) > 1 else 0.0
            return acc, mcc
