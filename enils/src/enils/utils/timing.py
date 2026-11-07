"""Per-turn latency measurement."""
import time
from contextlib import contextmanager


class Timings:
    """Create one instance right after the student stops speaking.

    stage(name): measures the duration of a block.
    mark(name):  records seconds elapsed since this object was created.
    """

    def __init__(self):
        self.t0 = time.perf_counter()
        self.durations = {}
        self.marks = {}

    @contextmanager
    def stage(self, name):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.durations[name] = time.perf_counter() - start

    def mark(self, name):
        # keep only the first mark with a given name
        self.marks.setdefault(name, time.perf_counter() - self.t0)

    def report(self, end_wait_s=0.0, target_s=2.5) -> str:
        lines = ["--- latency (seconds) ---"]
        for k, v in self.durations.items():
            lines.append(f"  {k:<22}{v:6.2f}")
        for k, v in self.marks.items():
            lines.append(f"  {k + ' (at)':<22}{v:6.2f}")
        if "first_audio" in self.marks:
            total = self.marks["first_audio"] + end_wait_s
            flag = "OK" if total <= target_s else "SLOW"
            lines.append(
                f"  perceived latency     {total:6.2f}  [{flag}, target {target_s}s; "
                f"includes {end_wait_s:.2f}s end-of-speech wait]"
            )
        return "\n".join(lines)
