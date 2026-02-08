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
    
    'beta_lactamase': {
        'name': 'Beta-Lactamase Fitness (Regression)',
        'base_dir': 'datasets/beta_lactamase',
        'train_file': 'beta_lactamase_train.lmdb',
        'valid_file': 'beta_lactamase_valid.lmdb',
        'test_file': 'beta_lactamase_test.lmdb',
        'num_classes': 1,  # Regression task
        'task_type': 'regression',
        'label_field': 'scaled_effect1',
        'sequence_field': 'primary',
        'has_single_sequence': True,
        'metric': 'spearman',  # Use Spearman correlation
    },
    
    'secondary_structure': {
        'name': 'Secondary Structure Prediction (3-class per residue)',
        'base_dir': 'datasets/secondary_structure',
        'train_file': 'secondary_structure_train.lmdb',
        'valid_file': 'secondary_structure_valid.lmdb',
        'test_file': 'secondary_structure_casp12.lmdb',  # Use CASP12 as main test
        'num_classes': 3,  # 3 secondary structure classes (helix, sheet, coil)
        'task_type': 'residue_classification',
        'label_field': 'ss3',
        'mask_field': 'valid_mask',
        'sequence_field': 'primary',
        'has_single_sequence': True,
    },
    
    'human_ppi': {
        'name': 'Human Protein-Protein Interaction',
        'base_dir': 'datasets/human_ppi',
        'train_file': 'human_ppi_train.lmdb',
        'valid_file': 'human_ppi_valid.lmdb',
        'test_file': 'human_ppi_test.lmdb',
        'num_classes': 2,
        'task_type': 'classification',
        'label_field': 'interaction',
        'sequence_field': ['primary_1', 'primary_2'],  # Two sequences
        'has_single_sequence': False,
    },
    
    'solubility': {
        'name': 'Protein Solubility Prediction',
        'base_dir': 'datasets/solubility',
        'train_file': 'solubility_train.lmdb',
        'valid_file': 'solubility_valid.lmdb',
        'test_file': 'solubility_test.lmdb',
        'num_classes': 2,
        'task_type': 'classification',
        'label_field': 'solubility',
        'sequence_field': 'primary',
        'has_single_sequence': True,
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
