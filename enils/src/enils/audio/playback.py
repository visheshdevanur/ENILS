"""Speaker output."""
import sounddevice as sd


class Player:
    def __init__(self, device=None):
        self.device = device

    def play(self, audio, sample_rate):
        """Blocking playback of an int16/float32 numpy array."""
        sd.play(audio, sample_rate, device=self.device)
        sd.wait()
