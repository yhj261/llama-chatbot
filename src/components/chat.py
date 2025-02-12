import streamlit as st
from utils.chat_utils import get_query_messages, create_chat_client


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input, settings, agent):
    """Process user input and generate AI response"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    client = create_chat_client(settings, agent=agent)

    # Stream the response
    # with st.chat_message("assistant"):
    #     message_placeholder = st.empty()
    #     full_response = ""

    #     for chunk in client.stream(get_query_messages(st.session_state.messages)):
    #         full_response += chunk.content
    #         message_placeholder.markdown(full_response + "▌")

    #     message_placeholder.markdown(full_response)
    config = {"configurable": {"user_id": "3", "thread_id": "1"}}

    data = {
        "messages": get_query_messages(st.session_state.messages),
    }
    events = client.invoke(data, config=config)
    for event in events["messages"]:
        st.markdown(event.content)
        # st.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": event.content}
        )

        # Save the response
        # st.session_state.messages.append({"role": "assistant", "content": full_response})


def render_chat_interface(settings, agent):
    """Render the main chat interface"""
    st.title("My Chatbot")
    st.write("Interact with an AI-powered Chatbot")

    # Display chat history
    display_chat_history()

    # Handle user input
    user_input = st.chat_input("Type your message...")
    if user_input:
        handle_user_input(user_input, settings, agent)
