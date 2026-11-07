"""Microphone capture with a simple energy-based end-of-speech detector."""
import collections
import queue
import time

import numpy as np
import sounddevice as sd


def _rms(block) -> float:
    return float(np.sqrt(np.mean(np.square(block))))


class Recorder:
    def __init__(self, a: dict):
        self.sr = a["sample_rate"]
        self.block_ms = a["block_ms"]
        self.block = int(self.sr * self.block_ms / 1000)
        self.silence_ms = a["silence_ms"]
        self.min_speech_ms = a["min_speech_ms"]
        self.max_s = a["max_record_s"]
        self.margin = a["energy_margin"]
        self.min_thr = a["min_threshold"]
        self.device = a.get("input_device")
        self.threshold = self.min_thr

    def _stream(self, q):
        def cb(indata, frames, t, status):
            q.put(indata[:, 0].copy())

        return sd.InputStream(
            samplerate=self.sr, channels=1, dtype="float32",
            blocksize=self.block, device=self.device, callback=cb,
        )

    def calibrate(self, seconds=0.8) -> float:
        """Measure ambient noise (stay quiet) and set the speech threshold."""
        q = queue.Queue()
        n = max(3, int(seconds * 1000 / self.block_ms))
        with self._stream(q):
            levels = [_rms(q.get()) for _ in range(n)]
        floor = float(np.median(levels))
        self.threshold = max(self.min_thr, floor * self.margin)
        return floor

    def record_utterance(self, idle_timeout=None):
        """Block until the student speaks and then stops.
        Returns float32 mono audio at sample_rate, or None if nothing valid."""
        q = queue.Queue()
        pre = collections.deque(maxlen=max(1, int(300 / self.block_ms)))  # 300 ms pre-roll
        frames, started = [], False
        silent_blocks = speech_blocks = 0
        t_wait = time.time()
        with self._stream(q):
            while True:
                block = q.get()
                loud = _rms(block) > self.threshold
                if not started:
                    pre.append(block)
                    if loud:
                        started = True
                        frames.extend(pre)
                        speech_blocks = 1
                    elif idle_timeout and time.time() - t_wait > idle_timeout:
                        return None
                else:
                    frames.append(block)
                    if loud:
                        silent_blocks = 0
                        speech_blocks += 1
                    else:
                        silent_blocks += 1
                    if silent_blocks * self.block_ms >= self.silence_ms:
                        break
                    if len(frames) * self.block_ms / 1000 > self.max_s:
                        break
        if speech_blocks * self.block_ms < self.min_speech_ms:
            return None
        return np.concatenate(frames)
