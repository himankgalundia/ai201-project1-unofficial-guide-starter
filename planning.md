# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Georgia Tech CS course and professor reviews — student-sourced knowledge about courses like CS 1301, CS 1331, CS 1332, CS 2200, CS 3510, and CS 4641. This knowledge is valuable because official course descriptions at GT tell you almost nothing about actual difficulty, workload, exam format, effective study strategies, or which professor to take. The registrar lists a course number, its prerequisites, and a three-sentence catalog description. Students have to find the real information on Rate My Professors, Reddit r/gatech, and word of mouth — scattered across dozens of threads and pages, impossible to search efficiently. A RAG system over this student-generated knowledge makes it directly queryable: "What study strategies work for CS 3510?" gets a grounded answer in seconds instead of an hour of thread-diving.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — CS 1301 | 8 student reviews of CS 1301 (Intro to Computing, Python) | `documents/rmp_cs1301_reviews.txt` |
| 2 | Rate My Professors — CS 1331 | 8 student reviews of CS 1331 (Intro to OOP, Java) | `documents/rmp_cs1331_reviews.txt` |
| 3 | Rate My Professors — CS 1332 | 8 student reviews of CS 1332 (Data Structures & Algorithms) | `documents/rmp_cs1332_reviews.txt` |
| 4 | Rate My Professors — CS 2200 | 8 student reviews of CS 2200 (Systems and Networks) | `documents/rmp_cs2200_reviews.txt` |
| 5 | Rate My Professors — CS 3510 | 8 student reviews of CS 3510 (Design and Analysis of Algorithms) | `documents/rmp_cs3510_reviews.txt` |
| 6 | Rate My Professors — CS 4641 | 8 student reviews of CS 4641 (Machine Learning) | `documents/rmp_cs4641_reviews.txt` |
| 7 | Reddit r/gatech — CS 1301 thread | Community tips and survival advice for CS 1301 | `documents/reddit_cs1301_tips.txt` |
| 8 | Reddit r/gatech — CS 1331 thread | Community tips, debugging advice, and exam strategy for CS 1331 | `documents/reddit_cs1331_tips.txt` |
| 9 | Reddit r/gatech — CS 1332 thread | Community tips for CS 1332, AVL trees, graph algorithms | `documents/reddit_cs1332_tips.txt` |
| 10 | Reddit r/gatech — CS 3510 thread | Study strategies and exam prep for CS 3510 | `documents/reddit_cs3510_study.txt` |
| 11 | Reddit r/gatech — CS 4641 thread | Tips, grading breakdown, and project advice for CS 4641 | `documents/reddit_cs4641_thread.txt` |
| 12 | Reddit r/gatech — CS 2200 thread | CS 2200 project help and debugging tips for C | `documents/reddit_cs2200_thread.txt` |
| 13 | Reddit r/gatech — CS survival guide | General GT CS degree survival guide, tool recommendations, electives | `documents/reddit_gatech_cs_survival.txt` |

Note: Rate My Professors blocks scraping via JavaScript rendering. Reddit API access requires OAuth credentials. Both sources were collected manually — text was copied from browser sessions and saved as plain .txt files. This is explicitly expected per the assignment instructions.

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:** The documents are review-style text — individual student reviews are typically 3–8 sentences (roughly 150–400 characters each). At 500 characters, a single chunk usually captures one full review or a clearly defined sub-topic within a longer Reddit thread. This is large enough to contain a complete, self-contained thought (e.g., "CS 3510 exams require proving algorithm correctness. The median on the midterm was in the 50s. The class is curved at the end.") while being specific enough to match narrow queries. An overlap of 100 characters ensures that if a key piece of information (like a grading breakdown or a specific tip) straddles a chunk boundary, it still appears in at least one retrievable chunk. I experimented with 300-character chunks (too small — individual reviews were fragmented, making retrieval return incomplete context) and 800-character chunks (too large — chunks pulled in multiple unrelated topics, diluting semantic signal). 500 with 100 overlap was the sweet spot for this corpus.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`. Runs fully locally — no API key, no rate limits, no cost per query.

**Top-k:** 5 chunks per query. This gives the LLM enough context to synthesize an answer across multiple reviews without overwhelming it with loosely related material. With 5 chunks of ~500 characters each, the total context is ~2,500 characters — well within `llama-3.3-70b-versatile`'s context window, and compact enough that the model stays focused.

**Production tradeoff reflection:** If deploying for real users and cost wasn't a constraint, I would evaluate:
- **OpenAI `text-embedding-3-large`** (3072 dimensions): much higher accuracy on nuanced similarity than `all-MiniLM-L6-v2` (384 dimensions), but adds per-query API cost and latency from an external call.
- **`intfloat/e5-large-v2`** or **`BAAI/bge-large-en-v1.5`**: stronger local models that outperform MiniLM on benchmarks; tradeoff is higher memory usage and slower inference (~2-4x slower on CPU).
- **Multilingual models** (e.g., `paraphrase-multilingual-MiniLM-L12-v2`): not needed for this English-only corpus, but important for GT's international student population if the domain expanded.
- **Context length**: `all-MiniLM-L6-v2` truncates inputs at 256 tokens (~1,000 chars). At 500-character chunks this is fine, but a production system with longer documents would need a model like `longformer` or a chunking strategy that ensures no chunk exceeds the token limit.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the workload like for CS 1301 at Georgia Tech? | Weekly labs (1–3 hrs each), larger homework projects every few weeks, total ~6–10 hrs/week. Two midterms and one final, all with multiple choice + coding questions. Manageable for beginners who attend class and keep up with labs. |
| 2 | What study strategies do students recommend for CS 3510? | Practice DP problems by formally defining the subproblem, write recurrence, analyze complexity. Use exchange argument for greedy proofs. Do every past exam under timed conditions. Form study groups. Read CLRS. |
| 3 | How is CS 4641 graded and what does the team project involve? | ~35% homework (5 assignments in Python/Jupyter), ~30% team project (proposal + midpoint + final report + 3-min video), ~15% midterm, ~20% final. Team project is groups of 3–4, runs the whole semester, involves applying ML methods to a dataset of your choice. |
| 4 | What programming language is used in CS 1332 and how hard is it compared to CS 1331? | Java (continuation of CS 1331). Significantly harder — covers data structures from arrays to graphs with ~100 autograder test cases per assignment. The AVL tree assignment is widely considered the hardest. Known retrieval challenge: generic phrasing pulls CS 2200 chunks instead of CS 1332 chunks — see failure case in README. |
| 5 | What resources do students recommend for debugging Java in CS 1331? | Use IntelliJ IDEA (better error highlighting than Eclipse), read the stack trace (first line gives exception type and line number), use IntelliJ's debugger instead of print statements, attend TA debugging office hours. Retrieval partially affected by same issue as Q4. |

---

## Anticipated Challenges

1. **Key facts split across chunk boundaries.** The 500-character fixed-size chunker does not respect sentence or review boundaries — it splits by character count. A grading breakdown like "35% homework, 30% project, 15% midterm, 20% final" could be split across two chunks, meaning neither chunk alone answers "how is the course graded?" The 100-character overlap mitigates this but doesn't eliminate it. A more robust solution would be to split by paragraph or by individual review block, which would respect the natural document structure better.

2. **Source ambiguity and attribution errors.** Several documents discuss similar topics (e.g., CS 3510 difficulty appears in both `rmp_cs3510_reviews.txt` and `reddit_cs3510_study.txt`). When the retriever pulls chunks from multiple files for the same query, the LLM may blend information from both without clearly distinguishing which claim came from which source. This could produce source citations that don't precisely map to the quoted content. The mitigation is to label each document block in the context passed to the LLM, which is implemented in `query.py`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     OFFLINE (run once)                          │
│                                                                 │
│  documents/*.txt                                                │
│       │                                                         │
│       ▼                                                         │
│  [Document Ingestion]   ingest.py                               │
│  load_documents()       - Reads all .txt files                  │
│  clean_text()           - Collapses blank lines, strips spaces  │
│       │                                                         │
│       ▼                                                         │
│  [Chunking]             ingest.py                               │
│  chunk_text()           - 500-char chunks, 100-char overlap     │
│       │                                                         │
│       ▼                                                         │
│  [Embedding]            embed.py                                │
│  SentenceTransformer    - all-MiniLM-L6-v2 (local)             │
│       │                                                         │
│       ▼                                                         │
│  [Vector Store]         ChromaDB (./chroma_db/)                 │
│  PersistentClient       - cosine similarity, metadata stored    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ONLINE (per query)                          │
│                                                                 │
│  User query (via Gradio or CLI)                                 │
│       │                                                         │
│       ▼                                                         │
│  [Retrieval]            query.py → retrieve()                   │
│  SentenceTransformer    - embed query with all-MiniLM-L6-v2     │
│  ChromaDB.query()       - top-5 chunks by cosine similarity     │
│       │                                                         │
│       ▼                                                         │
│  [Generation]           query.py → ask()                        │
│  Groq API               - llama-3.3-70b-versatile               │
│  System prompt          - "answer ONLY from retrieved docs"     │
│       │                                                         │
│       ▼                                                         │
│  Answer + Sources → Gradio UI (app.py)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude my Documents section (13 .txt files, review/forum text) and my Chunking Strategy section (500 chars, 100 overlap, reason: short review corpus). I will ask Claude to implement `ingest.py` with `load_documents()`, `clean_text()`, and `chunk_text()` functions. I will verify the output by running `python ingest.py` and inspecting 5 printed sample chunks — if any contain blank chunks, HTML artifacts, or are clearly too small/large, I will adjust the chunk size or cleaning logic.

**Milestone 4 — Embedding and retrieval:**
I will give Claude my Retrieval Approach section (all-MiniLM-L6-v2, top-5, ChromaDB cosine) and the architecture diagram. I will ask Claude to implement `embed.py` (build the vector store) and the `retrieve()` function in `query.py`. I will verify by running 3 test queries from my evaluation plan and checking that returned chunks visibly relate to each query and have cosine distances below 0.5.

**Milestone 5 — Generation and interface:**
I will give Claude my grounding requirement (answer from retrieved docs only, cite sources explicitly), the SYSTEM_PROMPT design, and the Gradio structure requirement (question input, answer output, sources output). I will ask Claude to implement `ask()` in `query.py` and the full `app.py` Gradio interface. I will verify by running the app, testing all 5 evaluation questions, and testing one out-of-scope question to confirm the system refuses rather than hallucinating.
