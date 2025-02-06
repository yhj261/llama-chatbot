import streamlit as st
from chat_interface import display_chat_interface

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "model" not in st.session_state:
    st.session_state.model = "Llama-3.1-8B-Instruct"

display_chat_interface()
