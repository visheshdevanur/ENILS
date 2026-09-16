import sounddevice as sd
import numpy as np
import time
import logging
from collections import deque
from enils.config import SAMPLE_RATE, CHANNELS, ENERGY_THRESHOLD, SILENCE_DURATION, WAKE_WORD_SNIPPET_SECONDS, MIC_DEVICE_ID, MAX_RECORDING_DURATION

logger = logging.getLogger("MicHandler")

class MicHandler:
    """Handles audio capture from the microphone, including energy detection and recording."""

    def __init__(self):
        """Initializes the MicHandler and opens a persistent audio stream."""
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.device_id = MIC_DEVICE_ID if MIC_DEVICE_ID is not None else 10

        self.buffer_maxlen = int(self.sample_rate * WAKE_WORD_SNIPPET_SECONDS)
        self.buffer = deque(maxlen=self.buffer_maxlen)

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_id
            )
            self.stream.start()
            logger.info(f"MicHandler: Persistent stream opened on device {self.device_id}")
        except Exception as e:
            logger.error(f"Failed to open persistent stream on device {self.device_id}: {e}")
            try:
                self.stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels)
                self.stream.start()
                logger.info("MicHandler: Fallback to system default device successful.")
            except Exception as e2:
                logger.critical(f"Could not open any audio stream: {e2}")
                self.stream = None

    def _get_rms(self, buffer):
        if len(buffer) == 0: return 0
        return np.sqrt(np.mean(buffer**2))

    def _fill_buffer(self, block_duration=0.1):
        if self.stream is None: return
        try:
            frames_to_read = int(self.sample_rate * block_duration)
            data, _ = self.stream.read(frames_to_read)
            if data.ndim > 1:
                audio_data = np.mean(data, axis=1).astype(np.float32)
            else:
                audio_data = data.astype(np.float32)
            self.buffer.extend(audio_data)
        except Exception as e:
            logger.error(f"Error reading from persistent stream: {e}")

    def wait_for_energy_spike(self, threshold=ENERGY_THRESHOLD, block_duration=0.1):
        print("Listening... (Say 'Tutor' or make some noise)")
        while True:
            self._fill_buffer(block_duration)
            if len(self.buffer) < int(self.sample_rate * block_duration):
                continue
            recent_block = list(self.buffer)[-int(self.sample_rate * block_duration):]
            rms = self._get_rms(np.array(recent_block))
            if time.time() % 2 < 0.1:
                print(f"Current Volume Level: {rms:.6f} (Threshold: {threshold})", end="\r")
            if rms > threshold:
                print(f"\nEnergy spike detected: {rms:.6f}")
                return True

    def get_buffered_audio(self):
        return np.array(self.buffer).astype(np.float32)

    def record_duration(self, duration_sec):
        pre_trigger_audio = self.get_buffered_audio()
        print(f"Recording for {duration_sec} seconds...")
        frames_to_read = int(duration_sec * self.sample_rate)
        try:
            data, _ = self.stream.read(frames_to_read)
            if data.ndim > 1:
                new_audio = np.mean(data, axis=1).astype(np.float32)
            else:
                new_audio = data.astype(np.float32)
            return np.concatenate([pre_trigger_audio, new_audio])
        except Exception as e:
            logger.error(f"Error during fixed duration recording: {e}")
            return pre_trigger_audio

    def record_until_silence(self, threshold=ENERGY_THRESHOLD, silence_duration=SILENCE_DURATION, block_duration=0.1):
        pre_trigger_audio = self.get_buffered_audio()
        print("Listening for your question...")
        recorded_frames = []
        silence_start_time = None
        start_time = time.time()

        try:
            while True:
                data, _ = self.stream.read(int(self.sample_rate * block_duration))
                audio_data = np.mean(data, axis=1).astype(np.float32) if data.ndim > 1 else data.astype(np.float32)
                recorded_frames.append(audio_data)

                rms = self._get_rms(audio_data)

                # Fail-safe: stop recording if it exceeds MAX_RECORDING_DURATION
                if time.time() - start_time > MAX_RECORDING_DURATION:
                    print("Max recording duration reached. Processing...")
                    break

                if rms < threshold:
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time >= silence_duration:
                        print("Silence detected, processing query...")
                        break
                else:
                    silence_start_time = None
        except Exception as e:
            logger.error(f"Error during silence recording: {e}")

        return np.concatenate([pre_trigger_audio] + recorded_frames)
