"""Run the full STT -> LLM -> TTS pipeline on one audio file (no microphone needed).

Usage:
    python scripts/test_file_pipeline.py data/samples_ogg/sample1.ogg
    python scripts/test_file_pipeline.py data/samples_ogg/sample1.ogg --subject math

Saves the spoken answer to outputs/reply.wav and prints a latency report.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import ROOT, load_config  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="path to an .ogg/.wav file with a spoken question")
    ap.add_argument("--subject", default=None, choices=["general", "math", "science", "language"])
    ap.add_argument("--out", default=None, help="output wav (default: outputs/reply_<audio name>.wav)")
    ap.add_argument("--play", action="store_true", help="also play the spoken reply through the speakers")
    args = ap.parse_args()

    cfg = load_config()

    import numpy as np
    import soundfile as sf

    from enils.pipeline.orchestrator import Tutor
    from enils.utils.timing import Timings

    tutor = Tutor(cfg, subject=args.subject)
    print("Warming up models ...")
    tutor.warmup()

    t = Timings()
    with t.stage("stt"):
        text, dur = tutor.stt.transcribe(args.audio)
    print(f"Audio length {dur:.1f}s -> You: {text}")
    if not text:
        print("No speech recognised.")
        return

    reply, chunks, sr = tutor.respond(text, t, player=None)
    if chunks:
        gap = np.zeros(int(sr * 0.25), dtype=np.int16)
        audio = np.concatenate([x for c in chunks for x in (c, gap)])
        out = Path(args.out) if args.out else ROOT / "outputs" / f"reply_{Path(args.audio).stem}.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out), audio, sr)
        print(f"Saved spoken reply: {out}   (open it in any audio player, or re-run with --play)")
        if args.play:
            from enils.audio.playback import Player
            Player(cfg["audio"].get("output_device")).play(audio, sr)
    print(t.report(end_wait_s=cfg["audio"]["silence_ms"] / 1000))


if __name__ == "__main__":
    main()
