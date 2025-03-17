# model_selector.py
import streamlit as st
import ollama

ollama_client = ollama.Client(host="http://10.6.66.221:11434")

@st.cache_data(ttl=3600)  # Cache expires after 3600 seconds (1 hour)
def get_available_models(_client=None):
    """Fetch available models from Ollama."""
    client = _client if _client else ollama_client
    try:
        models_response = client.list()

        # Check if 'models' key exists and is a list
        if "models" not in models_response or not isinstance(models_response["models"], list):
            st.error("No models found or invalid response from Ollama.")
            return ["llama3"]

        # Extract model names from the 'model' attribute
        models = []
        for model_entry in models_response["models"]:
            if hasattr(model_entry, "model"):
                models.append(model_entry.model)

        return models if models else ["llama3"]
    except Exception as e:
        st.error(f"Failed to fetch models from Ollama: {e}")
        return ["llama3"]  # Fallback to a default model

def model_selector(client=None):
    """Render a model selection dropdown and return the selected model."""
    available_models = get_available_models(client)
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama3"
    st.session_state.selected_model = st.selectbox(
        "Select Model",
        available_models,
        index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
    )
    return st.session_state.selected_model