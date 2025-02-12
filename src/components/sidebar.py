import streamlit as st


def render_settings_tab():
    """Render the settings tab in the sidebar"""
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

    return {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "presence_penalty": presence_penalty,
    }


def render_agents_tab():
    """Render the agents tab in the sidebar"""
    # Select LLM Agent
    agent = st.selectbox("Select LLM Agent", ["ChatBot", "RAG Agent", "Data Agent"])

    # Sidebar Model Parameters
    if agent == "RAG Agent":
        st.header("RAG Agent Options")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload")
        search_query = st.text_input("Search PDF Content", key="search_query")
        search_result = st.text_area("Search Result", "", key="search_result")

    # System Message Customization
    st.header("System Message")
    st.session_state.system_message = st.text_area(
        "Enter system message", "You are a helpful AI assistant."
    )

    if st.button("Clear Chat", type="primary"):
        st.session_state.messages = []

    return agent


def render_sidebar():
    """Render the complete sidebar"""
    st.sidebar.header("Settings")

    tab1, tab2 = st.sidebar.tabs(["Agents", "Settings"])

    with tab1:
        agent = render_agents_tab()

    with tab2:
        settings = render_settings_tab()

    return agent, settings
