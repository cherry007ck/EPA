"""
EPA Metrics Module

Simple accuracy and MCC metrics following APA's pattern.
"""

import torch
from sklearn.metrics import matthews_corrcoef as sklearn_mcc


def accuracy(pred, target):
    """
    Classification accuracy.
    
    Args:
        pred (Tensor): prediction of shape (N, C) or (N,)
        target (Tensor): target of shape (N,)
        
    Returns:
        Accuracy score
    """
    if pred.dim() > 1:
        pred = pred.argmax(dim=-1)
    return (pred == target).float().mean().item()


def mcc(pred, target):
    """
    Matthews Correlation Coefficient.
    
    Args:
        pred (Tensor): prediction of shape (N, C) or (N,)
        target (Tensor): target of shape (N,)
        
    Returns:
        MCC score
    """
    if pred.dim() > 1:
        pred = pred.argmax(dim=-1)
    
    pred_np = pred.cpu().numpy()
    target_np = target.cpu().numpy()
    
    return sklearn_mcc(target_np, pred_np)
