"""Offline text-to-speech using Piper (with pyttsx3 fallback on Windows)."""
import os
import tempfile
from pathlib import Path

import numpy as np


class PiperTTS:
    def __init__(self, model_path):
        self.backend = "piper"
        try:
            from piper import PiperVoice

            model_path = Path(model_path)
            config_path = Path(str(model_path) + ".json")
            self.voice = PiperVoice.load(str(model_path), config_path=str(config_path))
        except (ModuleNotFoundError, Exception) as e:
            # Fallback to local pyttsx3 if Piper native phonemizer is missing
            try:
                import pyttsx3

                self.backend = "pyttsx3"
                self.voice = None
            except Exception:
                raise e

    def synth(self, text):
        """Returns (int16 numpy array, sample_rate)."""
        if self.backend == "pyttsx3":
            import pyttsx3
            import soundfile as sf

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            try:
                engine = pyttsx3.init()
                engine.save_to_file(text, tmp_path)
                engine.runAndWait()
                audio, sr = sf.read(tmp_path, dtype="int16")
                return audio, sr
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        v = self.voice
        if hasattr(v, "synthesize_stream_raw"):  # piper-tts 1.2.x
            raw = b"".join(v.synthesize_stream_raw(text))
            return np.frombuffer(raw, dtype=np.int16), v.config.sample_rate
        # piper-tts 1.3+: synthesize() yields AudioChunk objects
        chunks = list(v.synthesize(text))
        if not chunks:
            return np.zeros(0, dtype=np.int16), 22050
        audio = np.concatenate([c.audio_int16_array for c in chunks])
        return audio, chunks[0].sample_rate

