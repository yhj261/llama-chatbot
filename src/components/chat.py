import streamlit as st
from utils.chat_utils import get_query_messages, create_chat_client
import base64
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import io
from PIL import Image


def display_chat_history():
    """Display all messages in the chat history"""
    # Iterate through all messages stored in the Streamlit session state
    # Each message is a dictionary with 'role' (user/assistant) and 'content' keys
    for message in st.session_state.messages:
        # Create a chat message container with the appropriate role styling
        # This will show user messages and AI responses in different styles
        with st.chat_message(message["role"]):
            # Render the message content as markdown
            # This allows for rich text formatting in the messages
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
    events = client.stream(data, config=config, stream_mode="values")

    for event in events:
        if not "messages" in event:
            continue
        message = event["messages"][-1]
        print(message.pretty_print())

        if isinstance(message, AIMessage):
            content = message.content
            print(content)
            # Check if content contains an image tag
            if "<plot>" in content:
                # Extract the image path between the tags
                img_start = content.find("<plot>") + 6
                img_end = content.find("</plot>")
                img_path = content[img_start:img_end]

                # Read and display the image using st.image
                with st.chat_message("assistant"):
                    st.markdown("Plotting...")
                    st.image(img_path)

                # Remove the image tags from the content for text display
                content = content[: img_start - 6] + content[img_end + 7 :]

            # Display any remaining text content
            if content.strip():
                with st.chat_message("assistant"):
                    st.markdown(content)
                    # Store the original content in session state
                    st.session_state.messages.append(
                        {"role": "assistant", "content": content}
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
