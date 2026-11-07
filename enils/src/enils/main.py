"""Live voice loop: listen -> transcribe -> think -> speak."""
import argparse


def main():
    ap = argparse.ArgumentParser(description="ENILS offline voice tutor")
    ap.add_argument("--config", default=None, help="path to a YAML config")
    ap.add_argument("--subject", default=None, choices=["general", "math", "science", "language"])
    ap.add_argument("--ptt", action="store_true", help="push-to-talk: press Enter before each question")
    args = ap.parse_args()

    # config first: it hides GPUs before heavy libraries are imported
    from enils.config import load_config
    cfg = load_config(args.config)

    from enils.audio.capture import Recorder
    from enils.audio.playback import Player
    from enils.pipeline.orchestrator import Tutor
    from enils.utils.timing import Timings

    tutor = Tutor(cfg, subject=args.subject)
    print("Warming up models ...")
    tutor.warmup()

    rec = Recorder(cfg["audio"])
    player = Player(cfg["audio"].get("output_device"))
    print("Calibrating microphone - please stay quiet for a moment ...")
    floor = rec.calibrate()
    print(f"Noise floor {floor:.4f}, speech threshold {rec.threshold:.4f}")
    print(f"Subject: {tutor.subject}. Press Ctrl+C to quit.")

    try:
        while True:
            if args.ptt:
                input("\nPress Enter, then ask your question ... ")
            else:
                print("\nListening ...")
            audio = rec.record_utterance()
            if audio is None:
                continue
            t = Timings()  # clock starts when the student stops speaking
            with t.stage("stt"):
                text, _ = tutor.stt.transcribe(audio)
            if not text:
                continue
            print(f"You: {text}")
            reply, _, _ = tutor.respond(text, t, player=player)
            print(t.report(end_wait_s=cfg["audio"]["silence_ms"] / 1000))

            # Automatically log turn to Excel and CSV
            try:
                from enils.config import ROOT
                from enils.utils.excel_logger import log_turn
                lat = (t.marks.get("first_audio", 0) + cfg["audio"]["silence_ms"] / 1000) if "first_audio" in t.marks else None
                log_turn(
                    output_dir=ROOT / "outputs",
                    question=text,
                    tutor_reply=reply,
                    rag_sources=getattr(tutor, "last_rag_sources", []),
                    latency_s=lat,
                )
            except Exception:
                pass
    except KeyboardInterrupt:

        print("\nGoodbye!")


if __name__ == "__main__":
    main()
