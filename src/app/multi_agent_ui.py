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
st.set_page_config(page_title="Chatbot", layout="wide")

# Sidebar Configuration
st.sidebar.header("Settings")

# Select LLM Agent
model = st.sidebar.selectbox("Select LLM Agent", ["ChatBot", "RAG Agent", "Data Agent"])

model_param_expander = st.sidebar.expander("Model Parameters")

# Temperature Slider
temperature = model_param_expander.slider("Temperature", 0.0, 1.0, 0.7, 0.05)

# Max Token Slider
max_tokens = model_param_expander.slider("Max Tokens", 1024, 4096 * 2, 4096, 1024)

# Top_p Slider
top_p = model_param_expander.slider("Top-p", 0.0, 1.0, 1.0, 0.05)

# Clear Chat Button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

# System Message Customization
st.sidebar.header("System Message")
st.session_state.system_message = st.sidebar.text_area(
    "Enter system message", "You are a helpful AI assistant."
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat Messages
st.title("My Chatbot")
st.write(f"Interact with an AI-powered {model}")

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
        model="llama3.1",
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
