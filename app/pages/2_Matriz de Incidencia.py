import streamlit as st
import pandas as pd
import statsmodels.api as sm

st.title("Matriz de Incidencia")

file = st.session_state.get("df")

if file:
    df = pd.read_csv(file)
    st.write("Variables disponibles:", df.columns)

    y = st.selectbox("Variable objetivo (y)", df.columns)
    X = st.multiselect("Regresores (X)", df.columns)

    if st.button("Entrenar modelo"):
        X_df = sm.add_constant(df[X])
        model = sm.OLS(df[y], X_df).fit()
        st.write(model.summary())
