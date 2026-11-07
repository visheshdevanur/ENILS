"""Verify that all model files named in config/default.yaml exist.
Usage: python scripts/check_models.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import load_config, resolve  # noqa: E402


def size_mb(p: Path) -> str:
    return f"{p.stat().st_size / 1e6:,.1f} MB"


def main():
    cfg = load_config()
    ok = True

    wdir = resolve(cfg["stt"]["model_dir"])
    for name in ("model.bin", "config.json"):
        p = wdir / name
        good = p.exists()
        ok &= good
        print(f"[{'OK' if good else 'MISSING'}] STT  {p}" + (f"  ({size_mb(p)})" if good else ""))

    llm = resolve(cfg["llm"]["model_path"])
    good = llm.exists()
    ok &= good
    print(f"[{'OK' if good else 'MISSING'}] LLM  {llm}" + (f"  ({size_mb(llm)})" if good else ""))

    onnx = resolve(cfg["tts"]["model_path"])
    js = Path(str(onnx) + ".json")
    for p in (onnx, js):
        good = p.exists()
        ok &= good
        print(f"[{'OK' if good else 'MISSING'}] TTS  {p}" + (f"  ({size_mb(p)})" if good else ""))

    print("\nAll model files found." if ok else "\nSome files are missing - see README.md for download links.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
