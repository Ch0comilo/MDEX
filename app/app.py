import streamlit as st
import pandas as pd

st.set_page_config(page_title="Proyecto", layout="wide")

st.title("Página Principal")

# Inicializar el espacio para df
if "df" not in st.session_state:
    st.session_state.df = None

file = st.file_uploader("Sube tu archivo CSV", type="csv")

if file:
    st.session_state.df = pd.read_csv(file)
    st.success("Archivo cargado correctamente")
    st.dataframe(st.session_state.df.head())

st.sidebar.info("Sube el archivo aquí y navega a las demás páginas.")

