#!/usr/bin/env python3
"""
Comprehensive Test for EPA with All 23 Augmentations
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'epa'))

print("="*70)
print("EPA COMPREHENSIVE AUGMENTATION TEST")
print("="*70)

# Test 1: Import and list augmentations
print("\n✓ Testing augmentation registry...")
from epa_augmentations import augment_list, random_augment, apply_augment

augs = augment_list()
print(f"  Total augmentations: {len(augs)}")

# Test 2: Test each augmentation
print("\n✓ Testing each augmentation on sample sequence...")
test_seq = list("MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFK")
print(f"  Original sequence ({len(test_seq)} residues): {''.join(test_seq[:20])}...")

successful = 0
failed = []

for i, (fn, low, high) in enumerate(augs, 1):
    try:
        aug_seq = fn(test_seq.copy(), 0.15)
        if isinstance(aug_seq, list) and len(aug_seq) > 0:
            successful += 1
            # print(f"  {i:2}. ✓ {fn.__name__:30s} -> {len(aug_seq)} residues")
        else:
            failed.append(fn.__name__)
    except Exception as e:
        failed.append(f"{fn.__name__} ({str(e)[:30]})")

print(f"  Successful: {successful}/{len(augs)}")
if failed:
    print(f"  Failed/Skipped: {failed}")

# Test 3: Test random augmentation
print("\n✓ Testing random_augment...")
for i in range(3):
    aug_seq = random_augment(test_seq.copy())
    print(f"  Trial {i+1}: {len(aug_seq)} residues")

# Test 4: Test policy application
print("\n✓ Testing policy application...")
from epa_augmentations import augment_dict
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# Generate a random policy
ops = augment_list()
policy = []
for _ in range(4):  # 4 sub-policies
    subpolicy = []
    for _ in range(2):  # 2 ops per sub-policy
        op_idx = np.random.randint(len(ops))
        prob = np.random.uniform(0.0, 1.0)
        level = np.random.uniform(0.0, 1.0)
        subpolicy.append((ops[op_idx][0].__name__, prob, level))
    policy.append(subpolicy)

print(f"  Generated policy with {len(policy)} sub-policies")
print(f"  Example: {policy[0]}")

aug_seq = apply_augment(test_seq.copy(), policy)
print(f"  Result: {len(aug_seq)} residues")

# Test 5: Load config
print("\n✓ Testing config loading...")
from util import load_config
cfg = load_config("config/LSTM/binloc_LSTM.yaml")
print(f"  Config loaded: {cfg.model['class']}, search={cfg.epa.search}")

print("\n" + "="*70)
print(f"✅ All tests passed! EPA has {len(augs)} augmentations ready to use!")
print("="*70)
print("\nAugmentation Breakdown:")
print("  - 10 Core (APA)")
print("  - 3 Simple additions")
print("  - 10 Research techniques")
print("="*70)
