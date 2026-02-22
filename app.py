import streamlit as st
import pandas as pd
import json
import os
from pywarp.parsers.wpl import WPLParser
from pywarp.parsers.oml import OMLEngine
from pywarp.parsers.knowdb import KnowledgeDatabase

# --- Page Config MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(layout="wide", page_title="PyWarp | AI Data Gateway & ETL Pipeline", page_icon="🚀")

# --- Initialize the Engine Components ---
@st.cache_resource
def load_engine():
    return WPLParser(), OMLEngine(), KnowledgeDatabase()

wpl, oml, know = load_engine()

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-family: monospace; color: #00ff41; background-color: #1a1c24; }
    .stAlert { background-color: #1a1c24; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: Navigation & Technical Architecture ---
with st.sidebar:
    st.title("🧭 Navigation")
    page = st.radio("Select Page:", ["📖 Home & Use Cases", "🧪 Interactive Playground"])
    
    st.markdown("---")
    st.title("⚙️ Engine Architecture")
    st.info("**Core Principles:**\n1. Hybrid Concurrency\n2. Deep PII Masking\n3. SQL Enrichment")
    st.markdown("---")
    st.write("**Tech Stack:**\n- Python 3.11\n- AsyncIO / Multi-core\n- SQLite (In-Memory)\n- Pydantic")
    if st.button("Download Technical Specs (PDF)"):
        st.write("Coming soon in v2.0")

# ==========================================
# PAGE 1: HOME & USE CASES
# ==========================================
if page == "📖 Home & Use Cases":
    st.title("🚀 PyWarp: High-Performance AI-Native Data Gateway")
    st.markdown("""
    PyWarp is a cutting-edge ETL engine designed to process raw, unstructured logs at high-throughput, 
    transforming them into clean, enriched, and privacy-compliant data streams for downstream 
    AI/ML, Security, and DevOps systems.
    """)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("💡 The Problem: Unstructured Logs ➡️ Unusable Data")
        st.write("Raw server logs are messy, inconsistent, and actively violate compliance laws if stored raw.")
        st.code('222.133.52.20 - "Patty Greenfield" [06/Aug/2019:12:12:19 +0800] "GET /checkout?cc=4111-2222-3333-4444 HTTP/1.1"', language="text")
    with col2:
        st.subheader("✨ The Solution")
        st.markdown("""
        1. **High-Speed Parsing:** Advanced Regex and Hash deduplication.
        2. **Deep PII Masking:** Redacts Credit Cards, Passwords, and Names.
        3. **SQL Enrichment:** Joins threat intel in real-time.
        4. **Schema Normalization:** 1NF URL splitting and ISO time casting.
        """)

    st.markdown("---")
    st.subheader("🎯 Real-World Data Feeds & Team Use Cases")
    
    tab1, tab2, tab3 = st.tabs(["🛡️ Security (SOC)", "⚙️ DevOps (SRE)", "🤖 AI/ML Data Science"])

    with tab1:
        st.markdown("### 🛡️ Security Operations Center")
        st.write("Automatically redacts PCI/GDPR data while flagging malicious external IPs.")
        col_s1, col_s2 = st.columns(2)
        col_s1.info("**Raw Hacker Input:**")
        col_s1.code('222.133.52.20 - - [time] "GET /login?pwd=admin123 HTTP/1.1"', language="text")
        col_s2.success("**PyWarp Output Stream:**")
        col_s2.code('{\n  "ip_masked": "222.133.*.*",\n  "endpoint": "/login?pwd=[REDACTED_SECRET]",\n  "threat_level": "High"\n}', language="json")

    with tab2:
        st.markdown("### ⚙️ DevOps & SRE")
        st.write("Standardizes chaotic timestamps and attributes infrastructure costs by department.")
        col_d1, col_d2 = st.columns(2)
        col_d1.info("**Raw Microservice Input:**")
        col_d1.code('10.0.0.5 - - [Tuesday, 22-Feb-2026 11:43:37 IST] "GET /api/v1/health HTTP/1.1" 500', language="text")
        col_d2.success("**PyWarp Output Stream:**")
        col_d2.code('{\n  "time_iso": "2026-02-22T11:43:37+05:30",\n  "department": "HR_Internal",\n  "status": 500\n}', language="json")

    with tab3:
        st.markdown("### 🤖 AI/ML Pipelines")
        st.write("Provides perfectly structured, noise-free features for RAG vector databases or training.")
        col_a1, col_a2 = st.columns(2)
        col_a1.info("**Squashed/Messy Input:**")
        col_a1.code('192.168.1.100 - "John Doe" [2026-01-01] GET/squashed_url HTTP/1.0', language="text")
        col_a2.success("**PyWarp Output Stream:**")
        col_a2.code('{\n  "user_masked": "J*** D***",\n  "http_method": "GET",\n  "endpoint": "/squashed_url"\n}', language="json")

    st.markdown("---")
    st.success("### 🚀 Now enough about the explanation, let's actually see it in real-time with your own data! Head over to the **Interactive Playground** using the sidebar on the left.")

# ==========================================
# PAGE 2: INTERACTIVE PLAYGROUND
# ==========================================
elif page == "🧪 Interactive Playground":
    st.title("🧪 Interactive Log Playground")
    st.markdown("Paste your messy logs, XSS attacks, or malformed URLs below. Watch the engine sort, mask, and enrich them instantly.")

    # Default hardcore test data
    default_logs = """2001:0db8::1 - "Admin User" [23/Feb/2026:12:20:00 +0000] "POST /checkout?cc=4111-2222-3333-4444&password=MySecretPassword123 HTTP/1.1" 200
222.133.52.20 - - [23/Feb/2026:12:05:00 +0000] "GET /purchase?amount=999999999 HTTP/1.1" OK
10.0.0.5 - - [12/31/2025:10:00:00 +0000] GET/switched_rows_columns HTTP/1.0 500"""

    input_col, output_col = st.columns(2)

    with input_col:
        st.markdown("**📥 Step 1: Messy Input Stream**")
        user_input = st.text_area("Paste Raw Logs Here:", value=default_logs, height=200)

    with output_col:
        st.markdown("**📤 Step 2: Engine Action**")
        st.write("Click below to pass the data through the WPL Parser, OML Engine, and Knowledge DB.")
        process_btn = st.button("✨ Transform & Sort Data", use_container_width=True)

    # Initialize session state to hold the processed dataframe
    if "processed_df" not in st.session_state:
        st.session_state.processed_df = None

    if process_btn:
        # Clear the deduplicator memory so users can test the same logs multiple times
        wpl.seen_hashes.clear() 
        
        raw_lines = user_input.strip().split('\n')
        processed_records = []
        
        # --- Process Data ---
        for line in raw_lines:
            if not line.strip(): continue
            parsed = wpl.parse(line)
            transformed = oml.transform(parsed)
            final = know.enrich(transformed)
            processed_records.append(final)
        
        # Save to session state so it survives the Download button rerun
        st.session_state.processed_df = pd.DataFrame(processed_records)
        
    # --- Display Results (Outside the button click) ---
    if st.session_state.processed_df is not None:
        df = st.session_state.processed_df
        
        st.markdown("---")
        st.subheader("🗄️ Cleaned & Enriched Output")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Clean CSV", data=csv, file_name="pywarp_cleaned_logs.csv", mime="text/csv")

        # --- "Something Interesting": Live Metrics Dashboard ---
        st.markdown("---")
        st.subheader("📊 Gateway Traffic Monitor")
        st.write("Real-time telemetry generated from the processed log batch.")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Total Logs Processed", value=len(df))
        
        if "threat_level" in df.columns:
            high_threats = len(df[df["threat_level"] == "High"])
            m2.metric(label="High Threats Blocked/Tagged", value=high_threats)
        if "status" in df.columns:
            errors = len(df[df["status"] >= 400])
            m3.metric(label="HTTP Errors (4xx/5xx)", value=errors)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Traffic by Department**")
            if "department" in df.columns:
                dept_counts = df["department"].value_counts()
                st.bar_chart(dept_counts) # Removed 'color' arg to ensure compatibility with all Streamlit versions
        with c2:
            st.markdown("**Security Threat Distribution**")
            if "threat_level" in df.columns:
                threat_counts = df["threat_level"].value_counts()
                st.bar_chart(threat_counts)