import mysql.connector
import ollama
import streamlit as st
import yaml

class ChatHistoryManager:
    def __init__(self):
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            self.mysql_config = config["mysql"]
            self.ollama_client = ollama.Client(host=config["ollama"]["host"])

    def do_ollama_query(self, model, chat_id, user_prompt):
        # insert our query, if one got passed in
        if user_prompt:
            self.insert_message(chat_id, "user", user_prompt)

        history = self.chat_messages(chat_id)

        try:
            response = self.ollama_client.chat(
                model=model,
                messages=( [{"role": role, "content": content} for role, content in history])
            )

            assistant_response = response["message"]["content"]
            self.insert_message(chat_id, "assistant", assistant_response)
            return assistant_response
        except Exception as e:
            st.error(f"Error communicating with Ollama: {e}")

    def db_connect(self):
        return mysql.connector.connect(
            host=self.mysql_config["host"],
            user=self.mysql_config["user"],
            password=self.mysql_config["password"],
            database=self.mysql_config["database"]
        )

    def chat_name(self, chat_id):
        db_connection = self.db_connect()
        cursor = db_connection.cursor()

        cursor.execute("SELECT chat_name FROM chats WHERE id = %s", (chat_id,))
        name = cursor.fetchone()[0]
        cursor.close()
        db_connection.close()

        return name

    def chat_messages(self, chat_id):
        db_connection = self.db_connect()
        cursor = db_connection.cursor()

        cursor.execute("SELECT role, content FROM messages WHERE chat_id = %s", (chat_id,))
        messages = cursor.fetchall()
        cursor.close()
        db_connection.close()

        return messages

    def insert_message(self, chat_id, role, content):
        db_connection = self.db_connect()
        cursor = db_connection.cursor()
        sql = """
            INSERT INTO messages (chat_id, role, content)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (chat_id, role, content))
        db_connection.commit()

        cursor.close()
        db_connection.close()
