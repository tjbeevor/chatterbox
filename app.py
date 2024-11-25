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
    page_title="Gemini Prompting Guide Assistant",
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

# Title and description
st.title("📚 Gemini Prompting Guide Assistant")
st.markdown("""
Welcome! I'm your AI assistant trained on the Gemini Prompting Guide (October 2024 edition). 
I can help you understand best practices for:
- Writing effective prompts
- Using Gemini in Google Workspace
- Creating role-specific prompts for different job functions
- And much more!

Ask me anything about the prompting guide!
""")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This assistant is powered by Google's Gemini model and is trained specifically on the 
    October 2024 Prompting Guide for Google Workspace.
    
    The guide covers:
    - Writing effective prompts
    - Best practices for different roles
    - Real-world use cases
    - Tips for leveling up your prompt writing
    """)
    
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
