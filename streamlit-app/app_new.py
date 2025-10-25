import streamlit as st
import openai
from datetime import datetime
import json
import random
import time
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session states if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_status" not in st.session_state:
    st.session_state.system_status = {
        'core': 'ONLINE',
        'memory': 'OPTIMAL',
        'processing': 'READY'
    }

# Load intents
def load_intents():
    intents_path = Path(__file__).parent.parent / "data" / "intents.json"
    try:
        with open(intents_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        # Use absolute path as fallback
        alt_path = Path("C:/Users/ms130/OneDrive/Desktop/AI CHATBOT/data/intents.json")
        with open(alt_path, "r") as file:
            return json.load(file)

if 'intents' not in st.session_state:
    st.session_state['intents'] = load_intents()

# Page configuration
st.set_page_config(
    page_title="Villie - Your AI Assistant",
    page_icon="🤖",
    layout="centered",
)

# Custom CSS
st.markdown("""
<style>
.stApp {
    max-width: 800px;
    margin: 0 auto;
    background: linear-gradient(to bottom, #1a1a1a, #2d2d2d);
}
.css-1y4p8pa {
    padding: 2rem 1rem;
}
.css-1v0mbdj {
    width: 100%;
}
.css-1p05t8e {
    border-radius: 15px;
    border: 2px solid #00ff00;
    padding: 15px;
    margin-bottom: 10px;
    background: rgba(0, 0, 0, 0.7);
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}
.message-container {
    display: flex;
    margin-bottom: 10px;
}
.user-message {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 12px;
    border-radius: 10px;
    margin-left: auto;
    max-width: 70%;
    border: 1px solid #404040;
}
.bot-message {
    background-color: #1a1a1a;
    color: #00ff00;
    padding: 12px;
    border-radius: 10px;
    margin-right: auto;
    max-width: 70%;
    border: 1px solid #00ff00;
    font-family: 'Courier New', monospace;
    position: relative;
}
.bot-message::before {
    content: '>';
    color: #00ff00;
    position: absolute;
    left: -20px;
    top: 50%;
    transform: translateY(-50%);
}
.st-emotion-cache-1wmy9hl, .st-emotion-cache-16txtl3 {
    background: rgba(0, 0, 0, 0.6) !important;
    color: #00ff00 !important;
    border: 1px solid #00ff00 !important;
}
.st-emotion-cache-1wmy9hl:hover, .st-emotion-cache-16txtl3:hover {
    border-color: #00ff00 !important;
    color: #ffffff !important;
}
.st-emotion-cache-183lzff {
    color: #00ff00 !important;
}
.st-emotion-cache-10trblm {
    color: #00ff00 !important;
    text-align: center;
    font-family: 'Courier New', monospace;
}
.status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    background-color: #00ff00;
    border-radius: 50%;
    margin-right: 8px;
    animation: blink 1.5s infinite;
}
@keyframes blink {
    0% { opacity: 1; }
    50% { opacity: 0.3; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

def get_bot_response(user_message):
    # Simulate processing time for robot-like behavior
    time.sleep(0.5)
    
    # First try to find a matching intent
    for intent in st.session_state['intents']['intents']:
        if any(pattern.lower() in user_message.lower() for pattern in intent['patterns']):
            return f"[RESPONSE PROTOCOL ACTIVATED] >> {random.choice(intent['responses'])}"

    # If no matching intent found, use OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are VILLIE, an advanced AI robot assistant. You should:
                    1. Always start responses with a system-like prefix like [PROCESSING], [ANALYZING], or [RESPONDING]
                    2. Use technical, robotic language but remain helpful and friendly
                    3. Occasionally include robot-like emojis (🤖, ⚡, 🔋, 💫)
                    4. Include status updates or processing indicators
                    5. End responses with a clear indication that you're ready for the next input"""
                },
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "I apologize, but I'm having trouble processing your request. Please try again later."

# Chat interface
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: #00ff00; font-family: "Courier New", monospace;'>
            <span class='status-indicator'></span>
            VILLIE v1.0 [ONLINE]
        </h1>
        <p style='color: #00ff00; font-family: "Courier New", monospace;'>
            SYSTEM STATUS: OPERATIONAL<br>
            CORE FUNCTIONS: ACTIVE<br>
            READY TO ASSIST
        </p>
    </div>
""", unsafe_allow_html=True)

# Add some vertical space
st.markdown("<br><br>", unsafe_allow_html=True)

# Display system status in sidebar
with st.sidebar:
    st.markdown("""
        <div style='background-color: rgba(0,0,0,0.7); padding: 20px; border: 1px solid #00ff00; border-radius: 10px;'>
            <h3 style='color: #00ff00; font-family: "Courier New", monospace;'>SYSTEM STATUS</h3>
            <div style='font-family: "Courier New", monospace; color: #00ff00;'>
                <p>CORE: <span class='status-indicator'></span> ONLINE</p>
                <p>MEMORY: <span class='status-indicator'></span> OPTIMAL</p>
                <p>PROCESSING: <span class='status-indicator'></span> READY</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("⚡ RESET SYSTEM", key="reset_button"):
        st.session_state.messages = []
        st.experimental_rerun()

# Display chat messages
for message in st.session_state.messages:
    is_user = message['role'] == 'user'
    
    if is_user:
        message_html = f"""
            <div class='message-container'>
                <div class='user-message'>
                    <span style='color: #888;'>[USER]:</span> {message['content']}
                </div>
            </div>
        """
    else:
        message_html = f"""
            <div class='message-container'>
                <div class='bot-message'>
                    <span style='color: #00ff00;'>[VILLIE]:</span> {message['content']}
                </div>
            </div>
        """
    st.markdown(message_html, unsafe_allow_html=True)

# Chat input
with st.container():
    col1, col2 = st.columns([5,1])
    
    with col1:
        # Get the user input without using session state
        user_input = st.text_input(
            "User Input",
            value="",
            placeholder="Enter command...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("SEND", key="send_button")

    if send_button and user_input:
        # Store current input
        current_message = user_input
        
        # Update system status
        st.session_state.system_status['processing'] = 'ACTIVE'
        
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": current_message,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        })
        
        # Get bot response
        with st.spinner("🤖 PROCESSING..."):
            bot_response = get_bot_response(current_message)
        
        # Add bot response
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        })
        
        # Reset system status
        st.session_state.system_status['processing'] = 'READY'
        st.experimental_rerun()

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()