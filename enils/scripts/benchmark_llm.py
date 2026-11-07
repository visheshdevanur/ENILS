"""Benchmark one or more GGUF models: time-to-first-token and generation speed.

Usage:
    python scripts/benchmark_llm.py
    python scripts/benchmark_llm.py --threads 2 4 6 8          # find the best thread count
    python scripts/benchmark_llm.py --model models/llm/other.gguf models/llm/Llama-3.2-1B-Instruct-Q4_K_M.gguf

Reports: TTFT = seconds until the first token, tok/s = generation speed after it.
Roughly, first-sentence delay = TTFT + (about 15 tokens / tok/s).
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import load_config, resolve  # noqa: E402
from enils.llm.prompts import system_prompt  # noqa: E402

QUESTIONS = [
    "What is the difference between speed and velocity?",
    "How do I solve two x plus five equals eleven?",
    "Why is the sky blue?",
]


def run(model_path, threads, n_ctx, max_tokens):
    from llama_cpp import Llama

    t = time.perf_counter()
    llm = Llama(model_path=str(model_path), n_ctx=n_ctx, n_threads=threads,
                n_threads_batch=threads, n_gpu_layers=0, verbose=False)
    load = time.perf_counter() - t
    sysmsg = {"role": "system", "content": system_prompt("general")}
    # warm-up with the real system prompt (as the live pipeline does)
    llm.create_chat_completion(messages=[sysmsg, {"role": "user", "content": "Hi"}], max_tokens=1)

    ttfts, speeds = [], []
    for q in QUESTIONS:
        t0 = time.perf_counter()
        first, n = None, 0
        for ch in llm.create_chat_completion(
            messages=[sysmsg, {"role": "user", "content": q}],
            max_tokens=max_tokens, temperature=0.4, stream=True,
        ):
            if ch["choices"][0]["delta"].get("content"):
                n += 1
                if first is None:
                    first = time.perf_counter() - t0
        total = time.perf_counter() - t0
        if first is not None and n > 1 and total > first:
            ttfts.append(first)
            speeds.append((n - 1) / (total - first))
    avg = lambda x: sum(x) / len(x) if x else 0.0
    print(f"{Path(model_path).name:<45} threads={threads:<3} load={load:5.1f}s  "
          f"TTFT={avg(ttfts):5.2f}s  speed={avg(speeds):5.1f} tok/s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", nargs="+", default=None)
    ap.add_argument("--threads", nargs="+", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=60)
    args = ap.parse_args()

    cfg = load_config()
    models = args.model or [cfg["llm"]["model_path"]]
    threads = args.threads or [cfg.get("cpu_threads", 4)]
    for m in models:
        for th in threads:
            run(resolve(m), th, cfg["llm"]["n_ctx"], args.max_tokens)


if __name__ == "__main__":
    main()
