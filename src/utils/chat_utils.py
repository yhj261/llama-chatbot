from langchain.schema import HumanMessage, AIMessage, SystemMessage
import streamlit as st
from langchain_openai import ChatOpenAI


def get_agent(llm, agent):
    from agents.data_research import get_graph

    graph = get_graph(llm)
    return graph


def get_query_messages(messages):
    """Convert chat messages to LangChain message format"""
    query_messages = []
    if "system_message" in st.session_state:
        query_messages.append(SystemMessage(content=st.session_state.system_message))

    for message in messages:
        if message["role"] == "user":
            query_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            query_messages.append(AIMessage(content=message["content"]))
    return query_messages


def create_chat_client(settings, model_host="http://localhost:11434/v1", agent=None):
    """Create and configure the chat client"""
    llm = ChatOpenAI(
        base_url=model_host,
        api_key="dummy",
        # model="deepseek-r1:32b",
        model="llama3.1",
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"],
        top_p=settings["top_p"] + 1e-3,
        frequency_penalty=settings["repeat_penalty"],
        presence_penalty=settings["presence_penalty"],
        # streaming=True,
    )

    if agent == "Data Agent":
        return get_agent(llm, agent)

    return llm
