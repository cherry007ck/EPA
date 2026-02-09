#!/usr/bin/env python3
"""Quick test script for EPA"""

import sys
import os

# Add epa to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'epa'))

print("="*60)
print("EPA Verification Test")
print("="*60)

# Test 1: Import augmentations
print("\n✓ Testing imports...")
try:
    from epa_augmentations import augment_list, get_augment, random_augment, apply_augment
    print("  [PASS] augmentations module imported")
except Exception as e:
    print(f"  [FAIL] augmentations import: {e}")
    sys.exit(1)

# Test 2: Import util
try:
    from util import load_config, get_root_logger, create_working_directory
    print("  [PASS] util module imported")
except Exception as e:
    print(f"  [FAIL] util import: {e}")
    sys.exit(1)

# Test 3: Check augmentation list
print("\n✓ Testing augmentation registry...")
augs = augment_list()
print(f"  Found {len(augs)} augmentations:")
for fn, low, high in augs:
    print(f"    - {fn.__name__}: ({low}, {high})")

# Test 4: Test random augmentation  
print("\n✓ Testing random augmentation...")
test_seq = list("ACDEFGHIKLMNPQRSTVWY" * 5)
aug_seq = random_augment(test_seq.copy())
print(f"  Original length: {len(test_seq)}")
print(f"  Augmented length: {len(aug_seq)}")
print(f"  [PASS] Augmentation works")

# Test 5: Load config
print("\n✓ Testing config loading...")
try:
    cfg = load_config("config/LSTM/binloc_LSTM.yaml")
    print(f"  Dataset: {cfg.dataset['class']}")
    print(f"  Model: {cfg.model['class']}")
    print(f"  EPA search: {cfg.epa.search}")
    print(f"  Baseline epochs: {cfg.epa.baseline_epochs}")
    print(f"  Policy trials: {cfg.epa.finetune_num}")
    print("  [PASS] Config loaded successfully")
except Exception as e:
    print(f"  [FAIL] Config loading: {e}")
    sys.exit(1)

# Test 6: Test policy generation
print("\n✓ Testing policy generation...")
from epa_augmentations import augment_list
import numpy as np
import random

random.seed(42)
np.random.seed(42)

ops = augment_list()
policy = []
for _ in range(4):  # 4 sub-policies
    subpolicy = []
    for _ in range(2):  # 2 ops
        op_idx = np.random.randint(len(ops))
        prob = np.random.uniform(0.0, 1.0)
        level = np.random.uniform(0.0, 1.0)
        subpolicy.append((ops[op_idx][0].__name__, prob, level))
    policy.append(subpolicy)

print(f"  Generated policy with {len(policy)} sub-policies")
print(f"  Example sub-policy: {policy[0]}")
print("  [PASS] Policy generation works")

# Test 7: Test policy application
print("\n✓ Testing policy application...")
test_seq = list("MKWVTFISLLFLFSSAYS" * 3)
aug_seq = apply_augment(test_seq.copy(), policy)
print(f"  Original: {len(test_seq)} residues")
print(f"  Augmented: {len(aug_seq)} residues")
print("  [PASS] Policy application works")

print("\n" + "="*60)
print("✅ All tests passed! EPA is ready to use.")
print("="*60)
print("\nTo run training:")
print("  python epa/EnhancedProteinAugment.py -c config/LSTM/binloc_LSTM.yaml")
print("="*60)
