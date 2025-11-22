import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Modelo BIBD")

file = st.session_state.get("df")

if file:
    df = pd.read_csv(file)
    st.write(df.describe())

    col = st.selectbox("Selecciona una variable numérica", df.select_dtypes("number").columns)

    fig, ax = plt.subplots()
    sns.boxplot(x=df[col], ax=ax)
    st.pyplot(fig)
