import streamlit as st
import requests
import base64
import pyttsx3
import threading
import io
from fpdf import FPDF
from textblob import TextBlob
from streamlit_mic_recorder import speech_to_text

# --- PAGE CONFIG ---
st.set_page_config(page_title="Prometheus AI", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- NATIVE APP CSS (STRICT BRANDING REMOVAL) ---
st.markdown("""
<style>
    header, footer, .stDeployButton, #MainMenu {visibility: hidden !important;}
    .block-container {padding: 2rem 3rem !important;}
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Space+Mono&display=swap');
    html, body, [class*="st-"] {font-family: 'Rajdhani', sans-serif !important; color: #ffffff;}
    .stApp {background-color: #050505;} 
    .stChatMessage {
        background: rgba(15, 22, 35, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 243, 255, 0.2) !important;
        border-radius: 20px !important;
        margin-bottom: 15px !important;
    }
    .stChatInputContainer textarea {
        background: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid rgba(0, 243, 255, 0.4) !important;
        border-radius: 30px !important;
        color: white !important;
    }
    h1 {font-size: 3.5rem !important; background: linear-gradient(90deg, #fff, #00f3ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {font-family: 'Space Mono', monospace; font-size: 0.8rem; color: #00f3ff; opacity: 0.8; letter-spacing: 2px;}
</style>
""", unsafe_allow_html=True)

# --- SIRI VOICE ENGINE ---
def speak_text(text, enabled):
    if not enabled: return
    def run_speech():
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            siri = next((v.id for v in voices if "Samantha" in v.name), voices[0].id)
            engine.setProperty('voice', siri)
            engine.setProperty('rate', 185)
            engine.say(text)
            engine.runAndWait()
        except: pass
    threading.Thread(target=run_speech, daemon=True).start()

# --- PDF GENERATION (FIXED FOR HORIZONTAL SPACE) ---
def create_pdf(messages):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=10, top=10, right=10) # Explicit margins
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(w=0, h=10, txt="PROMETHEUS AI ARCHIVE", ln=1, align='C')
    pdf.ln(5)
    
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    for msg in messages:
        role = "USER" if msg['role'] == "user" else "AI"
        # Aggressive cleaning for standard PDF fonts
        clean_text = msg['content'].encode('ascii', 'ignore').decode('ascii')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.multi_cell(w=effective_page_width, h=8, txt=f"--- {role} ---", align='L')
        pdf.set_font("Arial", size=10)
        # Fixed width multi_cell prevents "Not enough horizontal space" error
        pdf.multi_cell(w=effective_page_width, h=6, txt=clean_text)
        pdf.ln(4)
        
    return pdf.output(dest='S')

# --- BG IMAGE ---
def load_bg(img_file):
    try:
        with open(img_file, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), url("data:image/png;base64,{b64}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)
    except: pass

load_bg("likithroy.png")

# --- INITIALIZE STATE ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ NEURAL CONTROL")
    v_on = st.toggle("Neural Siri Voice", value=True)
    if st.button("🛑 STOP AUDIO"): pyttsx3.init().stop()
    
    st.markdown("---")
    st.markdown("### 📥 DATA EXPORT")
    if st.session_state.messages:
        try:
            pdf_out = create_pdf(st.session_state.messages)
            st.download_button("Download Session PDF", data=bytes(pdf_out), file_name="Archive.pdf", mime="application/pdf")
        except Exception as e:
            st.error("PDF Space Error. Try shorter messages.")

    st.markdown("---")
    st.markdown("### 🎓 QUIZ MODE")
    q_topic = st.text_input("Test Subject:")
    if st.button("Generate Test"):
        res = requests.post("http://127.0.0.1:8000/generate-quiz", json={"prompt": q_topic})
        st.session_state.messages.append({"role": "assistant", "content": f"QUIZ MODE:\n{res.json()['quiz']}"})
        st.rerun()

    st.markdown("---")
    v_prompt = speech_to_text(language='en', start_prompt="🎤 MIC INPUT", stop_prompt="⏹️ PROCESS", key='STT')

# --- HEADER ---
st.markdown("<h1>PROMETHEUS AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>SYSTEM ARCHITECT: LIKITH NAIDU ANUMAKONDA</div>", unsafe_allow_html=True)

# --- CHAT ENGINE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"]=="assistant" else "👤"):
        st.markdown(msg["content"])

user_input = st.chat_input("Connect with Prometheus...")
prompt = user_input or v_prompt

if user_input:
    # TextBlob Spellchecker logic
    corrected = str(TextBlob(user_input).correct())
    if corrected.lower() != user_input.lower():
        st.info(f"💡 Suggestion: **{corrected}**")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        try:
            response = requests.post("http://127.0.0.1:8000/chat", json={"prompt": prompt})
            ai_msg = response.json().get("response", "Error.")
            placeholder.markdown(ai_msg)
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            if v_on: speak_text(ai_msg, v_on)
        except: st.error("Neural Link Offline.")
