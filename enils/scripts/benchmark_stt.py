"""Benchmark STT speed (and WER if reference transcripts exist).

Usage:
    python scripts/benchmark_stt.py
    python scripts/benchmark_stt.py --model models/whisper/tiny.en
    python scripts/benchmark_stt.py --dir data/samples_ogg --csv data/transcripts.csv

transcripts.csv must have columns:  filename,text
"""
import argparse
import csv
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import ROOT, load_config, resolve  # noqa: E402


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]", " ", s.lower())).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="whisper model dir (default: from config)")
    ap.add_argument("--dir", default="data/samples_ogg")
    ap.add_argument("--csv", default="data/transcripts.csv")
    args = ap.parse_args()

    cfg = load_config()
    from enils.stt.whisper_stt import WhisperSTT

    s = cfg["stt"]
    model_dir = resolve(args.model or s["model_dir"])
    t0 = time.perf_counter()
    stt = WhisperSTT(model_dir, s["compute_type"], cfg.get("cpu_threads", 4),
                     s["beam_size"], s["vad_filter"], cfg.get("language", "en"))
    print(f"Model: {model_dir.name}  (load {time.perf_counter() - t0:.1f}s)")

    files = sorted(p for ext in ("*.ogg", "*.wav", "*.opus") for p in resolve(args.dir).glob(ext))
    if not files:
        print(f"No audio files found in {resolve(args.dir)}")
        return

    refs = {}
    csv_path = resolve(args.csv)
    if csv_path.exists():
        # utf-8-sig drops an Excel/Notepad BOM; skipinitialspace tolerates "a, b" style CSVs
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            reader.fieldnames = [(n or "").strip().lower() for n in reader.fieldnames or []]
            if "filename" not in reader.fieldnames or "text" not in reader.fieldnames:
                sys.exit(f"{csv_path} must have the header: filename,text   (found: {reader.fieldnames})")
            for row in reader:
                if row.get("filename") and row.get("text"):
                    refs[row["filename"].strip()] = row["text"].strip()

    rows, ref_list, hyp_list = [], [], []
    tot_audio = tot_time = 0.0
    for p in files:
        t = time.perf_counter()
        text, dur = stt.transcribe(str(p))
        el = time.perf_counter() - t
        tot_audio += dur
        tot_time += el
        rows.append((p.name, dur, el, el / max(dur, 1e-6), text))
        if p.name in refs:
            ref_list.append(normalize(refs[p.name]))
            hyp_list.append(normalize(text))
        print(f"{p.name:<30} {dur:5.1f}s audio  {el:5.2f}s  RTF {el / max(dur, 1e-6):4.2f}  | {text}")

    print(f"\nFiles: {len(files)}   total audio {tot_audio:.1f}s   decode {tot_time:.1f}s   "
          f"overall RTF {tot_time / max(tot_audio, 1e-6):.2f}  (RTF < 1 is faster than real time)")
    if ref_list:
        import jiwer
        print(f"WER over {len(ref_list)} files with references: {jiwer.wer(ref_list, hyp_list) * 100:.1f}%")
    else:
        print("No matching rows in transcripts.csv, so WER was skipped.")

    out = ROOT / "outputs" / f"stt_benchmark_{model_dir.name}.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "audio_s", "decode_s", "rtf", "hypothesis"])
        w.writerows(rows)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
