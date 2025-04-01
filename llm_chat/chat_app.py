import streamlit as st
import ollama
import yaml
from chat_history_manager import ChatHistoryManager
from model_selector import model_selector
from sidebar import render_sidebar, get_messages_for_chat, save_message

# Load configuration from config.yaml
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

st.set_page_config(page_title="Jarvis")
@st.fragment
def do_ollama_query(messages):
    try:
        response = ollama_client.chat(
            model=st.session_state.selected_model,
            messages=messages
        )

        assistant_response = response["message"]["content"]
        st.session_state.chats[chat_name].append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Save assistant message to the database
        save_message(st.session_state.current_chat_id, "assistant", assistant_response, mysql_config)
    except Exception as e:
        st.error(f"Error communicating with Ollama: {e}")

#def load_messages(messages):


config = load_config()

# Ollama client setup using the host from config
ollama_client = ollama.Client(host=config["ollama"]["host"])

# MySQL connection settings from config
mysql_config = config["mysql"]
chat_manager = ChatHistoryManager()

# Initialize chat sessions
if "chats" not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat_id = None

# Render the sidebar with MySQL config
with st.sidebar:
    render_sidebar(ollama_client, mysql_config)

st.title("Chat with Ollama LLM")

# Display chat history for selected chat
if st.session_state.current_chat_id:
    chat_name = chat_manager.chat_name(st.session_state.current_chat_id)
    last_role = None
    for role, content in chat_manager.chat_messages(st.session_state.current_chat_id):
        with st.chat_message(role):
            st.markdown(content)
    if prompt := st.chat_input("What do you need next?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Communicating with Ollama..."):
            response = chat_manager.do_ollama_query(st.session_state.selected_model, st.session_state.current_chat_id, prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
else:
    st.write("Create a new chat in the sidebar")
