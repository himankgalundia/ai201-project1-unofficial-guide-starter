"""
Embeds all document chunks and stores them in a persistent ChromaDB collection.
Run this once (or re-run whenever your documents change) before using query.py.

Usage:
    python embed.py
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import get_all_chunks

COLLECTION_NAME = "gt_cs_unofficial_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"


def build_vector_store():
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading and chunking documents...")
    chunks = get_all_chunks()
    print(f"  Total chunks: {len(chunks)}")

    texts = [c["text"] for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": c["source"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    print("Generating embeddings (this may take a moment)...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print(f"Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop and recreate so re-runs start fresh
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"  Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )

    print(f"\nDone! Stored {len(chunks)} chunks in collection '{COLLECTION_NAME}'.")
    return collection


if __name__ == "__main__":
    build_vector_store()
