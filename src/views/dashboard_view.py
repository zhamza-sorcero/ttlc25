import streamlit as st
import pandas as pd


def apply_custom_css(css_path='src/styles/custom_css.css'):
    """Apply custom CSS styling"""
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def display_title():
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2.5rem; font-weight: 800; color: #1e293b; 
                      letter-spacing: -0.025em;'>
                TTLC Conference 2025
            </h1>
            <h2 style='color: #64748b; font-size: 1.1rem;'>
                Social Sentiment
            </h2>
        </div>
    """, unsafe_allow_html=True)


    # Add data preview
    st.markdown("""
        <h4 style='color: #1e293b; margin: 20px 0 10px 0;'>Data Preview (Top 10 Rows):</h4>
    """, unsafe_allow_html=True)

    # Read and display the CSV data
    df = pd.read_csv('ttlc25.csv')
    st.dataframe(
        df.head(10),
        hide_index=True,
        use_container_width=True
    )


def create_tabs():
    tab1, tab2, tab3 = st.tabs(["📈 Engagement", "📊 Analysis", "💬 Chat"])
    return tab1, tab2, tab3  # Return all three tabs explicitly
