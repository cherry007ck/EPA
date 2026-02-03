#!/usr/bin/env python3
"""
Quick EPA Augmentation Test
"""
import sys
import os

# Add EPA to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'epa'))

print("="*70)
print("EPA AUGMENTATION TEST - All 23 Techniques")
print("="*70)

from epa_augmentations import augment_list, random_augment, apply_augment
import random
import numpy as np

# Test 1: List all augmentations
print("\n✓ Loading augmentations...")
augs = augment_list()
print(f"  Total: {len(augs)} augmentations")

print("\n=== CORE (10 from APA) ===")
for i, (fn, low, high) in enumerate(augs[:10], 1):
    print(f"{i:2}. {fn.__name__:35s} ({low:.1f}, {high:.1f})")

print("\n=== SIMPLE ADDITIONS (3) ===")
for i, (fn, low, high) in enumerate(augs[10:13], 11):
    print(f"{i:2}. {fn.__name__:35s} ({low:.1f}, {high:.1f})")

print("\n=== RESEARCH TECHNIQUES (10) ===")
for i, (fn, low, high) in enumerate(augs[13:], 14):
    print(f"{i:2}. {fn.__name__:35s} ({low:.1f}, {high:.1f})")

# Test 2: Test each augmentation
print("\n✓ Testing each augmentation...")
test_seq = list("MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFK")
successful = 0
errors = []

for fn, low, high in augs:
    try:
        aug_seq = fn(test_seq.copy(), 0.15)
        if isinstance(aug_seq, list) and len(aug_seq) > 0:
            successful += 1
        else:
            errors.append(f"{fn.__name__}: returned invalid")
    except Exception as e:
        errors.append(f"{fn.__name__}: {str(e)[:40]}")

print(f"  ✅ Successful: {successful}/{len(augs)}")
if errors:
    print(f"  ❌ Errors: {len(errors)}")
    for err in errors[:5]:
        print(f"     - {err}")

# Test 3: Policy generation
print("\n✓ Testing policy generation...")
random.seed(42)
np.random.seed(42)

policy = []
for _ in range(4):  # 4 sub-policies
    subpolicy = []
    for _ in range(2):  # 2 ops
        op_idx = np.random.randint(len(augs))
        prob = np.random.uniform(0.0, 1.0)
        level = np.random.uniform(0.0, 1.0)
        subpolicy.append((augs[op_idx][0].__name__, prob, level))
    policy.append(subpolicy)

print(f"  Generated {len(policy)} sub-policies")
print(f"  Example: {policy[0]}")

# Test 4: Apply policy
aug_seq = apply_augment(test_seq.copy(), policy)
print(f"  Original: {len(test_seq)} residues")
print(f"  Augmented: {len(aug_seq)} residues")

print("\n" + "="*70)
if successful == len(augs):
    print(f"✅ ALL {len(augs)} AUGMENTATIONS WORKING PERFECTLY!")
else:
    print(f"⚠️  {successful}/{len(augs)} augmentations working")
print("="*70)
