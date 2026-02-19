import streamlit as st
from utils.auth import authenticate, is_authed, logout

st.set_page_config(
    page_title="CodeForge",
    layout="centered"
)

# If already logged in
if is_authed():
    st.warning("You are already logged in.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Dashboard", use_container_width=True):
            st.switch_page("pages/1_Dashboard.py")
    with col2:
        if st.button("Logout", use_container_width=True):
            logout()

    st.stop()

# ---------- Styling ----------
st.markdown("""
<style>
#MainMenu, header, footer {visibility:hidden;}

.block-container {
    padding-top: 6rem;
    max-width: 420px;
}

.login-card {
    background: #18181F;
    padding: 40px;
    border-radius: 16px;
    border: 1px solid #26262E;
}

h1 {
    font-weight: 700;
    font-size: 28px;
    margin-bottom: 4px;
}

.subtitle {
    color: #9CA3AF;
    font-size: 14px;
    margin-bottom: 28px;
}

.stTextInput>div>div>input {
    background-color: #0F0F14;
    border: 1px solid #26262E;
    border-radius: 10px;
    height: 44px;
    color: #E5E7EB;
}

.stTextInput>div>div>input:focus {
    border: 1px solid #7C3AED;
    box-shadow: none;
}

.stButton>button {
    background: #7C3AED;
    border: none;
    border-radius: 10px;
    height: 44px;
    font-weight: 600;
}

.stButton>button:hover {
    background: #6D28D9;
}
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.markdown("<h1>CodeForge</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sign in to continue</div>", unsafe_allow_html=True)

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Sign In", use_container_width=True):
    user = authenticate(username.strip(), password)

    if user:
        st.session_state["auth"] = {
            "is_auth": True,
            "user": user
        }
        st.switch_page("pages/1_Dashboard.py")
    else:
        st.error("Invalid credentials.")