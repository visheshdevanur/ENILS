"""Offline speech-to-text using faster-whisper (CPU, INT8)."""


class WhisperSTT:
    def __init__(self, model_dir, compute_type="int8", cpu_threads=4,
                 beam_size=1, vad_filter=True, language="en"):
        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            str(model_dir),
            device="cpu",
            compute_type=compute_type,
            cpu_threads=cpu_threads,
        )
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.language = language

    def warmup(self):
        """Decode one second of silence so the first real question is not slow."""
        import numpy as np

        segments, _ = self.model.transcribe(
            np.zeros(16000, dtype=np.float32),
            language=self.language, beam_size=1, vad_filter=False,
        )
        list(segments)

    def transcribe(self, audio):
        """audio: path to an audio file (ogg/wav/...) OR float32 numpy array at 16 kHz.
        Returns (text, audio_duration_seconds)."""
        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            beam_size=self.beam_size,
            vad_filter=self.vad_filter,
            condition_on_previous_text=False,
        )
        # segments is a lazy generator: decoding happens while we iterate
        text = " ".join(s.text.strip() for s in segments).strip()
        return text, info.duration
