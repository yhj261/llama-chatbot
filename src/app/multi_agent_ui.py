import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage


def get_query_messages(messages):
    query_messages = []
    if "system_message" in st.session_state:
        query_messages.append(SystemMessage(content=st.session_state.system_message))

    for message in messages:
        if message["role"] == "user":
            query_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            query_messages.append(AIMessage(content=message["content"]))
    return query_messages


# Streamlit UI Setup
st.set_page_config(page_title="Multi-Agent ChatBot", layout="wide")

# Sidebar Configuration
st.sidebar.header("Settings")

tab1, tab2 = st.sidebar.tabs(["Agents", "Settings"])

with tab2:
    # Temperature Slider
    temperature = st.slider("Temperature", 0.0, 2.0, 1.0, 0.05)

    # Max Token Slider
    max_tokens = st.slider("Max Tokens", 1024, 4096 * 2, 4096, 1024)

    # Top_p Slider
    top_p = st.slider("Top-p", 0.0, 1.0, 0.1, 0.05)

    # Penalize repetitive text
    repeat_penalty = st.slider("Repetition Penalty", 0.0, 2.0, 0.0, 0.05)

    # Encourage topic diversity
    presence_penalty = st.slider("Presence Penalty", 0.0, 2.0, 0.0, 0.05)

with tab1:
    # Select LLM Agent
    agent = st.selectbox("Select LLM Agent", ["ChatBot", "RAG Agent", "Data Agent"])

    # Sidebar Model Parameters
    if agent == "RAG Agent":
        st.header("RAG Agent Options")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload")
        search_query = st.text_input("Search PDF Content", key="search_query")
        search_result = st.text_area("Search Result", "", key="search_result")

    # Clear Chat Button

    # System Message Customization
    st.header("System Message")
    st.session_state.system_message = st.text_area(
        "Enter system message", "You are a helpful AI assistant."
    )

    if st.button("Clear Chat", type="primary"):
        st.session_state.messages = []

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat Messages
st.title("My Chatbot")
st.write(f"Interact with an AI-powered Chatbot")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Box
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    full_chat = []
    # Call OpenAI API
    client = ChatOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="dummy",
        # model="llama3.1",
        model="deepseek-r1:32b",
        temperature=temperature,  # Adjust creativity level
        max_tokens=max_tokens,  # Limit response length
        top_p=top_p,  # Nucleus sampling
        frequency_penalty=0.2,  # Penalize repetitive text
        presence_penalty=0.3,  # Encourage topic diversity
    )
    response = client.invoke(get_query_messages(st.session_state.messages))
    ai_response = response.content
    # ai_response = "This is a simulated AI response."

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
