"""Local LLM via llama-cpp-python (GGUF, CPU only) with sentence streaming."""
import re

_BOUNDARY = re.compile(r"[.!?]\s|\n")
_CLAUSE = re.compile(r"[,;:]\s")


def pop_sentence(buf: str, min_len: int = 15, first: bool = False):
    """Return (sentence, rest) if buf holds a complete sentence, else (None, buf).

    Very short fragments such as '1. ' are not split off.
    first=True also allows a split at a comma/colon once at least ~6 words are
    available, so speech for the FIRST chunk can start sooner."""
    for m in _BOUNDARY.finditer(buf):
        s = buf[: m.end()].strip()
        if len(s) >= min_len:
            return s, buf[m.end():]
    if first:
        for m in _CLAUSE.finditer(buf):
            s = buf[: m.end()].strip()
            if len(s) >= 30 and len(s.split()) >= 6:
                return s, buf[m.end():]
    return None, buf


def clean_for_speech(text: str) -> str:
    """Strip markdown characters that a TTS engine would read out loud."""
    text = re.sub(r"[*_`#>~|]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class LocalLLM:
    def __init__(self, model_path, n_ctx=2048, threads=4, max_tokens=160, temperature=0.4):
        from llama_cpp import Llama

        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=threads,
            n_threads_batch=threads,
            n_gpu_layers=0,  # CPU only
            verbose=False,
        )
        self.max_tokens = max_tokens
        self.temperature = temperature

    def warmup(self, system_text=None):
        """Run one tiny request. Using the real system prompt means its tokens are
        already evaluated, so the first real question skips that work."""
        msgs = []
        if system_text:
            msgs.append({"role": "system", "content": system_text})
        msgs.append({"role": "user", "content": "Hi"})
        self.llm.create_chat_completion(messages=msgs, max_tokens=1)

    def stream_sentences(self, messages, max_sentences=None, early_first=True):
        """Yield the answer in speakable chunks as tokens arrive.

        max_sentences: stop generating after this many full sentences
                       (small models often ignore 'keep it short').
        early_first:   allow the first chunk to end at a comma, to start speaking sooner."""
        buf = ""
        first = True
        n_sent = 0
        stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"].get("content")
            if not delta:
                continue
            buf += delta
            while True:
                sentence, buf = pop_sentence(buf, first=early_first and first)
                if sentence is None:
                    break
                first = False
                yield sentence
                if sentence[-1] in ".!?":
                    n_sent += 1
                if max_sentences and n_sent >= max_sentences:
                    getattr(stream, "close", lambda: None)()
                    return
        tail = buf.strip()
        if tail:
            yield tail
