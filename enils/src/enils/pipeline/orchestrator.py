"""Tutor pipeline: STT -> LLM (streamed by sentence) -> TTS -> playback.

LLM, TTS and playback run on separate threads connected by queues, so speech
for sentence 1 plays while sentence 2 is still being generated.
"""
import queue
import threading

from enils.config import resolve
from enils.llm.client import LocalLLM, clean_for_speech
from enils.llm.prompts import system_prompt
from enils.stt.whisper_stt import WhisperSTT
from enils.tts.piper_tts import PiperTTS


class Tutor:
    def __init__(self, cfg: dict, subject=None):
        threads = cfg.get("cpu_threads", 4)
        self.cfg = cfg
        self.subject = subject or cfg["tutor"]["subject"]
        self.history = []  # list of {"role": ..., "content": ...}
        self.max_history = cfg["llm"]["history_turns"] * 2

        print("Loading STT ...")
        s = cfg["stt"]
        self.stt = WhisperSTT(
            resolve(s["model_dir"]), s["compute_type"], threads,
            s["beam_size"], s["vad_filter"], cfg.get("language", "en"),
        )
        print("Loading LLM ...")
        l = cfg["llm"]
        self.llm = LocalLLM(
            resolve(l["model_path"]), l["n_ctx"], threads, l["max_tokens"], l["temperature"]
        )
        print("Loading TTS ...")
        self.tts = PiperTTS(resolve(cfg["tts"]["model_path"]))

        # Offline RAG Knowledge Retriever
        self.rag_enabled = cfg.get("rag", {}).get("enabled", False)
        self.retriever = None
        self.last_rag_sources = []
        if self.rag_enabled:
            from enils.rag.retriever import OfflineRetriever
            k_dir = resolve(cfg.get("rag", {}).get("knowledge_dir", "data/knowledge"))
            self.retriever = OfflineRetriever(k_dir)
            print(f"Loaded Offline RAG ({len(self.retriever.chunks)} knowledge chunks) from {k_dir}")

    def warmup(self):
        """Run each model once so the first real question is not slow."""
        self.stt.warmup()
        self.llm.warmup(system_prompt(self.subject))
        self.tts.synth("Ready.")

    def respond(self, user_text, timings, player=None):
        """Generate and speak (or just collect) the answer.

        player=None -> audio is collected and returned instead of played
        (used by the file test script).
        Returns (reply_text, list_of_int16_arrays, sample_rate)."""
        context = None
        self.last_rag_sources = []
        if self.rag_enabled and self.retriever:
            with timings.stage("rag"):
                top_k = self.cfg.get("rag", {}).get("top_k", 2)
                max_chars = self.cfg.get("rag", {}).get("max_context_chars", 700)
                matched = self.retriever.retrieve(user_text, top_k=top_k)
                if matched:
                    context = self.retriever.format_context(matched, max_chars=max_chars)
                    self.last_rag_sources = [c.get("title", "") for c in matched]
                    print(f"[RAG Knowledge: {', '.join(self.last_rag_sources)}]")


        messages = (
            [{"role": "system", "content": system_prompt(self.subject, context=context)}]
            + self.history
            + [{"role": "user", "content": user_text}]
        )
        sent_q, audio_q = queue.Queue(), queue.Queue()
        collected, sr_holder = [], [22050]


        def tts_worker():
            while True:
                sentence = sent_q.get()
                if sentence is None:
                    audio_q.put(None)
                    return
                audio, sr = self.tts.synth(sentence)
                audio_q.put((audio, sr))

        def play_worker():
            while True:
                item = audio_q.get()
                if item is None:
                    return
                audio, sr = item
                sr_holder[0] = sr
                timings.mark("first_audio")
                if player is not None:
                    player.play(audio, sr)
                else:
                    collected.append(audio)

        t_tts = threading.Thread(target=tts_worker, daemon=True)
        t_play = threading.Thread(target=play_worker, daemon=True)
        t_tts.start()
        t_play.start()

        parts = []
        max_sent = self.cfg["llm"].get("max_sentences", 3)
        for sentence in self.llm.stream_sentences(messages, max_sentences=max_sent):
            timings.mark("llm_first_sentence")
            print(f"Tutor: {sentence}")
            parts.append(sentence)
            spoken = clean_for_speech(sentence)
            if spoken:
                sent_q.put(spoken)
        timings.mark("llm_done")
        sent_q.put(None)
        t_tts.join()
        t_play.join()

        reply = " ".join(parts)
        self.history += [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": reply},
        ]
        self.history = self.history[-self.max_history:]
        return reply, collected, sr_holder[0]
