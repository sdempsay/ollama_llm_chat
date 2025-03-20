import streamlit as st
import ollama
import yaml
from model_selector import model_selector
from sidebar import render_sidebar, get_messages_for_chat, save_message

# Load configuration from config.yaml
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

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

config = load_config()

# Ollama client setup using the host from config
ollama_client = ollama.Client(host=config["ollama"]["host"])

# MySQL connection settings from config
mysql_config = config["mysql"]

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
    chat_name = st.session_state.current_chat_name
    st.subheader(f"Chat: {chat_name}")

    # Fetch and display the messages for the selected chat from the database
    messages = get_messages_for_chat(st.session_state.current_chat_id, mysql_config)
    last_role = None
    for role, content in messages:
        last_role = role
        with st.chat_message(role):
            st.markdown(content)

    if chat_name not in st.session_state.chats or not chat_name:
        st.session_state.chats[chat_name] = ( [{"role": role, "content": content} for role, content in messages])
        ## ! System prompt stuff isn't quite ready
        #if st.session_state.selected_system_prompt:
            # st.session_state.chats[chat_name].insert(
            #     0,
            #     {"role": "system", "content": st.session_state.system_prompt[st.session_state.selected_system_prompt]})

    # Look for last message here
    if last_role and "user" == last_role:
        do_ollama_query(st.session_state.chats[chat_name])

    # Chat input and response handling
    if prompt := st.chat_input("What would you like to say?"):
        chat_name = st.session_state.current_chat_name

        # Ensure chat history is loaded from database (if not already)
        if chat_name not in st.session_state.chats or not chat_name:
            messages = get_messages_for_chat(st.session_state.current_chat_id, mysql_config)
            st.session_state.chats[chat_name] = ( [{"role": role, "content": content} for role, content in messages])
            ## ! System prompt stuff isn't quite ready

        st.session_state.chats[chat_name].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user message to the database
        save_message(st.session_state.current_chat_id, "user", prompt, mysql_config)
        do_ollama_query(st.session_state.chats[chat_name])
else:
    st.write("Create a new chat in the sidebar")
