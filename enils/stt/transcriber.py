import logging
from faster_whisper import WhisperModel
from enils.config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE

logger = logging.getLogger("Transcriber")

class Transcriber:
    """
    Handles speech-to-text transcription using the faster-whisper model.
    """

    def __init__(self):
        """
        Initializes the faster-whisper model using configuration settings.
        """
        logger.info(f"Loading STT Model ({WHISPER_MODEL}) on {WHISPER_DEVICE}...")
        try:
            self.model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE_TYPE)
            logger.info("STT Model loaded successfully.")
        except Exception as e:
            logger.exception(f"Failed to load STT Model: {e}")
            raise

    def transcribe(self, audio_data):
        """
        Transcribes audio data (1D numpy array) into text.

        Args:
            audio_data (np.ndarray): 1D numpy array of float32 audio samples.

        Returns:
            str: The transcribed text, stripped of leading/trailing whitespace.
        """
        if audio_data is None or len(audio_data) == 0:
            logger.warning("Empty audio data provided for transcription.")
            return ""

        try:
            # beam_size=1 for faster inference in MVP
            segments, info = self.model.transcribe(audio_data, beam_size=1)
            text = "".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            logger.exception(f"Transcription error: {e}")
            return ""
