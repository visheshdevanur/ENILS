"""Root entrypoint that delegates to enils/run.py."""
import os
import sys
from pathlib import Path

# Add enils/src to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / "enils" / "src"))
os.chdir(str(root_dir / "enils"))

if __name__ == "__main__":
    from enils.main import main
    main()
