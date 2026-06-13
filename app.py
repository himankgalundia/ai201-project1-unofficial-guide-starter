"""
Gradio web interface for the GT CS Unofficial Guide RAG system.

Run:
    python app.py
Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from query import ask

EXAMPLE_QUESTIONS = [
    "What is the workload like for CS 1301 at Georgia Tech?",
    "What study strategies do students recommend for CS 3510?",
    "How is CS 4641 Machine Learning graded and what does the team project involve?",
    "What programming language is used in CS 1332 and how hard is it compared to CS 1331?",
    "What resources do students recommend for passing CS 1331 Java?",
    "How difficult are the exams in CS 2200 Systems and Networks?",
]


def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", "", ""

    try:
        result = ask(question.strip())
    except Exception as e:
        return f"Error: {str(e)}", "", ""

    answer = result["answer"]
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    chunks_text = "\n\n".join(
        f"[{c['source']} | chunk #{c['chunk_index']} | dist={c['distance']}]\n{c['text'][:300]}..."
        for c in result["chunks"]
    )
    return answer, sources_text, chunks_text


with gr.Blocks(title="GT CS Unofficial Guide", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
# Georgia Tech CS — Unofficial Student Guide
Ask questions about CS courses and professors at Georgia Tech, based on real student reviews and tips.

**Tip:** The system answers only from its document collection. If it says "I don't have enough information," the topic isn't covered in the documents.
"""
    )

    with gr.Row():
        with gr.Column(scale=2):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. How hard is CS 3510? What are tips for CS 1332?",
                lines=3,
            )
            ask_btn = gr.Button("Ask", variant="primary")

            gr.Examples(
                examples=EXAMPLE_QUESTIONS,
                inputs=question_box,
                label="Example questions",
            )

        with gr.Column(scale=3):
            answer_box = gr.Textbox(label="Answer", lines=14)
            sources_box = gr.Textbox(label="Sources used", lines=5)

    with gr.Accordion("Retrieved chunks (debug view)", open=False):
        chunks_box = gr.Textbox(label="Raw retrieved chunks", lines=15)

    ask_btn.click(
        handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )
    question_box.submit(
        handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )

if __name__ == "__main__":
    demo.launch()
