import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import toml
import PyPDF2
from io import BytesIO
import requests

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Gemini PDF Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .bot-message {
            background-color: #f0f2f6;
        }
        .user-message {
            background-color: #e8f0fe;
        }
    </style>
""", unsafe_allow_html=True)

def load_pdf_from_url(url):
    """Load PDF content from a URL"""
    response = requests.get(url)
    pdf_file = BytesIO(response.content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def load_pdf_from_file(file):
    """Load PDF content from an uploaded file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

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
    st.session_state.pdf_content = None

def initialize_chat():
    chat = model.start_chat(history=[])
    return chat

if "chat" not in st.session_state:
    st.session_state.chat = initialize_chat()

# Title and description
st.title("📚 Gemini PDF Assistant")
st.markdown("I'm your AI assistant powered by Google's Gemini model and trained on the Gemini Prompting Guide. How can I help you today?")

# Sidebar with PDF loading options
with st.sidebar:
    st.header("Configuration")
    
    # Option to use local PDF upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        st.session_state.pdf_content = load_pdf_from_file(uploaded_file)
        st.success("PDF loaded successfully!")
        
    # Option to load PDF from GitHub
    if st.button("Load Prompting Guide from GitHub"):
        pdf_url = "https://github.com/tjbeevor/chatterbox/blob/main/gemini_for_workspace_prompt_guide_october_2024_digital_final.pdf"  # Replace with your PDF URL
        try:
            st.session_state.pdf_content = load_pdf_from_url(pdf_url)
            st.success("Prompting guide loaded successfully!")
        except Exception as e:
            st.error(f"Error loading PDF: {str(e)}")
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.chat = initialize_chat()
        st.rerun()

# Display chat history
for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
                <div class="chat-message user-message">
                    <b>You:</b><br>{message["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message bot-message">
                    <b>Assistant:</b><br>{message["content"]}
                </div>
            """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    if not st.session_state.pdf_content:
        st.warning("Please load a PDF first!")
        st.stop()
        
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    try:
        # Create prompt with context from PDF
        prompt = f"""Based on the following PDF content:

{st.session_state.pdf_content[:10000]}  # Limiting context size

User question: {user_input}

Please provide a relevant and accurate response based on the PDF content."""
        
        # Get response from Gemini
        response = st.session_state.chat.send_message(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        
        # Rerun to update the display
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
