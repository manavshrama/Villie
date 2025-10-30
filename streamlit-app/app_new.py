import streamlit as st
import openai
from datetime import datetime
import json
import random
import time
from pathlib import Path
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_status" not in st.session_state:
    st.session_state.system_status = {
        'core': 'ONLINE',
        'memory': 'OPTIMAL',
        'processing': 'READY'
    }

if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = None

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

# Load intents
def load_intents():
    intents_path = Path(__file__).parent.parent / "data" / "intents.json"
    try:
        with open(intents_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        alt_path = Path("C:/Users/ms130/OneDrive/Desktop/AI CHATBOT/data/intents.json")
        with open(alt_path, "r") as file:
            return json.load(file)

if 'intents' not in st.session_state:
    st.session_state['intents'] = load_intents()

# Page configuration
st.set_page_config(
    page_title="Villie - Your AI Assistant with Dashboard",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
.stApp {
    max-width: 1200px;
    margin: 0 auto;
    background: linear-gradient(to bottom, #1a1a1a, #2d2d2d);
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
.dashboard-container {
    background-color: rgba(0,0,0,0.8);
    border: 1px solid #00ff00;
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

def parse_markdown_table(text):
    """Parse markdown table from text and return pandas DataFrame"""
    lines = text.split('\n')
    table_lines = []
    in_table = False
    
    for line in lines:
        if '|' in line and not line.startswith('#'):
            table_lines.append(line)
            in_table = True
        elif in_table and line.strip() == '':
            break
    
    if len(table_lines) < 2:
        return None
    
    # Extract headers
    headers = [col.strip() for col in table_lines[0].split('|')[1:-1]]
    
    # Extract data rows
    data = []
    for line in table_lines[2:]:
        if '|' in line:
            row = [col.strip() for col in line.split('|')[1:-1]]
            if len(row) == len(headers):
                data.append(row)
    
    if not data:
        return None
    
    try:
        df = pd.DataFrame(data, columns=headers)
        # Try to convert numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
        return df
    except:
        return None

def detect_dashboard_keywords(text):
    """Detect if response contains dashboard-related keywords"""
    keywords = ['table', 'chart', 'graph', 'plot', 'data', 'statistics', 'analytics', 'visualization', 'dashboard']
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

def create_dashboard(df):
    """Create interactive dashboard from DataFrame"""
    if df is None or df.empty:
        return None
    
    # Determine chart type based on data
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    charts = []
    
    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        # Bar chart for categorical vs numeric
        fig = px.bar(df, x=categorical_cols[0], y=numeric_cols[0], 
                    title=f"{numeric_cols[0]} by {categorical_cols[0]}")
        charts.append(fig)
    
    if len(numeric_cols) >= 2:
        # Scatter plot for numeric vs numeric
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
        charts.append(fig)
    
    if len(numeric_cols) >= 1:
        # Histogram for numeric data
        fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
        charts.append(fig)
    
    return charts

def process_documents(uploaded_files):
    """Process uploaded documents and create vector store"""
    documents = []
    
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            loader = PyPDFLoader(uploaded_file)
            documents.extend(loader.load())
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
            documents.append(Document(page_content=text, metadata={"source": uploaded_file.name}))
    
    if documents:
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        rag_chain = ConversationalRetrievalChain.from_llm(
            llm=OpenAI(temperature=0.7),
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        
        return vectorstore, rag_chain
    
    return None, None

def get_bot_response(user_message, model="gpt-3.5-turbo", temperature=0.7, use_rag=False):
    time.sleep(0.5)
    
    # First try to find a matching intent
    for intent in st.session_state['intents']['intents']:
        if any(pattern.lower() in user_message.lower() for pattern in intent['patterns']):
            return f"[RESPONSE PROTOCOL ACTIVATED] >> {random.choice(intent['responses'])}"

    # Use RAG if available and enabled
    if use_rag and st.session_state.rag_chain:
        try:
            response = st.session_state.rag_chain({"question": user_message})
            return response["answer"]
        except Exception as e:
            st.warning(f"RAG processing failed: {e}")
    
    # Use OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": """You are VILLIE, an advanced AI robot assistant with data analysis capabilities. You should:
                    1. Always start responses with a system-like prefix like [PROCESSING], [ANALYZING], or [RESPONDING]
                    2. Use technical, robotic language but remain helpful and friendly
                    3. Occasionally include robot-like emojis (🤖, ⚡, 🔋, 💫)
                    4. Include status updates or processing indicators
                    5. When providing data or statistics, format them as markdown tables when appropriate
                    6. End responses with a clear indication that you're ready for the next input
                    
                    If the user asks for data analysis, charts, or visualizations, provide the data in markdown table format so the dashboard can automatically generate charts."""
                },
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "I apologize, but I'm having trouble processing your request. Please try again later."

# Sidebar configuration
with st.sidebar:
    st.markdown("""
        <div style='background-color: rgba(0,0,0,0.7); padding: 20px; border: 1px solid #00ff00; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: #00ff00; font-family: "Courier New", monospace;'>SYSTEM STATUS</h3>
            <div style='font-family: "Courier New", monospace; color: #00ff00;'>
                <p>CORE: <span class='status-indicator'></span> ONLINE</p>
                <p>MEMORY: <span class='status-indicator'></span> OPTIMAL</p>
                <p>PROCESSING: <span class='status-indicator'></span> READY</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Model selection
    model = st.selectbox("AI Model", ["gpt-3.5-turbo", "gpt-4-turbo"], index=0)
    
    # Randomness slider
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    
    # Document upload
    uploaded_files = st.file_uploader("Upload Knowledge Base (PDF/TXT)", 
                                    type=["pdf", "txt"], 
                                    accept_multiple_files=True)
    
    if uploaded_files and st.button("Process Documents"):
        with st.spinner("Processing documents..."):
            vectorstore, rag_chain = process_documents(uploaded_files)
            if vectorstore:
                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = rag_chain
                st.success("Documents processed successfully!")
    
    # Dashboard toggle
    dashboard_enabled = st.checkbox("Enable Auto-Dashboard", value=True)
    
    # Clear buttons
    if st.button("⚡ RESET SYSTEM"):
        st.session_state.messages = []
        st.session_state.dashboard_data = None
        st.session_state.show_dashboard = False
        st.rerun()
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #00ff00; font-family: "Courier New", monospace;'>
                <span class='status-indicator'></span>
                VILLIE v2.0 [ONLINE]
            </h1>
            <p style='color: #00ff00; font-family: "Courier New", monospace;'>
                SYSTEM STATUS: OPERATIONAL<br>
                CORE FUNCTIONS: ACTIVE<br>
                DASHBOARD MODULE: ENABLED<br>
                READY TO ASSIST
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Chat messages
    chat_container = st.container()
    with chat_container:
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
        col_input, col_send = st.columns([5,1])
        
        with col_input:
            user_input = st.text_input(
                "User Input",
                value="",
                placeholder="Enter command...",
                label_visibility="collapsed",
                key="user_input"
            )
        
        with col_send:
            send_button = st.button("SEND", key="send_button")
        
        if send_button and user_input:
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
                use_rag = st.session_state.vectorstore is not None
                bot_response = get_bot_response(current_message, model, temperature, use_rag)
            
            # Add bot response
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
            })
            
            # Check for dashboard generation
            if dashboard_enabled:
                df = parse_markdown_table(bot_response)
                if df is not None or detect_dashboard_keywords(bot_response):
                    st.session_state.dashboard_data = df
                    st.session_state.show_dashboard = True
            
            # Reset system status
            st.session_state.system_status['processing'] = 'READY'
            st.rerun()

with col2:
    if st.session_state.show_dashboard and st.session_state.dashboard_data is not None:
        st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
        st.markdown("### 📊 Auto-Generated Dashboard")
        
        charts = create_dashboard(st.session_state.dashboard_data)
        if charts:
            for i, chart in enumerate(charts):
                st.plotly_chart(chart, use_container_width=True, key=f"chart_{i}")
        else:
            st.info("No chartable data found in the response.")
        
        if st.button("Hide Dashboard"):
            st.session_state.show_dashboard = False
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    elif st.session_state.show_dashboard:
        st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
        st.markdown("### 📊 Dashboard Ready")
        st.info("Dashboard triggered but no table data found. Try asking for data analysis!")
        if st.button("Hide Dashboard"):
            st.session_state.show_dashboard = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
