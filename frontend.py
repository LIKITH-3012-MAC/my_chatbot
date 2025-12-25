import streamlit as st
import requests
import base64
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Prometheus AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOAD BACKGROUND IMAGE ---
def get_base64_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- SET YOUR IMAGE NAME HERE ---
image_filename = "likithroy.png"

try:
    bg_img = get_base64_bg(image_filename)
    # OPTION A: If you want the image CLEAR, we use a lighter gradient (0.4 opacity)
    bg_css = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6)), 
                          url("data:image/png;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning(f"⚠️ Image '{image_filename}' not found. Check the folder.")

# --- THE NEW "NEO-GLASS" CSS SYSTEM ---
st.markdown("""
<style>
    /* 1. FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Space+Mono:wght@400;700&display=swap');

    /* 2. GLOBAL TEXT - HIGH CONTRAST */
    .stApp, p, h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #ffffff !important;
        text-shadow: 0px 2px 4px rgba(0,0,0, 0.9); /* Heavy shadow for readability */
    }

    /* 3. HEADER DESIGN */
    h1 {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        background: linear-gradient(to right, #ffffff, #00f3ff); /* White to Cyan gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 30px rgba(0, 243, 255, 0.5); /* Glow */
        margin-bottom: 0 !important;
    }
    
    .subtitle {
        font-family: 'Space Mono', monospace;
        font-size: 1rem;
        color: #00f3ff;
        letter-spacing: 3px;
        background: rgba(0,0,0,0.6);
        padding: 5px 10px;
        border-radius: 4px;
        display: inline-block;
    }

    /* 4. CHAT BUBBLES - FROSTED GLASS */
    .stChatMessage {
        background: rgba(20, 25, 40, 0.75); /* Semi-transparent dark blue */
        backdrop-filter: blur(15px);        /* The Blur Effect */
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* User Bubble Accent */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        border-left: 4px solid #00f3ff; /* Cyan for User */
    }
    /* AI Bubble Accent */
    div[data-testid="stChatMessage"]:nth-child(even) {
        border-right: 4px solid #ff4500; /* Orange for AI */
    }

    /* 5. CODE BLOCKS */
    .stCodeBlock {
        border-radius: 8px !important;
        border: 1px solid #444;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    code {
        font-family: 'Space Mono', monospace !important;
    }

    /* 6. INPUT FIELD - FLOATING CAPSULE */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .stChatInputContainer textarea {
        background-color: rgba(0, 0, 0, 0.8) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 25px !important; /* Rounded Capsule */
    }
    .stChatInputContainer textarea:focus {
        border-color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.4) !important;
    }
    
    /* 7. AVATARS */
    .stAvatar {
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }

</style>
""", unsafe_allow_html=True)

# --- HEADER AREA ---
col1, col2 = st.columns([1.5, 10])
with col1:
    # Animated Hologram Logo
    st.markdown("<div style='font-size: 60px; text-shadow: 0 0 20px cyan;'>⚡</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<h1>PROMETHEUS AI</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>SYSTEM ARCHITECT: LIKITH NAIDU ANUMAKONDA</div>", unsafe_allow_html=True)

st.markdown("---") # Visual Divider

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "⚡"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("Accessing Neural Network..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        placeholder.markdown("`CALCULATING...`")
        
        try:
            response = requests.post(
                "http://localhost:8000/chat", 
                json={"prompt": prompt, "model": "llama3.2"}
            )
            
            if response.status_code == 200:
                ai_msg = response.json().get("response", "Error")
                placeholder.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            else:
                placeholder.error("System Failure.")
        except:
            placeholder.error("Backend Offline.")