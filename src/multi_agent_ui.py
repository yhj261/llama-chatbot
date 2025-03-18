import streamlit as st
from components.sidebar import render_sidebar
from components.chat import render_chat_interface
from components.sn_agent import render_sn_agent_interface


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():
    # Streamlit UI Setup
    st.set_page_config(page_title="Multi-Agent ChatBot", layout="wide")

    # Initialize session state
    init_session_state()

    # Get sidebar configuration
    agent, settings = render_sidebar()

    # Render appropriate interface based on selected agent
    if agent == "SN Agent":
        # Render the SN Agent interface
        render_sn_agent_interface()
    else:
        # Render main chat interface
        render_chat_interface(settings, agent)


if __name__ == "__main__":
    main()
