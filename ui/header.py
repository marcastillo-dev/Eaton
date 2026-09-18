# ui/header.py

import streamlit as st

def render_header():

    st.image(
        "assets/eaton_logo.png",
        width=220
    )

    st.markdown("""
    <h1 style="
        color:white;
        margin-top:-15px;
        margin-bottom:0px;
    ">
        Órdenes EDS
    </h1>
    """,
    unsafe_allow_html=True)

    st.divider()