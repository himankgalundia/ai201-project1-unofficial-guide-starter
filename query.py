"""
Retrieval and generation module.

retrieve(query)  — returns top-k chunks from ChromaDB
ask(question)    — full RAG pipeline: retrieve → prompt → Groq generation
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "gt_cs_unofficial_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
TOP_K = 5
GROQ_MODEL = "llama-3.3-70b-versatile"

# Lazy-loaded singletons so the Gradio app only initialises once
_embedding_model = None
_collection = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return top_k most relevant chunks for the query."""
    model = _get_embedding_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": doc,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "distance": round(dist, 4),
            }
        )
    return chunks


SYSTEM_PROMPT = """You are the Georgia Tech CS Unofficial Guide — a helpful assistant that answers \
student questions about CS courses and professors at Georgia Tech.

IMPORTANT RULES:
1. Answer ONLY using the information provided in the "Retrieved Documents" section below.
2. Do NOT use any general knowledge from your training data about Georgia Tech, courses, or professors.
3. If the retrieved documents do not contain enough information to answer the question, respond with:
   "I don't have enough information in my documents to answer that question."
4. At the end of every answer, list the source documents you drew from under a "Sources:" heading.
5. Be specific and quote or paraphrase the documents directly — do not extrapolate."""


def ask(question: str) -> dict:
    """
    Full RAG pipeline: retrieve relevant chunks, then generate a grounded answer.

    Returns:
        {
            "answer": str,       # LLM response
            "sources": list[str],  # unique source filenames
            "chunks": list[dict],  # raw retrieved chunks
        }
    """
    chunks = retrieve(question)
    sources = list(dict.fromkeys(c["source"] for c in chunks))  # ordered unique

    # Build the context block
    context_parts = []
    for i, c in enumerate(chunks, 1):
        context_parts.append(f"[Document {i} — {c['source']}]\n{c['text']}")
    context = "\n\n".join(context_parts)

    user_message = f"Retrieved Documents:\n\n{context}\n\nStudent Question: {question}"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
        temperature=0.1,
    )

    answer = response.choices[0].message.content
    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    test_questions = [
        "What is the workload like for CS 1301 at Georgia Tech?",
        "What study strategies do students recommend for CS 3510?",
        "How is CS 4641 graded and what does the team project involve?",
    ]
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"\nA: {result['answer']}")
        print(f"\nSources: {result['sources']}")
        print(f"Retrieved chunks (distances): {[c['distance'] for c in result['chunks']]}")
