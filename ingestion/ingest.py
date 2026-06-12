import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── Config ──────────────────────────────────────────────
RAW_DIRS = [
    ("data/raw/acts", "act"),
    ("data/raw/rules", "rules"),
    ("data/raw/scenarios", "scenarios"),
    ("data/raw/judgements", "judgements"),
]
PROCESSED_DIR = Path("data/processed")
METADATA_DIR = Path("data/metadata")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "consumer-law-rag"
EMBED_MODEL = "all-MiniLM-L6-v2"  # Fast, free, good quality

# ── Step 1: Extract text from PDFs ──────────────────────
def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# ── Step 2: Chunk text ───────────────────────────────────
def chunk_text(text: str, doc_name: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    
    return [
        {
            "id": f"{doc_name}_chunk_{i}",
            "text": chunk,
            "metadata": {
                "source": doc_name,
                "chunk_index": i,
                "doc_type": "doc_type"
            }
        }
        for i, chunk in enumerate(chunks)
    ]

# ── Step 3: Embed ────────────────────────────────────────
def embed_chunks(chunks: list[dict], model) -> list[dict]:
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
    return chunks

# ── Step 4: Upsert to Pinecone ───────────────────────────
def upsert_to_pinecone(chunks: list[dict], index):
    vectors = [
        {
            "id": c["id"],
            "values": c["embedding"],
            "metadata": {**c["metadata"], "text": c["text"]}
        }
        for c in chunks
    ]
    # Upsert in batches of 50
    for i in range(0, len(vectors), 50):
        index.upsert(vectors=vectors[i:i+50])
    print(f"Upserted {len(vectors)} vectors.")

# ── Main Pipeline ────────────────────────────────────────
def main():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(INDEX_NAME)
    model = SentenceTransformer(EMBED_MODEL)

    for raw_dir, doc_type in RAW_DIRS:
        path = Path(raw_dir)
        if not path.exists():
            print(f"Skipping {raw_dir} — folder not found")
            continue

        files = list(path.glob("*.pdf")) + list(path.glob("*.txt"))

        for file_path in files:
            print(f"\nProcessing: {file_path.name}")
            doc_name = file_path.stem

            if file_path.suffix == ".pdf":
                text = extract_text(file_path)
            else:
                text = file_path.read_text(encoding="utf-8")

            (PROCESSED_DIR / f"{doc_name}.txt").write_text(text, encoding="utf-8")

            chunks = chunk_text(text, doc_name)

            for chunk in chunks:
                chunk["metadata"]["doc_type"] = doc_type

            with open(METADATA_DIR / f"{doc_name}.json", "w") as f:
                json.dump([{k: v for k, v in c.items()
                           if k != "embedding"} for c in chunks], f, indent=2)

            chunks = embed_chunks(chunks, model)
            upsert_to_pinecone(chunks, index)
            print(f"Done: {doc_name} — {len(chunks)} chunks | type: {doc_type}")

    print("\n✅ All documents ingested successfully.")

if __name__ == "__main__":
    main()