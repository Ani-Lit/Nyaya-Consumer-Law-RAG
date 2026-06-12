import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from groq import Groq

load_dotenv()

# ── Init ─────────────────────────────────────────────────
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("consumer-law-rag")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Persona Prompts ───────────────────────────────────────
STUDENT_PROMPT = """You are a precise legal study assistant for Indian consumer law students.
Use ONLY the provided context to answer. Do not make up information.

Query Intent: {intent}

Adjust your response style based on intent:
- definition: Lead with the exact legal definition, then explain in plain terms
- case_law: Lead with the case name and year, then holding, then significance
- procedural: Use numbered steps, be sequential and clear
- comparison: Use a clear contrast structure — first concept vs second concept
- remedies: List all available reliefs, penalties, and compensation heads
- exam_notes: Give a concise bullet-point summary optimized for memorization

Structure EVERY response exactly like this:

**Answer**
[Direct, one-line answer to the question]

**Explanation**
[2-3 sentences explaining the concept clearly]

**Legal Basis**
[Exact Section number and Act name]

**Landmark Case & Principle**
[Search the context carefully for any case name, principle number, or judgements reference.
State: Principle [number] — [name] + Case Name (Year) — what the court held.
If no case or principle is found in context, skip this section entirely.]

**Practical Context**
[1-2 sentences on how this applies in real scenarios or exams]

**Related Topics**
[3-5 bullet points of related legal concepts, sub-domains, and real-world applications.
Example format:
- Medical Negligence — deficiency in service by hospitals (Spring Meadows case)
- Housing Delays — builder liability under deficiency (Emaar MGF case)
- Telecom Disputes — wrongful disconnection as deficiency
- Banking — wrongful dishonour of cheque as deficiency
Only include what's relevant to the question asked.]

Rules:
- If case reference is not in context, skip that section
- Always cite exact section numbers
- Never guess or hallucinate sections
- Keep each section concise

Context:
{context}

Question: {question}"""

# ── Intent Detection ──────────────────────────────────────

def detect_intent(query: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """Classify the user's legal query into exactly one of these intents:
- definition: asking what something means
- case_law: asking about judgements or court rulings
- procedural: asking how to do something or process steps
- comparison: asking difference between two concepts
- remedies: asking about compensation, relief, or penalties
- exam_notes: asking for summary, notes, or exam preparation

Reply with ONLY the intent word, nothing else."""
            },
            {"role": "user", "content": query}
        ],
        temperature=0,
        max_tokens=10
    )
    intent = response.choices[0].message.content.strip().lower()
    valid = ["definition", "case_law", "procedural", "comparison", "remedies", "exam_notes"]
    return intent if intent in valid else "definition"

# ── Retrieve ──────────────────────────────────────────────
def retrieve(query: str, top_k: int = 25) -> list[dict]:
    embedding = embed_model.encode(query).tolist()
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    matches = results["matches"]

    acts = [m for m in matches if m["metadata"].get("doc_type") == "act"]
    rules = [m for m in matches if m["metadata"].get("doc_type") == "rules"]
    judgements = [m for m in matches if m["metadata"].get("doc_type") == "judgements"]
    scenarios = [m for m in matches if m["metadata"].get("doc_type") == "scenarios"]

    # Always try to include judgements chunks
    prioritized = judgements[:10] + scenarios[:3] + acts[:5] + rules[:3]

    return prioritized[:top_k]

# ── Generate ──────────────────────────────────────────────
def generate(query: str, persona: str = "student") -> dict:
    intent = detect_intent(query)          # ← Add this
    matches = retrieve(query)

    context = "\n\n".join([m["metadata"]["text"] for m in matches])

    act_sources = [m["metadata"]["source"] for m in matches if m["metadata"].get("doc_type") == "act"]
    principle_sources = [m["metadata"]["source"] for m in matches if m["metadata"].get("doc_type") == "judgements"]
    all_sources = list(set([m["metadata"]["source"] for m in matches]))

    prompt = STUDENT_PROMPT.format(
        context=context,
        question=query,
        intent=intent                      # ← Add this
    )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=700
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": all_sources,
        "act_sources": list(set(act_sources)),
        "principle_sources": list(set(principle_sources)),
        "chunks_used": len(matches),
        "intent": intent                   # ← Add this
    }

# ── Test ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== STUDENT MODE ===")
    result = generate("What is the definition of consumer under CPA 2019?", persona="student")
    print(result["answer"])
    print(f"\nSources: {result['sources']}")