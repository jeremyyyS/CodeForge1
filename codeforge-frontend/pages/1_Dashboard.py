import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

from utils.auth import require_auth, get_current_user
from utils import api

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="CodeForge",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"   # 👈 Sidebar toggle enabled
)

# -------------------- AUTH --------------------
require_auth()
user = get_current_user()

# -------------------- SESSION STATE --------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "result" not in st.session_state:
    st.session_state.result = None

# -------------------- THEME TOGGLE --------------------
def switch_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# -------------------- THEME COLORS --------------------
if st.session_state.theme == "dark":
    BG = "#0B0F19"
    CARD = "rgba(17,24,39,0.8)"
    TEXT = "#E6E8EC"
    ACCENT = "#00F5FF"
    GRAPH_FONT = "#E6E8EC"
    button_label = "Light Mode"
else:
    BG = "#F5F7FA"
    CARD = "rgba(255,255,255,0.95)"
    TEXT = "#111827"
    ACCENT = "#2563EB"
    GRAPH_FONT = "#111827"
    button_label = "Dark Mode"

# -------------------- GLOBAL STYLING --------------------
st.markdown(f"""
<style>

/* Keep sidebar toggle visible */
#MainMenu, footer {{visibility:hidden;}}

/* Proper centering behaviour */
.block-container {{
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
    padding-top: 1.5rem;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {BG};
    color: {TEXT};
}}

.codeforge-title {{
    text-align: center;
    font-size: 64px;
    font-weight: 800;
    background: linear-gradient(90deg, #00F5FF, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.subtitle {{
    text-align: center;
    font-size: 16px;
    opacity: 0.7;
    margin-bottom: 20px;
}}

.stButton>button {{
    background: linear-gradient(90deg, #2563EB, #00F5FF);
    color: white;
    border-radius: 10px;
    border: none;
    height: 48px;
    font-weight: 600;
}}

.metric-card {{
    background: {CARD};
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    border: 1px solid rgba(59,130,246,0.3);
}}

.metric-value {{
    font-size: 30px;
    font-weight: 700;
    color: {ACCENT};
}}

.ai-panel {{
    background: {CARD};
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(0,245,255,0.3);
}}

</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR CONTENT --------------------
with st.sidebar:
    st.title("Navigation")
    st.write(f"Signed in as **{user['username']}**")
    st.write("---")
    st.write("You can collapse this sidebar using the ☰ button.")

# -------------------- HEADER --------------------
header_left, header_right = st.columns([8,2])

with header_left:
    st.markdown("<div class='codeforge-title'>CODEFORGE</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Shaping Faster. Smarter. Leaner Code.</div>", unsafe_allow_html=True)

with header_right:
    st.button(button_label, on_click=switch_theme)
    if st.button("Logout"):
        from utils.auth import logout
        logout()

st.divider()

# -------------------- LAYOUT --------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Input Code")

    code_input = st.text_area(
        "",
        height=300,
        placeholder="Paste your Python code here...",
        label_visibility="collapsed"
    )

    b1, b2 = st.columns(2)
    with b1:
        run = st.button("Run Optimization", use_container_width=True)
    with b2:
        bench = st.button("Benchmark Only", use_container_width=True)

with col2:
    st.markdown("### Optimized Code")
    output_placeholder = st.empty()

# -------------------- RUN LOGIC --------------------
if run and code_input.strip():
    with st.spinner("Optimizing..."):
        try:
            st.session_state.result = api.api_client.optimize(code_input)
        except Exception:
            st.session_state.result = {"error": "Backend unavailable."}

elif bench and code_input.strip():
    with st.spinner("Benchmarking..."):
        try:
            st.session_state.result = api.api_client.optimize_rules_only(code_input)
        except Exception:
            st.session_state.result = {"error": "Backend unavailable."}

result = st.session_state.result

# -------------------- OUTPUT --------------------
if result and not result.get("error"):
    optimized_code = result.get("optimized_code", "")
    output_placeholder.code(optimized_code, language="python")

    if result.get("ai_explanation"):
        explanation = result["ai_explanation"]
        st.markdown(f"""
        <div class="ai-panel">
            <h3>AI Analysis</h3>
            <p>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

elif result and result.get("error"):
    st.error(result["error"])



# -------------------- METRICS (SAFE HANDLING) --------------------
if result and isinstance(result, dict):

    metrics = result.get("benchmarks") or {}

    if metrics:
        orig = metrics.get("original") or {}
        opt = metrics.get("optimized") or {}

        orig_ms = orig.get("runtime_ms")
        opt_ms = opt.get("runtime_ms")
        orig_mem = orig.get("memory_mb")
        opt_mem = opt.get("memory_mb")
        speed = metrics.get("speedup_factor")

        st.divider()
        st.markdown("### Performance Metrics")

        m1, m2, m3 = st.columns(3)

        with m1:
            runtime_saved = round(orig_ms - opt_ms,2) if orig_ms and opt_ms else "—"
            st.markdown(f"<div class='metric-card'><div>Runtime Saved</div><div class='metric-value'>{runtime_saved}</div></div>", unsafe_allow_html=True)

        with m2:
            memory_saved = round(orig_mem - opt_mem,2) if orig_mem and opt_mem else "—"
            st.markdown(f"<div class='metric-card'><div>Memory Reduced</div><div class='metric-value'>{memory_saved}</div></div>", unsafe_allow_html=True)

        with m3:
            st.markdown(f"<div class='metric-card'><div>Speedup Factor</div><div class='metric-value'>{round(speed,2) if speed else '—'}</div></div>", unsafe_allow_html=True)

        # Gauge
        if speed:
            st.markdown("### 🚀 Speedup Performance")

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=speed,
                title={'text': "Speedup Factor"},
                gauge={'axis': {'range': [0, max(5, speed+1)]}}
            ))

            fig_gauge.update_layout(
                paper_bgcolor=BG,
                font_color=GRAPH_FONT,
                height=350
            )

            st.plotly_chart(fig_gauge, use_container_width=True)

        # Bar Charts
        st.markdown("### Performance Comparison")

        c1, c2 = st.columns(2)

        if orig_ms and opt_ms:
            df_runtime = pd.DataFrame({
                "Version": ["Before", "After"],
                "Runtime (ms)": [orig_ms, opt_ms]
            })
            fig_runtime = px.bar(df_runtime, x="Version", y="Runtime (ms)")
            fig_runtime.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=GRAPH_FONT
            )
            c1.plotly_chart(fig_runtime, use_container_width=True)

        if orig_mem and opt_mem:
            df_mem = pd.DataFrame({
                "Version": ["Before", "After"],
                "Memory (MB)": [orig_mem, opt_mem]
            })
            fig_mem = px.bar(df_mem, x="Version", y="Memory (MB)")
            fig_mem.update_layout(
                plot_bgcolor=BG,
                paper_bgcolor=BG,
                font_color=GRAPH_FONT
            )
            c2.plotly_chart(fig_mem, use_container_width=True)
