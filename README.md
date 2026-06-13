# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**Georgia Tech CS Course and Professor Reviews**

This system covers student-sourced knowledge about Georgia Tech's core CS courses: CS 1301 (Intro to Computing), CS 1331 (OOP in Java), CS 1332 (Data Structures), CS 2200 (Systems and Networks), CS 3510 (Algorithms), and CS 4641 (Machine Learning).

This knowledge is valuable because official GT sources — the registrar, course catalog, and department pages — describe what a course covers but say almost nothing about actual difficulty, workload, effective study strategies, exam format, or which professor to choose. Students piece this together from Rate My Professors reviews, Reddit threads on r/gatech, and word of mouth. The problem is that this information is fragmented across dozens of pages and threads, making it slow and unreliable to search. A RAG system over this corpus makes specific, verifiable student knowledge directly queryable in seconds.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — CS 1301 | RMP reviews (manually collected) | `documents/rmp_cs1301_reviews.txt` |
| 2 | Rate My Professors — CS 1331 | RMP reviews (manually collected) | `documents/rmp_cs1331_reviews.txt` |
| 3 | Rate My Professors — CS 1332 | RMP reviews (manually collected) | `documents/rmp_cs1332_reviews.txt` |
| 4 | Rate My Professors — CS 2200 | RMP reviews (manually collected) | `documents/rmp_cs2200_reviews.txt` |
| 5 | Rate My Professors — CS 3510 | RMP reviews (manually collected) | `documents/rmp_cs3510_reviews.txt` |
| 6 | Rate My Professors — CS 4641 | RMP reviews (manually collected) | `documents/rmp_cs4641_reviews.txt` |
| 7 | Reddit r/gatech — CS 1301 tips thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs1301_tips.txt` |
| 8 | Reddit r/gatech — CS 1331 tips thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs1331_tips.txt` |
| 9 | Reddit r/gatech — CS 1332 tips thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs1332_tips.txt` |
| 10 | Reddit r/gatech — CS 3510 study thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs3510_study.txt` |
| 11 | Reddit r/gatech — CS 4641 thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs4641_thread.txt` |
| 12 | Reddit r/gatech — CS 2200 project thread | Reddit Q&A thread (manually collected) | `documents/reddit_cs2200_thread.txt` |
| 13 | Reddit r/gatech — CS survival guide | Reddit long-form guide (manually collected) | `documents/reddit_gatech_cs_survival.txt` |

**Collection method note:** Rate My Professors blocks programmatic access due to JavaScript rendering. Reddit's API requires OAuth credentials and has strict rate limits. Both sources were collected manually — text was copied from browser sessions and saved as plain `.txt` files, as described in the assignment instructions as a normal and expected approach.

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:**
The corpus is made up of short review-style text — individual student reviews run 150–400 characters (3–8 sentences), and Reddit comments run 200–600 characters. A 500-character chunk captures one complete review or a coherent sub-section of a longer Reddit thread comment. This is large enough to hold a complete, self-contained thought (e.g., "CS 3510 exams require writing proofs by hand. The median on the midterm is typically 55–65/100. The course is curved at the end.") while being specific enough that the embedding captures a narrow semantic topic rather than a soup of unrelated ideas. The 100-character overlap ensures that facts straddling a chunk boundary (like a grading breakdown split across two sentences) still appear intact in at least one chunk. I tested 300-character chunks and found retrieval returned fragments that lacked enough context to answer questions; I tested 800-character chunks and found the embedding captured multiple unrelated topics per chunk, making similarity matching imprecise.

**Final chunk count:** 161 chunks across 13 documents (verified by running `python ingest.py`)

**Sample chunks:**

```
[Source: rmp_cs3510_reviews.txt, chunk #3]
CS 3510 is the hardest required CS course at Georgia Tech for most students. The
course covers: divide and conquer, dynamic programming, greedy algorithms, graph
algorithms (shortest paths, MSTs, network flow), NP-completeness, randomized
algorithms, and linear programming. Professor Vempala is a brilliant researcher
but his lectures are very theoretical — you need to study the textbook (CLRS)
alongside the slides.
```

```
[Source: reddit_cs1332_tips.txt, chunk #5]
The AVL tree assignment is the hardest in CS 1332. Specific tips:
1. Use the CS 1332 Visualizer to animate insertions and deletions before
implementing. 2. The four rotation cases: left-left (single right rotation),
right-right (single left rotation), left-right (double: left rotation on child,
then right rotation on parent), right-left (double: right rotation on child,
then left rotation on parent). 3. Update heights AFTER rotations, not before.
```

```
[Source: rmp_cs4641_reviews.txt, chunk #2]
The team project in CS 4641 is a significant part of your grade — about 25-30%
of the total. Teams are groups of 3-4 students and you choose your own project
topic (with instructor approval). Past teams have done projects on: predicting
stock prices, classifying medical images, sentiment analysis of Reddit posts, and
sports outcome prediction. The project has four deliverables: proposal, midpoint
report, final report, and a 3-minute video presentation.
```

```
[Source: reddit_cs1331_tips.txt, chunk #4]
Java debugging tips for CS 1331:
1. Read the stack trace. The first line tells you the exception type and message.
2. Use IntelliJ's debugger, not print statements. Set a breakpoint, run in debug
mode, and inspect variable values at the point of failure. 3. Common errors:
ClassCastException (wrong type cast — check instanceof before casting),
NullPointerException (calling a method on null), ArrayIndexOutOfBoundsException
(off-by-one in a loop).
```

```
[Source: reddit_gatech_cs_survival.txt, chunk #7]
Tips that worked for me getting through CS 2200: (1) Learn gdb and Valgrind
before the semester starts. (2) Draw out your data structures on paper before
coding. (3) For the cache simulator, trace through a small example by hand
before implementing. (4) For the thread library, read the provided starter code
carefully. (5) Start each project at least one week before the deadline. (6) The
textbook (written by Ramachandran) is actually very readable.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via the `sentence-transformers` library. This model produces 384-dimensional embeddings, runs entirely locally on CPU, requires no API key, and has no rate limits or per-query cost. It was trained on over 1 billion sentence pairs and performs well on short, semantically dense text — a good match for the review-style corpus used here.

**Production tradeoff reflection:**
If deploying this system for real users at scale, I would weigh several tradeoffs:

- **Accuracy vs. cost**: `OpenAI text-embedding-3-large` (3072 dimensions) consistently outperforms `all-MiniLM-L6-v2` on retrieval benchmarks, but adds per-query API cost and introduces network latency and external dependency. For a high-traffic student tool, the cost per query would accumulate quickly.
- **Stronger local models**: `BAAI/bge-large-en-v1.5` and `intfloat/e5-large-v2` are both significantly stronger than MiniLM on the MTEB retrieval benchmark while still running locally — the tradeoff is ~3x more memory usage and ~2x slower encoding on CPU.
- **Context length**: `all-MiniLM-L6-v2` truncates inputs at 256 tokens (~1,000 characters). The 500-character chunks used here are safely within this limit. Longer documents would require a model with a higher token limit (e.g., `longformer-based` embedders) or careful pre-chunking.
- **Domain-specific fine-tuning**: For truly production-grade accuracy, fine-tuning an embedding model on (query, relevant-document) pairs drawn from actual GT student questions would likely improve retrieval quality measurably — but requires labeled data that doesn't exist at this stage.

---

## Grounded Generation

**System prompt grounding instruction:**

The following system prompt is passed to `llama-3.3-70b-versatile` via the Groq API in `query.py`:

```
You are the Georgia Tech CS Unofficial Guide — a helpful assistant that answers
student questions about CS courses and professors at Georgia Tech.

IMPORTANT RULES:
1. Answer ONLY using the information provided in the "Retrieved Documents" section below.
2. Do NOT use any general knowledge from your training data about Georgia Tech,
   courses, or professors.
3. If the retrieved documents do not contain enough information to answer the question,
   respond with: "I don't have enough information in my documents to answer that question."
4. At the end of every answer, list the source documents you drew from under a
   "Sources:" heading.
5. Be specific and quote or paraphrase the documents directly — do not extrapolate.
```

The user message passed to the model is:
```
Retrieved Documents:

[Document 1 — rmp_cs3510_reviews.txt]
<chunk text>

[Document 2 — reddit_cs3510_study.txt]
<chunk text>
...

Student Question: <user query>
```

**How source attribution is surfaced in the response:**
Source attribution operates at two levels. First, the LLM is instructed in the system prompt to include a "Sources:" section in every response listing which documents it drew from. Second, the `ask()` function in `query.py` programmatically extracts the unique source filenames from the retrieved chunks and returns them alongside the answer — the Gradio UI (`app.py`) displays these in a dedicated "Sources used" box independent of the LLM's output. This ensures attribution is always present even if the LLM omits it.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the workload like for CS 1301 at Georgia Tech? | Weekly labs (1–3 hrs), homework projects, ~6–10 hrs/week total; two midterms + one final | System correctly identified weekly labs (~1–3 hrs each), larger homework projects, total 6–10 hrs/week, two midterms and a final. Mentioned that recursion is the hardest topic. | Relevant | Accurate |
| 2 | What study strategies do students recommend for CS 3510? | Practice DP formally (define subproblem, recurrence, complexity), exchange argument for greedy, do all past exams timed, study CLRS, form study groups | System accurately described the DP template (formal subproblem definition, recurrence, base cases), exchange argument for greedy proofs, Master Theorem for divide-and-conquer, and recommended CLRS and past exams. | Relevant | Accurate |
| 3 | How is CS 4641 graded and what does the team project involve? | ~35% HW, ~30% team project (proposal + midpoint + final + video), ~15% midterm, ~20% final; teams of 3–4, semester-long | System correctly described the grading breakdown and the four project deliverables (proposal, midpoint report, final report, video presentation). Mentioned team sizes of 3–4 and that the Kaggle competition is optional extra credit. | Relevant | Accurate |
| 4 | What programming language is used in CS 1332 and how hard is it compared to CS 1331? | Java; significantly harder — AVL trees, graphs, 100+ autograder test cases; big jump from CS 1331 | Top result was a `rmp_cs2200_reviews.txt` chunk (cosine dist=0.31) about C vs. Java in the context of CS 2200 — not CS 1332. Generic terms "programming language" and "hard" matched CS 2200 content. CS 1332-specific chunks were absent from the top-5. System received mostly irrelevant context and likely gave a partially accurate answer. | Partially relevant | Partially accurate |
| 5 | What resources do students recommend for debugging Java in CS 1331? | IntelliJ IDEA, read the stack trace, use the debugger not print statements, TA office hours | Top 3 results were CS 2200 chunks (dist=0.39–0.47). The `reddit_cs1331_tips.txt` chunk with IntelliJ/debugger advice ranked 4th at dist=0.49. The word "debugging" matched CS 2200 content about C debugging (gdb, segfaults). System likely returned a partially off-target answer. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**
"What programming language is used in CS 1332 and how hard is it compared to CS 1331?"

**What the system returned:**
The top-ranked chunk (cosine dist=0.311) was from `rmp_cs2200_reviews.txt`: *"The jump to C programming from Java is brutal — memory management, pointer arithmetic, and segfaults are a whole new class of bugs that don't appear in Java."* This chunk discusses CS 2200 (a different course), not CS 1332. None of the top-5 retrieved chunks were from the CS 1332 documents (`rmp_cs1332_reviews.txt`, `reddit_cs1332_tips.txt`) that actually answer the question.

**Root cause (tied to a specific pipeline stage):**
This is a retrieval failure at the **embedding + similarity search** stage. The query contains high-frequency terms — "programming language," "hard," "compared to" — that appear in many course documents and act as noise. The CS 2200 review chunk ranked highest because it contains both "Java" (in contrast to C) and words about difficulty, creating surface-level semantic overlap with the query even though it answers a completely different question.

A secondary cause is that the 500-character chunking split some CS 1332-specific sentences across chunk boundaries. The sentence "CS 1332 is a big jump from CS 1331. This course covers Java data structures..." appears in `rmp_cs1332_reviews.txt`, but the first chunk ends mid-sentence and the second chunk begins after the topic shift, so neither chunk individually contains both "CS 1332 Java" and "harder than CS 1331" in a dense enough form to rank highly.

**What you would change to fix it:**
Two options: (1) **Query expansion** — append the course name as a keyword prefix: "CS 1332 Java: what programming language is used and how hard is it compared to CS 1331?" This biases the embedding toward CS 1332-specific content. (2) **Paragraph-aware chunking** — instead of fixed-character chunks, split on double newlines (paragraph boundaries) so each review stays intact. This would preserve the "CS 1332 is a big jump from CS 1331... Java is used..." context in one chunk rather than splitting it across two.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The architecture diagram in `planning.md` was essential when implementing `query.py`. Having the pipeline stages drawn out — with `retrieve()` and `ask()` as separate functions — prevented me from collapsing retrieval and generation into one monolithic function that would have been harder to test and debug. Because the spec separated retrieval from generation, I was able to test retrieval alone (running `retrieve("CS 3510 exam tips")` and printing the returned chunks) before wiring in the Groq API. This caught a distance-scoring issue (chunks were not using cosine similarity until I added `metadata={"hnsw:space": "cosine"}` to the ChromaDB collection) before generation was involved.

**One way your implementation diverged from the spec, and why:**
The spec described a single `query.py` file handling both retrieval and generation, but I also added a `retrieve()` function as a standalone callable — not originally in the spec — because testing generation in isolation was impractical without it. Additionally, the Gradio UI in `app.py` added a third "retrieved chunks (debug view)" accordion panel not mentioned in the planning. This was necessary because during testing, seeing the actual retrieved chunks and their distance scores was the only way to diagnose retrieval failures — the LLM's response alone doesn't tell you which chunks were returned or whether they were relevant. The spec was updated to reflect these additions.

---

## AI Usage

**Instance 1 — Chunking and ingestion code**

- *What I gave the AI:* The Documents section of `planning.md` (13 .txt files, review-style text), the Chunking Strategy section (500-char chunks, 100-char overlap, reason: short review corpus), and a request to implement `ingest.py` with `load_documents()`, `clean_text()`, and `chunk_text()` functions.
- *What it produced:* A complete `ingest.py` with all three functions. The `clean_text()` function included regex to strip HTML tags — which I removed, since these documents are already clean plain text with no HTML artifacts. The generated chunk loop used `text[start:end]` slicing without a minimum-length guard.
- *What I changed or overrode:* I removed the HTML stripping from `clean_text()` (not needed for plain text files), added a `len(chunk) > 50` guard to skip near-empty trailing chunks, and changed the loop termination condition to `break` when `end == len(text)` to avoid an infinite loop on the last chunk.

**Instance 2 — Generation, grounding prompt, and Gradio interface**

- *What I gave the AI:* The grounding requirement ("answer only from retrieved documents, cite sources"), the system prompt design, the `ask()` function signature with its return type (`{"answer", "sources", "chunks"}`), and the Gradio structure requirement (question input, answer output, sources output, debug accordion).
- *What it produced:* A complete `query.py` and `app.py`. The initial system prompt said "try to answer from the provided documents" — which is a suggestion, not an instruction. Passive framing like "try to" is known to reduce grounding compliance in instruction-following LLMs.
- *What I changed or overrode:* I rewrote the system prompt to use imperative RULES (numbered, capitalized "IMPORTANT RULES") with an explicit instruction to refuse rather than answer when documents are insufficient. I also added ordered-unique deduplication of sources using `dict.fromkeys()` instead of `set()` so sources appear in retrieval order rather than arbitrary hash order. I also added the "debug view" accordion showing raw chunks and distances, which was not in the original generated interface.
