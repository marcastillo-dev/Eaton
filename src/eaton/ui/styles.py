# ui/styles.py

import base64
from pathlib import Path

import streamlit as st


def mostrar_imagen_marco(assets_dir, marco):

    rutas = {
        "black": Path(assets_dir) / f"{marco}_black.png",
        "white": Path(assets_dir) / f"{marco}_white.png"
    }

    imagenes = {}

    for tema, ruta in rutas.items():
        if ruta.is_file():
            contenido = base64.b64encode(ruta.read_bytes()).decode("ascii")
            imagenes[tema] = f"data:image/png;base64,{contenido}"

    if not imagenes:
        return

    imagen_clara = imagenes.get("white", imagenes.get("black"))
    imagen_oscura = imagenes.get("black", imagen_clara)

    st.markdown(
        f"""
        <picture class="marco-tematico">
            <source media="(prefers-color-scheme: dark)" srcset="{imagen_oscura}">
            <img src="{imagen_clara}" alt="Marco {marco}">
        </picture>
        """,
        unsafe_allow_html=True
    )

def cargar_estilos():

    st.markdown("""
    <style>

    :root {
        --app-bg: #F4F6F8;
        --surface: #FFFFFF;
        --text-primary: #0A2342;
        --text-secondary: #40566F;
        --border: #D9E2EC;
        --control-bg: #FFFFFF;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --app-bg: #0D1117;
            --surface: #161B22;
            --text-primary: #F0F6FC;
            --text-secondary: #C9D1D9;
            --border: #30363D;
            --control-bg: #21262D;
        }
    }

    .stApp,
    .main,
    [data-testid="stAppViewContainer"] {
        background-color: var(--app-bg);
        color: var(--text-primary);
    }

    [data-testid="stHeader"] {
        background-color: var(--app-bg);
    }

    h1, h2, h3, h4, h5, h6,
    p, label, [data-testid="stCaptionContainer"],
    [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--text-secondary);
    }

    [data-testid="stTextInput"] input,
    [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] input {
        background-color: var(--control-bg);
        color: var(--text-primary);
        border-color: var(--border);
    }

    [data-testid="stImage"] img,
    .marco-tematico img {
        display: block;
        width: 100%;
        height: auto;
    }

    .marco-tematico {
        display: block;
        width: 100%;
    }

    h1 {
        color: var(--text-primary);
    }

    .stButton button{
        background-color:#005EB8;
        color:#FFFFFF;
        border-radius:6px;
        padding:0.25rem 0.5rem;
        min-height:32px;
        min-width:60px;
        font-size:12px;
    }

    [data-testid="stExpander"],
    [data-testid="stPopover"] {
        border-color: var(--border);
        color: var(--text-primary);
    }

    </style>
    """,
    unsafe_allow_html=True)
