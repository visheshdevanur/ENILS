"""Calculate Cosine Similarity and BERTScore between Tutor Output and Expected Answer and save to Excel.

Usage:
    python scripts/update_cosine_column.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.compute_evaluation_metrics import main

if __name__ == "__main__":
    main()
