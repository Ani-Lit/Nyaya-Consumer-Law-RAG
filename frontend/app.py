import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from retrieval.rag_chain import generate

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Nyaya — Consumer Law Study Assistant",
    page_icon="⚖",
    layout="centered"
)

# ── Fonts ─────────────────────────────────────────────────
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #101010;
    color: #e7e2da;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 860px; padding-top: 4rem; padding-bottom: 3rem; }

.nyaya-header { padding-bottom: 2.5rem; margin-bottom: 2.5rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.nyaya-title { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 600; letter-spacing: -1px; margin-bottom: 0.4rem; color: #f3efe8; }
.nyaya-title span { color: #c6a56b; font-style: italic; }
.nyaya-subtitle { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1.8px; color: #8b8175; margin-bottom: 1.2rem; }
.nyaya-desc { font-size: 0.98rem; line-height: 1.9; color: #a8a098; max-width: 650px; }

.coverage { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1.5rem; }
.tag { font-size: 0.7rem; padding: 0.4rem 0.75rem; border: 1px solid rgba(198,165,107,0.18); background: rgba(198,165,107,0.05); color: #c6a56b; border-radius: 999px; letter-spacing: 0.8px; }

.section-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.8px; color: #7d746a; margin-bottom: 1rem; }

.stButton > button {
    width: 100%; background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important; color: #c8c1b8 !important;
    border-radius: 12px !important; padding: 0.9rem 1rem !important;
    text-align: left !important; font-size: 0.84rem !important; line-height: 1.5 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { border-color: rgba(198,165,107,0.45) !important; background: rgba(198,165,107,0.05) !important; color: #f2ede6 !important; }

[data-testid="stChatMessage"] { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.05); border-radius: 18px; padding: 1.3rem 1.4rem !important; margin-bottom: 1rem; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { border-left: 2px solid #c6a56b; background: rgba(255,255,255,0.03); }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: rgba(198,165,107,0.04); border: 1px solid rgba(198,165,107,0.12); }
[data-testid="stChatMessage"] p { font-size: 0.96rem !important; line-height: 1.9 !important; color: #ddd6cd !important; }

[data-testid="stChatInput"] textarea { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important; color: #f3eee7 !important; border-radius: 14px !important; padding: 0.9rem !important; font-size: 0.92rem !important; }
[data-testid="stChatInput"] textarea:focus { border-color: rgba(198,165,107,0.45) !important; box-shadow: none !important; }

.streamlit-expanderHeader { color: #9b9185 !important; font-size: 0.76rem !important; letter-spacing: 1px !important; }
.streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.05) !important; padding: 0.8rem !important; }

hr { border-color: rgba(255,255,255,0.06) !important; margin: 2.5rem 0 !important; }
.nyaya-footer { text-align: center; color: #6f675f; font-size: 0.78rem; line-height: 1.8; padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.markdown("""
<div class="nyaya-header">
    <p class="nyaya-title">N<span>yaya</span></p>
    <p class="nyaya-subtitle">Consumer Law Study Assistant &nbsp;·&nbsp; India</p>
    <p class="nyaya-desc">
        A research tool for law students. Ask questions about consumer law, 
        get answers grounded in the actual text of Indian legislation — 
        with section references and legal precision.
    </p>
    <div class="coverage">
        <span class="tag">CPA 2019</span>
        <span class="tag">E-Commerce Rules 2020</span>
        <span class="tag">Legal Metrology Act 2009</span>
        <span class="tag">Mediation Rules 2020</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Example Queries ───────────────────────────────────────
st.markdown('<p class="section-label">Sample queries</p>', unsafe_allow_html=True)

example_queries = [
    "Define consumer under Section 2(7) of CPA 2019",
    "What is the pecuniary jurisdiction of the District Commission?",
    "Explain unfair trade practice under CPA 2019",
    "What are the powers of the Central Consumer Protection Authority?",
    "What constitutes deficiency in service?",
    "Explain the mediation process under Consumer Protection Act"
]

cols = st.columns(2)
selected_example = None
for i, q in enumerate(example_queries):
    if cols[i % 2].button(q):
        selected_example = q

st.markdown("---")

# ── Chat History ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────
query = st.chat_input("Ask about consumer law — section, definition, jurisdiction...") or selected_example

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching legislation..."):
            result = generate(query, persona="student")
        st.markdown(result["answer"])
        with st.expander("Sources"):
            st.caption(f"Query intent: {result['intent']}")
            if result["act_sources"]:
                st.caption("Legislation")
                for s in result["act_sources"]:
                    st.markdown(f"`{s}`")
            if result["principle_sources"]:
                st.caption("Principles & Case Law")
                for s in result["principle_sources"]:
                    st.markdown(f"`{s}`")
            st.caption(f"{result['chunks_used']} chunks retrieved")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"]
    })

# ── Footer ────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="nyaya-footer">
    For academic and educational purposes only. Not a substitute for professional legal advice.<br>
    Nyaya is grounded in Indian consumer legislation as of 2020.
</div>
""", unsafe_allow_html=True)