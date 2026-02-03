"""
EPA Utility Functions

Configuration loading, logging, and directory management utilities.
"""

import os
import sys
import time
import logging

import yaml
from easydict import EasyDict


def load_config(cfg_file):
    """
    Load YAML configuration file.
    
    Args:
        cfg_file: Path to YAML config file
        
    Returns:
        EasyDict configuration object
    """
    with open(cfg_file, "r") as fin:
        raw_text = fin.read()
    cfg = yaml.load(raw_text, Loader=yaml.CLoader)
    cfg = EasyDict(cfg)
    return cfg


def get_root_logger(file=True):
    """
    Get the root logger with file and console handlers.
    
    Args:
        file: Whether to log to file
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)-10s %(message)s", "%H:%M:%S")
    
    if file:
        handler = logging.FileHandler("log.txt")
        handler.setFormatter(format)
        logger.addHandler(handler)
    
    return logger


def create_working_directory(cfg):
    """
    Create output directory for experiment.
    
    Args:
        cfg: Configuration object
        
    Returns:
        Path to created output directory
    """
    output_dir = os.path.join(
        os.path.expanduser(cfg.output_dir),
        cfg.dataset["class"],
        cfg.model["class"] + "_" + time.strftime("%Y-%m-%d-%H-%M-%S")
    )
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
