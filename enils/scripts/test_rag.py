"""Test the offline RAG system with sample questions from Class 10 Science Chapter 1.

Usage:
    python scripts/test_rag.py
    python scripts/test_rag.py "Why are chips packets flushed with nitrogen?"
"""
import argparse
import sys
import time
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enils.config import load_config, resolve
from enils.rag.retriever import OfflineRetriever
from enils.llm.client import LocalLLM
from enils.llm.prompts import system_prompt

TEST_QUESTIONS = [
    "What is a combination reaction?",
    "Why should a magnesium ribbon be cleaned before burning in air?",
    "Why are chips bags flushed with nitrogen gas?",
    "What is rancidity and how can it be prevented?",
    "Why does an iron nail turn brown in copper sulphate solution?"
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=None, help="Optional custom question")
    args = ap.parse_args()

    cfg = load_config()
    k_dir = resolve(cfg.get("rag", {}).get("knowledge_dir", "data/knowledge"))
    print(f"Loading Offline RAG from {k_dir} ...")
    retriever = OfflineRetriever(k_dir)
    print(f"Loaded {len(retriever.chunks)} knowledge chunks from textbook.")

    print("\nLoading Local LLM (CPU) ...")
    l_cfg = cfg["llm"]
    llm = LocalLLM(
        resolve(l_cfg["model_path"]),
        l_cfg["n_ctx"],
        cfg.get("cpu_threads", 4),
        l_cfg["max_tokens"],
        l_cfg["temperature"]
    )
    llm.warmup(system_prompt("science"))
    print("LLM Ready!\n" + "=" * 60)

    queries = [args.query] if args.query else TEST_QUESTIONS

    for q in queries:
        print(f"\n[Question]: {q}")
        t0 = time.perf_counter()
        matched = retriever.retrieve(q, top_k=2)
        retrieval_ms = (time.perf_counter() - t0) * 1000

        titles = [m.get("title", "") for m in matched]
        print(f"[RAG Retrieved in {retrieval_ms:.2f}ms]: {', '.join(titles)}")

        context = retriever.format_context(matched, max_chars=cfg.get("rag", {}).get("max_context_chars", 700))
        sys_p = system_prompt("science", context=context)
        messages = [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": q}
        ]

        t_gen = time.perf_counter()
        sentences = list(llm.stream_sentences(messages, max_sentences=3))
        gen_s = time.perf_counter() - t_gen

        reply = " ".join(sentences)
        print(f"[Tutor Answer ({gen_s:.2f}s)]:\n{reply}")
        print("-" * 60)

        # Log turn to Excel
        try:
            from enils.config import ROOT
            from enils.utils.excel_logger import log_turn
            log_turn(
                output_dir=ROOT / "outputs",
                question=q,
                tutor_reply=reply,
                rag_sources=titles,
                latency_s=gen_s,
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
