import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Veredicto Final", layout="wide")
st.title("Veredicto Final")

# Recuperar el df cargado en la página principal
df = st.session_state.get("df")

# Si no hay df cargado, mostrar aviso
if df is None:
    st.warning("⚠️ No se ha subido ningún archivo aún. Por favor vuelve a la página principal y carga un CSV.")
    st.stop()

# Mostrar primeras filas
st.subheader("Vista previa de los datos")
st.dataframe(df.head())

# Mostrar información básica
st.subheader("Información general")
col1, col2 = st.columns(2)

with col1:
    st.write("**Dimensiones:**")
    st.write(f"- Filas: `{df.shape[0]}`")
    st.write(f"- Columnas: `{df.shape[1]}`")

with col2:
    st.write("**Tipos de variables:**")
    st.write(df.dtypes)

# Estadísticas descriptivas
st.subheader("Estadísticas descriptivas")
st.dataframe(df.describe())

# Selección de columna numérica
st.subheader("Visualización")
numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

if len(numeric_cols) == 0:
    st.error("No hay columnas numéricas para graficar.")
    st.stop()

col = st.selectbox("Selecciona una columna numérica para visualizar:", numeric_cols)

# Histograma
fig, ax = plt.subplots()
sns.histplot(df[col], kde=True, ax=ax)
ax.set_title(f"Histograma de {col}")
st.pyplot(fig)

# Gráfico de caja
fig2, ax2 = plt.subplots()
sns.boxplot(data=df, y=col, ax=ax2)
ax2.set_title(f"Diagrama de Caja de {col}")
st.pyplot(fig2)

# Correlaciones
st.subheader("Mapa de correlaciones")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax3)
st.pyplot(fig3)

st.success("¡Análisis generado con éxito!")
