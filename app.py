import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import toml
import PyPDF2
from io import BytesIO
import requests
import time

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Gemini Prompting Guide Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for professional appearance
st.markdown("""
    <style>
        /* Main container styling */
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        .main-header {
            padding: 2rem 0;
            text-align: center;
            background: linear-gradient(120deg, #4285f4, #34a853);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Chat message container */
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Message bubbles */
        .chat-message {
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            animation: fadeIn 0.5s ease-in-out;
        }
        
        /* User message styling */
        .user-message {
            justify-content: flex-end;
        }
        
        .user-message .message-content {
            background: #E3F2FD;
            margin-left: 2rem;
            border-radius: 20px 20px 0 20px;
        }
        
        /* Assistant message styling */
        .assistant-message {
            justify-content: flex-start;
        }
        
        .assistant-message .message-content {
            background: #F5F5F5;
            margin-right: 2rem;
            border-radius: 20px 20px 20px 0;
        }
        
        /* Message content */
        .message-content {
            padding: 1rem 1.5rem;
            max-width: 80%;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Avatar styling */
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin: 0 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        /* Sidebar styling */
        .sidebar-content {
            background: #FAFAFA;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Input box styling */
        .stTextInput input {
            border-radius: 20px;
            border: 2px solid #E0E0E0;
            padding: 10px 20px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            border-color: #4285f4;
            box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 20px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        /* Loading animation */
        .loading-dots {
            display: inline-block;
        }
        
        .loading-dots::after {
            content: '.';
            animation: dots 1.5s steps(5, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80% { content: '....'; }
            100% { content: '.....'; }
        }
    </style>
""", unsafe_allow_html=True)

def load_pdf_from_github():
    """Load the Gemini Prompting Guide PDF from GitHub"""
    # Raw GitHub URL for the PDF
    pdf_url = "https://raw.githubusercontent.com/tjbeevor/chatterbox/main/gemini_for_workspace_prompt_guide_october_2024_digital_final.pdf"
    
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"  # Add spacing between pages
        return text
    except Exception as e:
        st.error(f"Error loading PDF from GitHub: {str(e)}")
        return None

# Initialize Gemini
try:
    config = toml.load(".streamlit/secrets.toml")
    genai.configure(api_key=config["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("Error loading API key. Please check your configuration.")
    st.stop()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = load_pdf_from_github()

def initialize_chat():
    chat = model.start_chat(history=[])
    return chat

if "chat" not in st.session_state:
    st.session_state.chat = initialize_chat()

# Enhanced Header
st.markdown("""
    <div class="main-header">
        <h1>✨ Gemini Prompting Guide Assistant</h1>
        <p>Your AI companion for mastering Gemini prompts</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with professional styling
with st.sidebar:
    st.markdown("""
        <div class="sidebar-content">
            <h2>🎯 About</h2>
            <p>Powered by Google's Gemini model and trained on the October 2024 Prompting Guide.</p>
            <hr>
            <h3>📚 Guide Contents</h3>
            <ul>
                <li>Writing effective prompts</li>
                <li>Best practices by role</li>
                <li>Real-world use cases</li>
                <li>Advanced techniques</li>
            </ul>
            <hr>
            <p><em>Version 1.0 - Based on October 2024 Edition</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.chat = initialize_chat()
        st.rerun()

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history with enhanced styling
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">
                    <b>You</b><br>
                    {message["content"]}
                </div>
                <div class="avatar" style="background-color: #E3F2FD;">👤</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="avatar" style="background-color: #F5F5F5;">🤖</div>
                <div class="message-content">
                    <b>Assistant</b><br>
                    {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask me anything about Gemini prompting...")

if user_input:
    if not st.session_state.pdf_content:
        st.error("Error: Unable to load the prompting guide. Please try again later.")
        st.stop()
        
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    try:
        # Create prompt with context from PDF
        prompt = f"""You are an AI assistant specifically trained on the Gemini Prompting Guide (October 2024 edition). 
        Use the following content from the guide to provide accurate, helpful responses:

        {st.session_state.pdf_content}

        User question: {user_input}

        Please provide a relevant and accurate response based on the prompting guide. If the question isn't 
        covered in the guide, politely indicate that and stick to information that is contained in the guide."""
        
        # Get response from Gemini
        response = st.session_state.chat.send_message(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        
        # Rerun to update the display
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
