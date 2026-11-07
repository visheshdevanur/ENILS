"""Convert OGG samples to 16 kHz mono WAV copies (originals are untouched).
Requires ffmpeg on PATH.

Usage: python scripts/convert_ogg_to_wav.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "samples_ogg"
DST = ROOT / "data" / "samples_wav"


def main():
    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.ogg")) + sorted(SRC.glob("*.opus"))
    if not files:
        print(f"No .ogg files in {SRC}")
        return
    for f in files:
        out = DST / (f.stem + ".wav")
        r = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-ar", "16000", "-ac", "1", str(out)]
        )
        print(("OK   " if r.returncode == 0 else "FAIL ") + f.name)
    print(f"Done. Output in {DST}")


if __name__ == "__main__":
    sys.exit(main())
