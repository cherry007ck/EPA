#!/usr/bin/env python3
"""
ResNet Models for Protein Sequence Classification
Adapted 1D ResNet architecture for protein sequences
"""

import torch
import torch.nn as nn


class ResidualBlock1D(nn.Module):
    """1D Residual block for sequence data"""
    
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, downsample=None):
        super().__init__()
        
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, 
                               stride=stride, padding=kernel_size//2, bias=False)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size,
                               stride=1, padding=kernel_size//2, bias=False)
        self.bn2 = nn.BatchNorm1d(out_channels)
        
        self.downsample = downsample
        self.stride = stride
    
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
        
        out += identity
        out = self.relu(out)
        
        return out


class ProteinResNet(nn.Module):
    """ResNet for protein sequence classification"""
    
    def __init__(self, num_classes=2, embed_dim=128, channels=[64, 128, 256, 512], 
                 num_blocks=[2, 2, 2, 2], dropout=0.3):
        """
        Args:
            num_classes: Number of output classes
            embed_dim: Embedding dimension for amino acids
            channels: Number of channels in each ResNet stage
            num_blocks: Number of residual blocks in each stage
            dropout: Dropout rate
        """
        super().__init__()
        
        self.embed_dim = embed_dim
        
        # Embedding layer (20 amino acids + padding)
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        
        # Initial convolution
        self.conv1 = nn.Conv1d(embed_dim, channels[0], kernel_size=7, 
                               stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm1d(channels[0])
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        
        # Residual layers
        self.layer1 = self._make_layer(channels[0], channels[0], num_blocks[0])
        self.layer2 = self._make_layer(channels[0], channels[1], num_blocks[1], stride=2)
        self.layer3 = self._make_layer(channels[1], channels[2], num_blocks[2], stride=2)
        self.layer4 = self._make_layer(channels[2], channels[3], num_blocks[3], stride=2)
        
        # Global average pooling
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(channels[3], num_classes)
    
    def _make_layer(self, in_channels, out_channels, num_blocks, stride=1):
        """Create a residual layer with multiple blocks"""
        downsample = None
        if stride != 1 or in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, 
                         stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )
        
        layers = []
        layers.append(ResidualBlock1D(in_channels, out_channels, stride=stride, 
                                      downsample=downsample))
        
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock1D(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        # x: (batch, seq_len) - token indices
        x = self.embedding(x)  # (batch, seq_len, embed_dim)
        x = x.transpose(1, 2)  # (batch, embed_dim, seq_len) for Conv1d
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class ProteinResNetPPI(nn.Module):
    """ResNet for protein-protein interaction (two sequences)"""
    
    def __init__(self, num_classes=2, embed_dim=128, channels=[64, 128, 256, 512],
                 num_blocks=[2, 2, 2, 2], dropout=0.3):
        super().__init__()
        
        # Shared ResNet encoder for both sequences
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        
        # Initial convolution
        self.conv1 = nn.Conv1d(embed_dim, channels[0], kernel_size=7,
                               stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm1d(channels[0])
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        
        # Residual layers (shared)
        self.layer1 = self._make_layer(channels[0], channels[0], num_blocks[0])
        self.layer2 = self._make_layer(channels[0], channels[1], num_blocks[1], stride=2)
        self.layer3 = self._make_layer(channels[1], channels[2], num_blocks[2], stride=2)
        self.layer4 = self._make_layer(channels[2], channels[3], num_blocks[3], stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head (concatenate both sequence representations)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(channels[3] * 2, num_classes)
    
    def _make_layer(self, in_channels, out_channels, num_blocks, stride=1):
        """Create a residual layer"""
        downsample = None
        if stride != 1 or in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1,
                         stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )
        
        layers = []
        layers.append(ResidualBlock1D(in_channels, out_channels, stride=stride,
                                      downsample=downsample))
        
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock1D(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def encode_sequence(self, x):
        """Encode a single sequence"""
        x = self.embedding(x)
        x = x.transpose(1, 2)
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        
        return x
    
    def forward(self, x):
        if isinstance(x, tuple):
            x1, x2 = x
            h1 = self.encode_sequence(x1)
            h2 = self.encode_sequence(x2)
            h = torch.cat([h1, h2], dim=1)
            return self.fc(self.dropout(h))
        else:
            # Single sequence fallback
            h = self.encode_sequence(x)
            # Duplicate features for compatibility
            h = torch.cat([h, h], dim=1)
            return self.fc(self.dropout(h))


class ProteinResNetRegression(nn.Module):
    """ResNet for protein regression tasks"""
    
    def __init__(self, embed_dim=128, channels=[64, 128, 256, 512],
                 num_blocks=[2, 2, 2, 2], dropout=0.3):
        super().__init__()
        
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        
        # Initial convolution
        self.conv1 = nn.Conv1d(embed_dim, channels[0], kernel_size=7,
                               stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm1d(channels[0])
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        
        # Residual layers
        self.layer1 = self._make_layer(channels[0], channels[0], num_blocks[0])
        self.layer2 = self._make_layer(channels[0], channels[1], num_blocks[1], stride=2)
        self.layer3 = self._make_layer(channels[1], channels[2], num_blocks[2], stride=2)
        self.layer4 = self._make_layer(channels[2], channels[3], num_blocks[3], stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        
        # Regression head
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(channels[3], 1)
    
    def _make_layer(self, in_channels, out_channels, num_blocks, stride=1):
        """Create a residual layer"""
        downsample = None
        if stride != 1 or in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1,
                         stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )
        
        layers = []
        layers.append(ResidualBlock1D(in_channels, out_channels, stride=stride,
                                      downsample=downsample))
        
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock1D(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.embedding(x)
        x = x.transpose(1, 2)
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x.squeeze(-1)  # (batch_size,)


class ProteinResNetResidue(nn.Module):
    """ResNet for per-residue classification (e.g., secondary structure)"""
    
    def __init__(self, num_classes=3, embed_dim=128, channels=[64, 128, 256, 128],
                 num_blocks=[2, 2, 2, 2], dropout=0.3):
        """
        Note: For residue-level tasks, we need to preserve sequence length,
        so we use stride=1 and no downsampling
        """
        super().__init__()
        
        self.embedding = nn.Embedding(21, embed_dim, padding_idx=0)
        
        # Initial convolution (no stride to preserve length)
        self.conv1 = nn.Conv1d(embed_dim, channels[0], kernel_size=7,
                               stride=1, padding=3, bias=False)
        self.bn1 = nn.BatchNorm1d(channels[0])
        self.relu = nn.ReLU(inplace=True)
        
        # Residual layers (no downsampling)
        self.layer1 = self._make_layer(channels[0], channels[0], num_blocks[0])
        self.layer2 = self._make_layer(channels[0], channels[1], num_blocks[1])
        self.layer3 = self._make_layer(channels[1], channels[2], num_blocks[2])
        self.layer4 = self._make_layer(channels[2], channels[3], num_blocks[3])
        
        # Per-residue classification
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Conv1d(channels[3], num_classes, kernel_size=1)
    
    def _make_layer(self, in_channels, out_channels, num_blocks, stride=1):
        """Create a residual layer"""
        downsample = None
        if in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, bias=False),
                nn.BatchNorm1d(out_channels)
            )
        
        layers = []
        layers.append(ResidualBlock1D(in_channels, out_channels, stride=1,
                                      downsample=downsample))
        
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock1D(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        # x: (batch, seq_len)
        x = self.embedding(x)  # (batch, seq_len, embed_dim)
        x = x.transpose(1, 2)  # (batch, embed_dim, seq_len)
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.dropout(x)
        x = self.fc(x)  # (batch, num_classes, seq_len)
        
        x = x.transpose(1, 2)  # (batch, seq_len, num_classes)
        
        return x


if __name__ == "__main__":
    # Test ResNet models
    print("Testing ResNet Models for Proteins")
    print("="*70)
    
    batch_size = 4
    seq_len = 100
    
    # Test classification
    print("\n1. Classification ResNet:")
    model = ProteinResNet(num_classes=10)
    x = torch.randint(0, 21, (batch_size, seq_len))
    out = model(x)
    print(f"   Input: {x.shape} -> Output: {out.shape}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test PPI
    print("\n2. PPI ResNet:")
    model_ppi = ProteinResNetPPI(num_classes=2)
    x1 = torch.randint(0, 21, (batch_size, 80))
    x2 = torch.randint(0, 21, (batch_size, 120))
    out = model_ppi((x1, x2))
    print(f"   Input: {x1.shape}, {x2.shape} -> Output: {out.shape}")
    print(f"   Parameters: {sum(p.numel() for p in model_ppi.parameters()):,}")
    
    # Test regression
    print("\n3. Regression ResNet:")
    model_reg = ProteinResNetRegression()
    x = torch.randint(0, 21, (batch_size, seq_len))
    out = model_reg(x)
    print(f"   Input: {x.shape} -> Output: {out.shape}")
    print(f"   Parameters: {sum(p.numel() for p in model_reg.parameters()):,}")
    
    # Test residue-level
    print("\n4. Residue-level ResNet:")
    model_res = ProteinResNetResidue(num_classes=3)
    x = torch.randint(0, 21, (batch_size, seq_len))
    out = model_res(x)
    print(f"   Input: {x.shape} -> Output: {out.shape}")
    print(f"   Parameters: {sum(p.numel() for p in model_res.parameters()):,}")
    
    print("\n" + "="*70)
    print("✅ All ResNet models working correctly!")
