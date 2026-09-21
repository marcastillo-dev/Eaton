# ui/header.py

import streamlit as st
from src.eaton.config.settings import LOGO

def render_header():

    st.image(
        str(LOGO),
        width=220
    )

    st.markdown("""
    <h1 style="
        color:var(--text-primary);
        margin-top:-15px;
        margin-bottom:0px;
    ">
        Órdenes EDS
    </h1>
    """,
    unsafe_allow_html=True)

    st.divider()