# llm_chat
A chat agent that can talk to an ollama backend leveraging a MySQL database for storage of chat sessions

## Python modules
You will need a few pip modules to get this application running.  You can use a virtual environment if you choose, but the following modules are required:
* streamlit
* ollama
* mysql-connector-python

## Setup
Setup requires that you have an Ollama server with at least one model loaded and a MariaDB/MySQL database set up and accessible.

The database schema and a config.yaml file follow
### Database Schemas

~~~sql
CREATE TABLE chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    role VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);
~~~

### config.yaml
Here is an example of a config.yaml file:
~~~yaml
ollama:
  host: "http://127.0.0.1:11434"

mysql:
  host: "127.0.0.1"
  user: "llmUser"
  password: "llmUser"
  database: "llmChat"
~~~

## Starting streamlit
To start the application locally with StreamLit, run the following command:
~~~
streamlit run llm_chat/chat_app.py
~~~