# ui/styles.py

import streamlit as st

def cargar_estilos():

    st.markdown("""
    <style>

    .main {
        background-color: #F4F6F8;
    }

    h1 {
        color: #0A2342;
    }

    .stButton button{
        background-color:#005EB8;
        color:white;
        border-radius:6px;
        padding:0.25rem 0.5rem;
        min-height:32px;
        min-width:60px;
        font-size:12px;
    }

    </style>
    """,
    unsafe_allow_html=True)
