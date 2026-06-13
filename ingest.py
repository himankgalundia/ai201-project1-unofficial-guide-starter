"""
Document ingestion pipeline: loads .txt files from documents/, cleans them,
and splits them into overlapping character-level chunks.
"""

import os
import re

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def load_documents():
    docs = []
    for fname in sorted(os.listdir(DOCUMENTS_DIR)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(DOCUMENTS_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = clean_text(raw)
        if cleaned:
            docs.append({"source": fname, "text": cleaned})
    return docs


def clean_text(text):
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace from each line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if len(chunk) > 50:  # skip near-empty chunks
            chunks.append(chunk)
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def get_all_chunks():
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "chunk_index": i,
            })
    return all_chunks


if __name__ == "__main__":
    chunks = get_all_chunks()
    print(f"Total chunks: {len(chunks)}")
    print("\n--- 5 sample chunks ---")
    import random
    for c in random.sample(chunks, min(5, len(chunks))):
        print(f"\n[Source: {c['source']}, chunk #{c['chunk_index']}]")
        print(c["text"])
        print("-" * 60)
