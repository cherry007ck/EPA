"""
Configuration Loader for EPA Benchmarks
Loads and validates configurations from YAML/JSON files
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path



class ConfigLoader:
    """Centralized configuration loader with validation"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_cache = {}
    
    def load_model_config(self, model_type: str, dataset_name: str) -> Dict[str, Any]:
        """
        Load configuration for a specific model-dataset pair
        
        Args:
            model_type: Model type (lstm, random_forest, resnet, esm2)
            dataset_name: Dataset name
            
        Returns:
            Configuration dictionary
        """
        cache_key = f"{model_type}_{dataset_name}"
        
        if cache_key in self.config_cache:
            return self.config_cache[cache_key].copy()
        
        # Try to load specific config file from model subdirectory
        config_filename = f"{model_type}_{dataset_name}.yaml"
        model_dir = self.config_dir / model_type
        config_file = model_dir / config_filename
        
        # Also try flat structure for backward compatibility
        fallback_file = self.config_dir / config_filename
        
        if config_file.exists():
            config = self._load_yaml(config_file)
        elif fallback_file.exists():
            config = self._load_yaml(fallback_file)
        else:
            # Fall back to default config for model type
            default_file = model_dir / f"{model_type}_default.yaml"
            fallback_default = self.config_dir / f"{model_type}_default.yaml"
            
            if default_file.exists():
                config = self._load_yaml(default_file)
            elif fallback_default.exists():
                config = self._load_yaml(fallback_default)
            else:
                raise FileNotFoundError(
                    f"No configuration found for {model_type} on {dataset_name}\n"
                    f"Tried: {config_file}, {fallback_file}"
                )
        
        # Validate configuration
        self._validate_config(config, model_type)
        
        # Cache it
        self.config_cache[cache_key] = config.copy()
        
        return config

    
    def load_all_configs(self, model_type: str) -> Dict[str, Dict[str, Any]]:
        """Load all dataset configurations for a model type"""
        configs = {}
        
        # Try model subdirectory first
        model_dir = self.config_dir / model_type
        pattern = f"{model_type}_*.yaml"
        
        config_files = []
        if model_dir.exists():
            config_files = list(model_dir.glob(pattern))
        
        # Fall back to flat structure
        if not config_files:
            config_files = list(self.config_dir.glob(pattern))
        
        for config_file in config_files:
            # Extract dataset name
            filename = config_file.stem
            if filename == f"{model_type}_default":
                continue
            
            dataset_name = filename.replace(f"{model_type}_", "")
            configs[dataset_name] = self.load_model_config(model_type, dataset_name)
        
        return configs
    
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _validate_config(self, config: Dict[str, Any], model_type: str):
        """Validate configuration structure"""
        required_fields = ['model', 'training', 'dataset']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in configuration")
        
        # Validate model section
        if 'type' not in config['model']:
            raise ValueError("Missing 'type' in model configuration")
        
        if config['model']['type'] != model_type:
            raise ValueError(
                f"Model type mismatch: config says {config['model']['type']}, "
                f"but loading {model_type}"
            )
        
        # Validate training section
        if model_type in ['lstm', 'resnet', 'esm2']:
            required_training = ['epochs', 'batch_size', 'learning_rate']
            for field in required_training:
                if field not in config['training']:
                    raise ValueError(f"Missing '{field}' in training configuration")
        
        return True
    
    def save_config(self, config: Dict[str, Any], model_type: str, 
                   dataset_name: str, overwrite: bool = False):
        """Save configuration to file"""
        config_file = self.config_dir / f"{model_type}_{dataset_name}.yaml"
        
        if config_file.exists() and not overwrite:
            raise FileExistsError(
                f"Configuration already exists: {config_file}\n"
                "Use overwrite=True to replace it"
            )
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Saved configuration to {config_file}")
    
    def list_available_configs(self, model_type: Optional[str] = None) -> List[str]:
        """
        List all available configuration files
        
        Args:
            model_type: Optional filter by model type
            
        Returns:
            List of config names (without .yaml extension)
        """
        config_names = []
        
        if model_type:
            # Check model subdirectory
            model_dir = self.config_dir / model_type
            if model_dir.exists():
                pattern = f"{model_type}_*.yaml"
                configs = sorted(model_dir.glob(pattern))
            else:
                # Fall back to flat structure
                pattern = f"{model_type}_*.yaml"
                configs = sorted(self.config_dir.glob(pattern))
        else:
            # List all configs from all subdirectories
            for subdir in self.config_dir.iterdir():
                if subdir.is_dir():
                    configs = sorted(subdir.glob("*.yaml"))
                    for config_file in configs:
                        if '_default' not in config_file.stem:
                            config_names.append(config_file.stem)
            
            # Also check flat structure
            configs = sorted(self.config_dir.glob("*.yaml"))
            for config_file in configs:
                if '_default' not in config_file.stem and config_file.stem not in config_names:
                    config_names.append(config_file.stem)
            
            return sorted(config_names)
        
        for config_file in configs:
            if '_default' not in config_file.stem:
                config_names.append(config_file.stem)
        
        return config_names
    
    def print_available_configs(self, model_type: Optional[str] = None):
        """
        Print all available configurations (formatted)
        
        Args:
            model_type: Optional filter by model type
        """
        print("\n" + "="*70)
        print("Available Configurations")
        print("="*70)
        
        config_names = self.list_available_configs(model_type)
        
        if not config_names:
            print("No configurations found")
            return
        
        current_model = None
        for filename in config_names:
            parts = filename.split('_', 1)
            if len(parts) == 2:
                model, dataset = parts
                if model != current_model:
                    print(f"\n{model.upper()}:")
                    current_model = model
                print(f"   - {dataset}")
        
        print("="*70 + "\n")


# Global config loader instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def load_config(model_type: str, dataset_name: str) -> Dict[str, Any]:
    """Convenience function to load configuration"""
    loader = get_config_loader()
    return loader.load_model_config(model_type, dataset_name)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuration Loader')
    parser.add_argument('--list', action='store_true',
                       help='List all available configurations')
    parser.add_argument('--model', type=str,
                       help='Filter by model type')
    parser.add_argument('--load', type=str, nargs=2, metavar=('MODEL', 'DATASET'),
                       help='Load and display a configuration')
    args = parser.parse_args()
    
    loader = ConfigLoader()
    
    if args.list:
        loader.print_available_configs(args.model)
    elif args.load:
        model_type, dataset_name = args.load
        config = loader.load_model_config(model_type, dataset_name)
        print(f"\nConfiguration for {model_type} on {dataset_name}:")
        print("="*70)
        print(yaml.dump(config, default_flow_style=False))
    else:
        print("Use --list to see available configurations")
        print("Use --load MODEL DATASET to load a specific configuration")
