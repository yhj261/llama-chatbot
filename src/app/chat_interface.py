import streamlit as st
import logging
import time
import requests

logger = logging.getLogger()

chat_api_endpoint = "http://localhost:8123/chat"


def get_api_response(query, session_id, model):
    logger.info(f"{query=}, {session_id=}, {model=}")
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    body = {"query": query, "model": model}
    if session_id:
        body["session_id"] = session_id

    resp = requests.post(chat_api_endpoint, json=body, headers=headers)
    return resp.json()


def display_chat_interface():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input("Query"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("Generating response ..."):
            resp = get_api_response(
                query, st.session_state.session_id, st.session_state.model
            )

            if resp:
                st.session_state.session_id = resp.get("session_id")
                st.session_state.messages.append(
                    {"role": "assistant", "content": resp.get("answer")}
                )

                with st.chat_message("assistant"):
                    st.markdown(resp.get("answer"))
