import streamlit as st

from src.controllers.main_controller import main

try:
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")