import streamlit as st

st.session_state['system_prompt'] = {}
st.session_state.system_prompt["Basic"] = """
You are acting as a helpful research assistant who will talk in an easy going tone and will often
give explanations to how you came up with your response.
"""

st.session_state.system_prompt["Architect"] = """
You are acting as a software architect answering questions for the Principal software architect.  
You provide details when needed but generally give concise answers.  
You are an expert in Java, OSGi, and Intermediate at Python tasks. You also give very creative answers.
"""

# st.session_state.selected_system_prompt = "Basic"

def system_prompt_selector():
    available_prompts = [ "Basic", "Architect" ]
    if "selected_system_prompt" not in st.session_state:
        st.session_state.selected_system_prompt = None

    st.session_state.selected_system_prompt = st.selectbox(
        "System Prompt",
        available_prompts,
        index=available_prompts.index(st.session_state.selected_system_prompt) if st.session_state.selected_system_prompt in available_prompts else 0
    )
    return st.session_state.selected_system_prompt