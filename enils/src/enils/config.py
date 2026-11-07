"""Configuration loading and path resolution."""
import os
from pathlib import Path

import yaml

# src/enils/config.py -> parents[2] is the project root
ROOT = Path(__file__).resolve().parents[2]


def load_config(path=None) -> dict:
    """Load YAML config. Call this BEFORE importing heavy libraries so that
    force_cpu can hide GPUs from them."""
    path = Path(path) if path else ROOT / "config" / "default.yaml"
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if cfg.get("force_cpu", True):
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    return cfg


def resolve(p) -> Path:
    """Resolve a config path relative to the project root."""
    p = Path(p)
    return p if p.is_absolute() else ROOT / p
