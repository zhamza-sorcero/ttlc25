import os
import streamlit as st

from src.controllers.main_controller import main

try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.warning("OpenAI API key not found in secrets. Chat functionality will be disabled.")
    os.environ["OPENAI_API_KEY"] = ""

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
