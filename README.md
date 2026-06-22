# Nyaya: Consumer Law Reasoning System

Nyaya is a domain-specific Retrieval-Augmented Generation (RAG) system designed to help students understand Indian Consumer Law through legal principles, landmark judgments, statutory provisions, and real-world consumer scenarios.

Unlike traditional legal chatbots that rely solely on statutory retrieval, Nyaya uses a principle-driven retrieval architecture that connects user queries to legal doctrines, case law, and practical consumer disputes.

---

## Why Nyaya?

Legal questions are rarely asked using legal terminology.

For example:

> "My car keeps developing engine problems despite multiple repairs."

A student may not know:

* the relevant legal principle,
* the landmark judgment,
* or the applicable provision of the Consumer Protection Act.

Nyaya bridges this gap by retrieving:

1. Real-world scenario
2. Legal principle
3. Landmark judgment
4. Statutory provision
5. Structured explanation

This makes legal concepts easier to understand and remember.

---

## Features

* Principle-driven legal retrieval
* Landmark case integration
* Scenario-based semantic search
* Consumer Protection Act 2019 retrieval
* Legal Metrology Act 2009 retrieval
* Structured educational responses
* Student-focused legal explanations
* Source-grounded answer generation

---

## Knowledge Base

### Statutes

* Consumer Protection Act, 2019
* Legal Metrology Act, 2009

### Rules

* Consumer Protection (E-Commerce) Rules, 2020
* Consumer Protection (Mediation) Rules, 2020

### Legal Principles

* 54 legal principles extracted from landmark consumer law judgments

Examples include:

* Definition of Consumer
* Commercial Purpose Exclusion
* Medical Negligence
* Informed Consent
* Housing Delay Compensation
* Insurance Claim Repudiation
* Deficiency in Service
* Limitation Period
* Consumer Rights
* Compensation Jurisprudence

### Landmark Cases

Nyaya currently incorporates 24 landmark judgments including:

* Laxmi Engineering Works v PSG Industrial Institute
* Indian Medical Association v VP Shantha
* Lucknow Development Authority v MK Gupta
* Jacob Mathew v State of Punjab
* Samira Kohli v Dr Prabha Manchanda
* Charan Singh v Healing Touch Hospital
* Maruti Udyog Ltd v Susheel Kumar Gabgotra
* National Insurance Co Ltd v Hindustan Safety Glass Works Ltd
* Kishore Lal v Chairman, ESI Corporation

### Real-World Scenarios

* 25 consumer dispute scenarios
* Medical negligence
* Insurance disputes
* E-commerce fraud
* Builder delays
* Defective goods
* Warranty disputes
* Telecom complaints
* Banking disputes

---

## Architecture

User Query

↓

Semantic Embedding

↓

Pinecone Vector Search

↓

Scenario Retrieval

↓

Legal Principle Retrieval

↓

Case Law Retrieval

↓

Statutory Retrieval

↓

LLM Response Generation

↓

Structured Legal Answer

---

## Tech Stack

### Backend

* Python
* Pinecone
* Sentence Transformers
* Groq API

### Embeddings

* all-MiniLM-L6-v2

### LLM

* Llama 3.3 70B (Groq)

### Frontend

* Streamlit

---

## Example Query

### User Question

> A patient underwent surgery without being informed about the risks involved. Can they claim compensation under consumer law?

### Nyaya Retrieves

* Principle 21 — Informed Consent
* Principle 19 — Medical Negligence
* Principle 51 — Compensation Jurisprudence
* Samira Kohli v Dr Prabha Manchanda
* Jacob Mathew v State of Punjab
* Charan Singh v Healing Touch Hospital

### Output

Structured answer including:

* Direct Answer
* Explanation
* Legal Basis
* Landmark Case & Principle
* Practical Context
* Related Topics

---

## Project Structure

```text
frontend/
ingestion/
retrieval/

data/
├── acts/
├── rules/
├── judgements/
└── scenarios/

README.md
requirements.txt
```

## Installation

```bash
git clone https://github.com/Ani-Lit/Nyaya.git
cd Nyaya

pip install -r requirements.txt
```

Create a `.env` file:

```env
PINECONE_API_KEY=your_key
GROQ_API_KEY=your_key
```

Run:

```bash
streamlit run frontend/app.py
```

---

## Future Improvements

* Retrieval benchmarking framework
* Hybrid retrieval (Dense + BM25)
* Reranking pipeline
* Legal citation support
* Explainable retrieval traces
* Multi-jurisdiction legal knowledge base

---

## Author

Anirudha Kumar

B.Tech Computer Science (AI)
Shoolini University

Interested in:

* Machine Learning
* Computer Vision
* NLP
* Retrieval-Augmented Generation
* Medical Imaging
* AI for Legal Systems
