"""Check speakers and microphone.

Usage:  python scripts/test_audio.py

1. Lists audio devices and the defaults.
2. Plays a short beep           -> you should hear it.
3. Speaks a sentence with Piper -> you should hear a voice.
4. Records 3 seconds from the microphone and prints the level.
   Speak during the recording; a level near 0 means the wrong or muted mic.

If you hear nothing, find the right speaker number in the device list and set
audio.output_device (and audio.input_device) in config/default.yaml.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import load_config, resolve  # noqa: E402


def main():
    cfg = load_config()

    import numpy as np
    import sounddevice as sd

    a = cfg["audio"]
    print("=== Audio devices (number, name, in/out channels) ===")
    print(sd.query_devices())
    print(f"\nSystem defaults (input, output): {sd.default.device}")
    print(f"Config: input_device={a.get('input_device')}  output_device={a.get('output_device')}\n")

    out_dev = a.get("output_device")
    in_dev = a.get("input_device")

    print("[1/3] Playing a beep ...")
    sr = 22050
    t = np.linspace(0, 0.8, int(sr * 0.8), endpoint=False)
    beep = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    sd.play(beep, sr, device=out_dev)
    sd.wait()

    print("[2/3] Speaking with Piper ...")
    from enils.tts.piper_tts import PiperTTS

    tts = PiperTTS(resolve(cfg["tts"]["model_path"]))
    audio, sr = tts.synth("Hello. This is the ENILS speaker test. Can you hear me?")
    print(f"      synthesized {len(audio) / sr:.1f} s of audio at {sr} Hz, peak {int(np.abs(audio).max())} of 32767")
    sd.play(audio, sr, device=out_dev)
    sd.wait()

    print("[3/3] Recording 3 seconds - please speak now ...")
    rec = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype="float32", device=in_dev)
    sd.wait()
    rec = rec[:, 0]
    rms = float(np.sqrt(np.mean(rec ** 2)))
    peak = float(np.abs(rec).max())
    print(f"      mic level: RMS {rms:.4f}, peak {peak:.3f}")
    if peak < 0.01:
        print("      -> almost silent: wrong microphone, muted, or no permission (Windows privacy settings).")
    else:
        print("      -> microphone is picking up sound.")
        print("      Playing your recording back ...")
        sd.play(rec, 16000, device=out_dev)
        sd.wait()
    print("\nDone.")


if __name__ == "__main__":
    main()
