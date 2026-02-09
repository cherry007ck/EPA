#!/usr/bin/env python3
"""
Random Forest Models for EPA Benchmarking
Uses sklearn's RandomForest with protein sequence features
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler


class ProteinFeatureExtractor:
    """Extract features from protein sequences for traditional ML models"""
    
    def __init__(self):
        self.amino_acids = "ACDEFGHIKLMNPQRSTVWY"
        self.aa_to_idx = {aa: i for i, aa in enumerate(self.amino_acids)}
    
    def extract_features(self, sequences):
        """
        Extract multiple feature types from protein sequences
        
        Features:
        - Amino acid composition (20 features)
        - Sequence length (1 feature)
        - Dipeptide composition (400 features) - optional, can be large
        - Basic physicochemical properties (5 features)
        """
        features = []
        
        for seq in sequences:
            feat = []
            
            # 1. Amino acid composition (20 features)
            aa_count = np.zeros(20)
            for aa in seq:
                if aa in self.aa_to_idx:
                    aa_count[self.aa_to_idx[aa]] += 1
            aa_comp = aa_count / max(len(seq), 1)  # Normalize
            feat.extend(aa_comp)
            
            # 2. Sequence length (1 feature)
            feat.append(len(seq))
            
            # 3. Basic physicochemical properties
            # Hydrophobic: A, V, I, L, M, F, Y, W
            # Polar: S, T, N, Q
            # Charged: R, K, D, E, H
            # Special: C, G, P
            hydrophobic = sum(1 for aa in seq if aa in 'AVILMFYW')
            polar = sum(1 for aa in seq if aa in 'STNQ')
            charged = sum(1 for aa in seq if aa in 'RKDEH')
            special = sum(1 for aa in seq if aa in 'CGP')
            
            feat.append(hydrophobic / max(len(seq), 1))
            feat.append(polar / max(len(seq), 1))
            feat.append(charged / max(len(seq), 1))
            feat.append(special / max(len(seq), 1))
            
            features.append(feat)
        
        return np.array(features)


class RandomForestModel:
    """
    Random Forest wrapper for protein classification/regression
    Works with both single sequences and PPI tasks
    """
    
    def __init__(self, task_type='classification', n_estimators=100, max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, n_jobs=-1, random_state=42):
        self.task_type = task_type
        self.feature_extractor = ProteinFeatureExtractor()
        self.scaler = StandardScaler()
        
        # Choose appropriate sklearn model
        if task_type == 'regression':
            self.model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                n_jobs=n_jobs,
                random_state=random_state
            )
        else:  # classification
            self.model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                n_jobs=n_jobs,
                random_state=random_state
            )
    
    def prepare_features(self, sequences, is_ppi=False):
        """Extract and scale features from sequences"""
        if is_ppi:
            # For PPI: concatenate features from both sequences
            seqs1, seqs2 = sequences
            feat1 = self.feature_extractor.extract_features(seqs1)
            feat2 = self.feature_extractor.extract_features(seqs2)
            features = np.concatenate([feat1, feat2], axis=1)
        else:
            # Single sequence
            features = self.feature_extractor.extract_features(sequences)
        
        return features
    
    def fit(self, sequences, labels, is_ppi=False):
        """Train the Random Forest model"""
        # Extract features
        X = self.prepare_features(sequences, is_ppi)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X, labels)
        
        return self
    
    def predict(self, sequences, is_ppi=False):
        """Make predictions"""
        # Extract features
        X = self.prepare_features(sequences, is_ppi)
        
        # Scale features
        X = self.scaler.transform(X)
        
        # Predict
        return self.model.predict(X)
    
    def predict_proba(self, sequences, is_ppi=False):
        """Get prediction probabilities (classification only)"""
        if self.task_type != 'classification':
            raise ValueError("predict_proba only available for classification tasks")
        
        # Extract features
        X = self.prepare_features(sequences, is_ppi)
        
        # Scale features
        X = self.scaler.transform(X)
        
        # Predict probabilities
        return self.model.predict_proba(X)
    
    def feature_importance(self):
        """Get feature importances"""
        return self.model.feature_importances_


if __name__ == "__main__":
    # Test feature extraction
    print("Testing Random Forest Model for Proteins")
    print("="*60)
    
    extractor = ProteinFeatureExtractor()
    test_seqs = ["ACDEFGHIKLMNPQRSTVWY", "AAAAA", "GGGGG"]
    features = extractor.extract_features(test_seqs)
    
    print(f"Test sequences: {len(test_seqs)}")
    print(f"Feature shape: {features.shape}")
    print(f"Feature count per sequence: {features.shape[1]}")
    print("\nFeature breakdown:")
    print("  - Amino acid composition: 20")
    print("  - Sequence length: 1")
    print("  - Physicochemical properties: 4")
    print(f"  - Total: {features.shape[1]}")
    print("="*60)
