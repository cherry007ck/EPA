"""
Dataset Configuration for EPA
Defines properties for each dataset type
"""

DATASET_CONFIGS = {
    'subcellular_localization': {
        'name': 'Subcellular Localization (10-class)',
        'base_dir': 'datasets/subcellular_localization',
        'train_file': 'subcellular_localization_train.lmdb',
        'valid_file': 'subcellular_localization_valid.lmdb',
        'test_file': 'subcellular_localization_test.lmdb',
        'num_classes': 10,
        'task_type': 'classification',
        'label_field': 'localization',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'subcellular_localization_2': {
        'name': 'Subcellular Localization Binary',
        'base_dir': 'datasets/subcellular_localization_2',
        'train_file': 'subcellular_localization_2_train.lmdb',
        'valid_file': 'subcellular_localization_2_valid.lmdb',
        'test_file': 'subcellular_localization_2_test.lmdb',
        'num_classes': 2,
        'task_type': 'classification',
        'label_field': 'localization',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'remote_homology_fold': {
        'name': 'Remote Homology (Fold prediction)',
        'base_dir': 'datasets/remote_homology',
        'train_file': 'remote_homology_train.lmdb',
        'valid_file': 'remote_homology_valid.lmdb',
        'test_file': 'remote_homology_test_fold_holdout.lmdb',
        'num_classes': 1195,  # Will be determined at runtime
        'task_type': 'classification',
        'label_field': 'fold_label',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'remote_homology_family': {
        'name': 'Remote Homology (Family prediction)',
        'base_dir': 'datasets/remote_homology',
        'train_file': 'remote_homology_train.lmdb',
        'valid_file': 'remote_homology_valid.lmdb',
        'test_file': 'remote_homology_test_family_holdout.lmdb',
        'num_classes': 4254,  # Will be determined at runtime
        'task_type': 'classification',
        'label_field': 'family_label',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'remote_homology_superfamily': {
        'name': 'Remote Homology (Superfamily prediction)',
        'base_dir': 'datasets/remote_homology',
        'train_file': 'remote_homology_train.lmdb',
        'valid_file': 'remote_homology_valid.lmdb',
        'test_file': 'remote_homology_test_superfamily_holdout.lmdb',
        'num_classes': 2056,  # Will be determined at runtime
        'task_type': 'classification',
        'label_field': 'superfamily_label',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'yeast_ppi': {
        'name': 'Yeast Protein-Protein Interaction',
        'base_dir': 'datasets/yeast_ppi',
        'train_file': 'yeast_ppi_train.lmdb',
        'valid_file': 'yeast_ppi_valid.lmdb',
        'test_file': 'yeast_ppi_test.lmdb',
        'num_classes': 2,
        'task_type': 'classification',
        'label_field': 'interaction',
        'sequence_field': ['primary_1', 'primary_2'],  # Two sequences
        'has_single_sequence': False,
    },
}


def get_dataset_config(dataset_name):
    """Get configuration for a specific dataset"""
    if dataset_name not in DATASET_CONFIGS:
        raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(DATASET_CONFIGS.keys())}")
    return DATASET_CONFIGS[dataset_name]


def list_available_datasets():
    """List all available datasets"""
    print("Available datasets:")
    for key, config in DATASET_CONFIGS.items():
        print(f"  - {key}: {config['name']} ({config['num_classes']} classes)")
