"""Offline, low-latency, zero-dependency RAG retriever for ENILS.

Uses BM25 + keyword/formula boosting on indexed chunks.
Supports JSON structured chunks and plain-text/OCR files in data/knowledge/.
Runs completely offline on CPU in <2ms.
"""
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def stem_word(w: str) -> str:
    """Lightweight suffix stemmer for English science terms."""
    w = w.lower()
    for s in ("ing", "tion", "tions", "ed", "es", "s"):
        if w.endswith(s) and len(w) > len(s) + 2:
            return w[:-len(s)]
    return w


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text preserving chemical symbols like CaO, H2O, with stemming."""
    raw = re.findall(r"[A-Za-z0-9\(\)\_\-]+", text.lower())
    tokens = []
    for t in raw:
        if len(t) > 1 or t in ("c", "h", "o", "n", "s", "p", "k"):
            tokens.append(t)
            st = stem_word(t)
            if st != t:
                tokens.append(st)
    return tokens



class OfflineRetriever:
    def __init__(self, knowledge_dir: Path, k1: float = 1.5, b: float = 0.75):
        self.knowledge_dir = Path(knowledge_dir)
        self.k1 = k1
        self.b = b
        self.chunks: List[Dict] = []
        self.corpus_tokens: List[List[str]] = []
        self.doc_lens: List[int] = []
        self.avg_dl: float = 0.0
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.build_index()

    def build_index(self):
        """Load all knowledge chunks from JSON and text/OCR files and build BM25 index."""
        self.chunks = []
        if not self.knowledge_dir.exists():
            return

        # 1. Load any JSON chunk files
        for json_path in sorted(self.knowledge_dir.glob("*.json")):
            try:
                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.chunks.extend(data)
                    elif isinstance(data, dict) and "chunks" in data:
                        self.chunks.extend(data["chunks"])
            except Exception as e:
                print(f"[RAG] Warning loading {json_path}: {e}")

        # 2. Load any plain text / OCR files as additional chunks if not already covered
        for txt_path in sorted(self.knowledge_dir.glob("*.txt")):
            # If it's the raw full text and we already have structured JSON, skip adding full text as a single massive chunk
            if txt_path.name.endswith("_full.txt") and self.chunks:
                continue
            try:
                with open(txt_path, encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    self.chunks.append({
                        "id": txt_path.stem,
                        "title": txt_path.stem.replace("_", " ").title(),
                        "pages": "N/A",
                        "section": "Textbook / OCR",
                        "keywords": [],
                        "text": content,
                    })
            except Exception as e:
                print(f"[RAG] Warning loading {txt_path}: {e}")

        if not self.chunks:
            return

        # 3. Compute corpus frequencies for BM25
        self.corpus_tokens = []
        self.doc_lens = []
        total_len = 0
        df = {}

        for chunk in self.chunks:
            combined_text = f"{chunk.get('title', '')} {' '.join(chunk.get('keywords', []))} {chunk.get('text', '')}"
            tokens = tokenize(combined_text)
            self.corpus_tokens.append(tokens)
            doc_len = len(tokens)
            self.doc_lens.append(doc_len)
            total_len += doc_len

            seen = set(tokens)
            for token in seen:
                df[token] = df.get(token, 0) + 1

        self.df = df
        num_docs = len(self.chunks)
        self.avg_dl = (total_len / num_docs) if num_docs > 0 else 1.0

        # Calculate BM25 IDF
        self.idf = {}
        for token, freq in df.items():
            self.idf[token] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict]:
        """Retrieve top_k most relevant chunks for a user query."""
        if not self.chunks:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores: List[Tuple[float, int]] = []
        q_lower = query.lower()

        for idx, tokens in enumerate(self.corpus_tokens):
            chunk = self.chunks[idx]
            doc_len = self.doc_lens[idx]

            # 1. BM25 score
            score = 0.0
            term_freqs: Dict[str, int] = {}
            for t in tokens:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for qt in q_tokens:
                if qt in term_freqs:
                    tf = term_freqs[qt]
                    idf = self.idf.get(qt, 0.0)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_dl))
                    score += idf * (tf * (self.k1 + 1.0)) / denom

            # 2. Keyword & Title boost using IDF
            title_tokens = set(tokenize(chunk.get("title", "")))
            keywords_text = " ".join(chunk.get("keywords", []))
            keyword_tokens = set(tokenize(keywords_text))

            for qt in q_tokens:
                idf = self.idf.get(qt, 1.0)
                if qt in title_tokens:
                    score += idf * 3.0
                if qt in keyword_tokens:
                    score += idf * 2.0

            # Direct phrase matching boost
            for kw in chunk.get("keywords", []):
                if kw.lower() in q_lower:
                    score += 5.0

            if score >= 1.5:
                scores.append((score, idx))


        scores.sort(key=lambda x: x[0], reverse=True)
        top_indices = [idx for _, idx in scores[:top_k]]
        return [self.chunks[i] for i in top_indices]

    def format_context(self, chunks: List[Dict], max_chars: int = 700) -> str:
        """Format retrieved chunks into a clean, concise prompt context."""
        if not chunks:
            return ""

        context_parts = []
        cur_len = 0
        for c in chunks:
            title = c.get("title", "Section")
            text = c.get("text", "").strip()
            part = f"[{title}]\n{text}"
            if cur_len + len(part) > max_chars and context_parts:
                # Truncate text cleanly if too long for edge context
                remaining = max_chars - cur_len
                if remaining > 100:
                    context_parts.append(f"[{title}]\n{text[:remaining]}...")
                break
            context_parts.append(part)
            cur_len += len(part)

        return "\n\n".join(context_parts)
