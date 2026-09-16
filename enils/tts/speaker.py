import logging
import pyttsx3
from enils.config import TTS_RATE, TTS_VOLUME

logger = logging.getLogger("Speaker")

class Speaker:
    """
    Handles text-to-speech conversion using the pyttsx3 engine.
    """

    def __init__(self):
        """
        Initializes the TTS engine and sets properties for rate and volume.
        """
        logger.info("Initializing TTS Engine...")
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', TTS_RATE)
            self.engine.setProperty('volume', TTS_VOLUME)

            # Set to a pleasant voice if available (usually index 1 on Windows)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)

            logger.info("TTS Engine initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize TTS Engine: {e}")
            self.engine = None

    def speak(self, text):
        """
        Speaks the given text out loud, blocking until finished.

        Args:
            text (str): The text to be spoken.
        """
        if not self.engine:
            logger.error("TTS Engine not initialized. Cannot speak.")
            return

        if not text:
            logger.warning("No text provided to the speaker.")
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.exception(f"TTS playback error: {e}")
