import streamlit as st
import mysql.connector
import datetime
from model_selector import model_selector
from system_prompts import system_prompt_selector

# Function to render the sidebar
def render_sidebar(ollama_client, mysql_config):
    with st.expander("Chat Options", expanded=True):
        st.session_state.selectedModel = model_selector(client=ollama_client)

        ## ! System prompt stuff isn't quite ready
        #st.session_state.selected_system_prompt = system_prompt_selector()

        if st.session_state.current_chat_id:
            chat_name = st.session_state.current_chat_name
            if st.button(f"Delete {chat_name}"):
                delete_dialog(mysql_config)

        if st.session_state.current_chat_id:
            chat_name = st.session_state.current_chat_name
            if st.button(f"Rename {chat_name}"):
                rename_dialog(mysql_config)

        # Create new chat button
        if st.sidebar.button("Create New Chat"):
            create_chat_dialog(mysql_config)

    # Fetch chat names from MySQL
    chat_names = get_chat_names_from_db(mysql_config)

    st.subheader("Existing chats", divider=True)

    # If there are existing chats, show them with buttons
    if chat_names:
        for chat_name in chat_names:
            if st.sidebar.button(chat_name, type="tertiary"):
                st.session_state.current_chat_name = chat_name
                st.session_state.current_chat_id = get_chat_id_for_name(chat_name, mysql_config)
                messages = None
                st.rerun()

@st.dialog("Delete chat")
def delete_dialog(mysql_config):
    st.write(f"Are you sure you want to delete the chat named {st.session_state.current_chat_name}")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            # do something
            remove_chat_in_db(st.session_state.current_chat_id, mysql_config)
            st.session_state.current_chat_name = None
            st.session_state.current_chat_id = None
            st.rerun()
    with col2:
        if st.button("No"):
            st.rerun()
@st.dialog("Rename chat")
def rename_dialog(mysql_config):
    name = st.text_input(label="Chat Name", placeholder=st.session_state.current_chat_name)
    if name:
        rename_chat_in_db(st.session_state.current_chat_id, name, mysql_config)
        st.session_state.current_chat_name = name
        st.rerun()

@st.dialog("Create chat")
def create_chat_dialog(mysql_config):
    name = st.text_input(label="Chat Name", placeholder="Create new chat")
    if name:
        new_chat_id = create_new_chat(name, mysql_config)
        st.session_state.current_chat_name = name
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chats[name] = {"id": new_chat_id, "messages": []}
        st.rerun()

# Function to get all chat names from MySQL
def get_chat_names_from_db(mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = db_connection.cursor()

    # SQL query to fetch all chat names
    cursor.execute("SELECT chat_name FROM chats")
    chat_names = [row[0] for row in cursor.fetchall()]

    cursor.close()
    db_connection.close()

    return chat_names

# Function to get the chat ID for a given chat name
def get_chat_id_for_name(chat_name, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = db_connection.cursor()

    # SQL query to fetch chat ID for a given chat name
    cursor.execute("SELECT id FROM chats WHERE chat_name = %s", (chat_name,))
    chat_id = cursor.fetchone()[0]

    cursor.close()
    db_connection.close()

    return chat_id

# Function to save a message to MySQL
def save_message(chat_id, role, content, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = db_connection.cursor()

    # SQL query to insert message into the database
    sql = """
        INSERT INTO messages (chat_id, role, content)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (chat_id, role, content))
    db_connection.commit()

    cursor.close()
    db_connection.close()

# Function to get messages for a specific chat
def get_messages_for_chat(chat_id, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = db_connection.cursor()

    # SQL query to retrieve messages for a chat
    cursor.execute("SELECT role, content FROM messages WHERE chat_id = %s", (chat_id,))
    messages = cursor.fetchall()

    cursor.close()
    db_connection.close()

    return messages

# Function to create a new chat and store it in MySQL
def create_new_chat(chat_name, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = db_connection.cursor()

    # Get the current timestamp
    now = datetime.datetime.now()
    region = now.strftime("%Z")

    # Generate a unique chat name based on the timestamp and region
    # if 'CDT' in region:
    #     chat_name = f"Chat - {now.strftime('%Y-%m-%d %I:%M %p')} CDT"
    # else:
    #     chat_name = f"Chat - {now.strftime('%Y-%m-%d %I:%M %p')} {region}"

    # SQL query to insert a new chat
    sql = "INSERT INTO chats (chat_name) VALUES (%s)"
    cursor.execute(sql, (chat_name,))

    db_connection.commit()

    # Get the newly created chat ID
    new_chat_id = cursor.lastrowid

    cursor.close()
    db_connection.close()

    st.session_state.current_chat_id = new_chat_id
    st.session_state.current_chat_name = chat_name

    return new_chat_id

def rename_chat_in_db(chat_id, new_name, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    st.write(f"UPDATE chats SET chat_name = {new_name} WHERE id = {chat_id}")
    cursor = db_connection.cursor()
    sql = "UPDATE chats SET chat_name = %s WHERE id = %s"
    cursor.execute(sql, (new_name, chat_id,))
    db_connection.commit()

    cursor.close()
    db_connection.close()

def remove_chat_in_db(chat_id, mysql_config):
    db_connection = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )

    cursor = db_connection.cursor()
    delete_messages = "DELETE FROM messages WHERE chat_id = %s"
    delete_chat = "DELETE from chats WHERE id = %s"
    cursor.execute(delete_messages, (chat_id,))
    cursor.execute(delete_chat, (chat_id,))
    db_connection.commit()
    cursor.close()
    db_connection.close()