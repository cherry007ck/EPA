#!/usr/bin/env python3
"""
LSTM Models for EPA Benchmarking
"""

import torch
import torch.nn as nn


class LSTMModel(nn.Module):
    """Simple LSTM model for sequence classification"""
    def __init__(self, num_classes=2, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)  # 20 AAs + padding
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=bidirectional)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.fc = nn.Linear(lstm_output_dim, num_classes)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(self.dropout(x.mean(dim=1)))


class PPIModel(nn.Module):
    """Model for protein-protein interaction (two sequences)"""
    def __init__(self, num_classes=2, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=bidirectional)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.fc = nn.Linear(lstm_output_dim * 2, num_classes)  # Concatenate both sequence representations
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        if isinstance(x, tuple):
            x1, x2 = x
            # Process first sequence
            h1 = self.embedding(x1)
            h1, _ = self.lstm(h1)
            h1 = h1.mean(dim=1)
            
            # Process second sequence
            h2 = self.embedding(x2)
            h2, _ = self.lstm(h2)
            h2 = h2.mean(dim=1)
            
            # Concatenate
            h = torch.cat([h1, h2], dim=1)
            return self.fc(self.dropout(h))
        else:
            # Single sequence fallback
            x = self.embedding(x)
            x, _ = self.lstm(x)
            return self.fc(self.dropout(x.mean(dim=1)))


class RegressionModel(nn.Module):
    """LSTM model for regression tasks (single output value)"""
    def __init__(self, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=bidirectional)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.fc = nn.Linear(lstm_output_dim, 1)  # Single output for regression
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)
        return self.fc(self.dropout(x.mean(dim=1))).squeeze(-1)  # Return shape: (batch_size,)


class ResidueLSTMModel(nn.Module):
    """LSTM model for per-residue classification"""
    def __init__(self, num_classes=3, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True, bidirectional=bidirectional)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.fc = nn.Linear(lstm_output_dim, num_classes)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm(x)  # (batch, seq_len, hidden_dim*2)
        return self.fc(self.dropout(x))  # (batch, seq_len, num_classes)
