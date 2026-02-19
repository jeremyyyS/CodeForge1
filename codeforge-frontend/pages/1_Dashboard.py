import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html as html_module

from utils.auth import require_auth, get_current_user
from utils import api

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="CodeForge",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
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

.rule-tag {{
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 8px;
    padding: 6px 12px;
    margin: 4px;
    font-size: 13px;
}}

.safety-ok {{
    color: #22C55E;
    font-weight: 600;
}}

.safety-warn {{
    color: #F59E0B;
    font-weight: 600;
}}

</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR CONTENT --------------------
with st.sidebar:
    st.title("Navigation")
    st.write(f"Signed in as **{user['username']}**")
    st.write("---")
    st.write("You can collapse this sidebar using the menu button.")

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

# -------------------- MODE SELECTOR --------------------
st.markdown("### Select Optimization Mode")
opt_mode = st.radio(
    "Optimization Mode",
    ["AI-Powered (Hybrid)", "Rules-Only (Offline)"],
    horizontal=True,
    help="AI-Powered uses Gemini API with automatic fallback. Rules-Only works fully offline."
)
st.markdown("")
uploaded_file = st.file_uploader("Or upload a .py file", type=["py"])

# -------------------- LAYOUT --------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Input Code")

    # Pre-fill from uploaded file
    default_code = ""
    if uploaded_file is not None:
        default_code = uploaded_file.read().decode("utf-8")
        uploaded_file.seek(0)

    code_input = st.text_area(
        "",
        value=default_code,
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
        if opt_mode == "AI-Powered (Hybrid)":
            result = api.api_client.optimize(code_input)
        else:
            result = api.api_client.optimize_rules_only(code_input)
        st.session_state.result = result

elif bench and code_input.strip():
    with st.spinner("Benchmarking (Rules-Only)..."):
        result = api.api_client.optimize_rules_only(code_input)
        st.session_state.result = result

result = st.session_state.result

# -------------------- ERROR HANDLING --------------------
if result and result.get("error"):
    st.error(result["error"])
    st.stop()

# -------------------- OUTPUT --------------------
if result and result.get("optimized_code"):
    optimized_code = result["optimized_code"]
    output_placeholder.code(optimized_code, language="python")

    # Download button
    st.download_button(
        label="Download Optimized Code",
        data=optimized_code,
        file_name="optimized_code.py",
        mime="text/x-python"
    )

    # -------------------- TABS --------------------
    tab_code, tab_perf, tab_rules, tab_safety, tab_ai = st.tabs([
        "Code Diff", "Performance", "Rules Detected", "Safety & Confidence", "AI Explanation"
    ])

    # ---- TAB: Code Diff ----
    with tab_code:
        diff_col1, diff_col2 = st.columns(2)
        with diff_col1:
            st.markdown("**Original**")
            st.code(result.get("original_code", ""), language="python")
        with diff_col2:
            st.markdown("**Optimized**")
            st.code(optimized_code, language="python")

        # Show explainability diff if available
        explainability = result.get("explainability")
        if explainability:
            transform = explainability.get("transformation", {})
            st.markdown(f"""
            **Lines:** {transform.get('original_lines', '?')} -> {transform.get('optimized_lines', '?')}
            (net change: {transform.get('net_change', '?')})
            """)

    # ---- TAB: Performance ----
    with tab_perf:
        metrics = result.get("benchmarks") or {}

        if metrics:
            orig = metrics.get("original") or {}
            opt = metrics.get("optimized") or {}

            orig_ms = orig.get("runtime_ms")
            opt_ms = opt.get("runtime_ms")
            orig_mem = orig.get("memory_mb")
            opt_mem = opt.get("memory_mb")
            speed = metrics.get("speedup_factor")

            st.markdown("### Performance Metrics")

            m1, m2, m3 = st.columns(3)

            with m1:
                runtime_saved = f"{round(orig_ms - opt_ms, 2)} ms" if orig_ms and opt_ms else "---"
                st.markdown(f"<div class='metric-card'><div>Runtime Saved</div><div class='metric-value'>{runtime_saved}</div></div>", unsafe_allow_html=True)

            with m2:
                memory_saved = f"{round(orig_mem - opt_mem, 2)} MB" if orig_mem and opt_mem else "---"
                st.markdown(f"<div class='metric-card'><div>Memory Reduced</div><div class='metric-value'>{memory_saved}</div></div>", unsafe_allow_html=True)

            with m3:
                speedup_text = f"{round(speed, 2)}x" if speed else "---"
                st.markdown(f"<div class='metric-card'><div>Speedup Factor</div><div class='metric-value'>{speedup_text}</div></div>", unsafe_allow_html=True)

            # Gauge
            if speed:
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
        else:
            st.info("No benchmark data available for this optimization.")

    # ---- TAB: Rules Detected ----
    with tab_rules:
        rules_detected = result.get("rules_detected", [])
        if rules_detected:
            st.markdown(f"**{len(rules_detected)} optimization pattern(s) detected:**")
            for rule in rules_detected:
                rule_name = html_module.escape(rule.get("rule", "unknown"))
                message = html_module.escape(rule.get("message", ""))
                suggestion = html_module.escape(rule.get("suggestion", ""))
                line = rule.get("line", "?")
                st.markdown(f"""
                <div class='rule-tag'>
                    <strong>{rule_name}</strong> (line {line})<br>
                    {message}<br>
                    <em>Suggestion: {suggestion}</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No rule-based patterns detected in this code.")

    # ---- TAB: Safety & Confidence ----
    with tab_safety:
        safety = result.get("safety_analysis")
        confidence = result.get("confidence")

        if safety:
            verdict = safety.get("verdict", "Unknown")
            is_safe = safety.get("is_safe", False)
            css_class = "safety-ok" if is_safe else "safety-warn"
            st.markdown(f"<div class='{css_class}'>Verdict: {html_module.escape(verdict)}</div>", unsafe_allow_html=True)

            warnings = safety.get("warnings", [])
            if warnings:
                for w in warnings:
                    st.warning(f"**{w.get('type', 'Warning')}** ({w.get('severity', '?')}): {w.get('message', '')}")
            else:
                st.success("No safety warnings. Optimization is safe to apply.")
        else:
            st.info("Safety analysis not available for this mode.")

        if confidence:
            st.markdown("---")
            overall = confidence.get("overall", 0)
            level = confidence.get("confidence_level", "?")
            recommendation = confidence.get("recommendation", "?")

            st.markdown(f"**Confidence Score: {overall}/100** ({level})")
            st.progress(min(overall / 100.0, 1.0))
            st.markdown(f"**Recommendation:** {recommendation}")

            breakdown = confidence.get("breakdown", {})
            if breakdown:
                bd1, bd2, bd3 = st.columns(3)
                with bd1:
                    st.metric("Rule Certainty", f"{breakdown.get('rule_certainty', 0)}/40")
                with bd2:
                    st.metric("Speedup Gain", f"{breakdown.get('speedup_gain', 0)}/40")
                with bd3:
                    st.metric("Benchmark Stability", f"{breakdown.get('benchmark_stability', 0)}/20")
        else:
            st.info("Confidence scoring not available for this mode.")

    # ---- TAB: AI Explanation ----
    with tab_ai:
        ai_explanation = result.get("ai_explanation")
        if ai_explanation:
            # Escape HTML to prevent XSS from AI-generated content
            safe_explanation = html_module.escape(ai_explanation)
            st.markdown(f"""
            <div class="ai-panel">
                <h3>AI Analysis</h3>
                <p>{safe_explanation}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("AI explanation not available. The Gemini API may be unavailable.")

    # ---- Mode indicator ----
    mode = result.get("mode", "UNKNOWN")
    st.caption(f"Mode: {mode} | Timestamp: {result.get('timestamp', 'N/A')}")
