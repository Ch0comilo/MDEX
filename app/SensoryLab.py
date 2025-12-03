import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Catación de Café — EDA", layout="wide")

st.title(" EDA — Dataset de Catadores de Café")

# Inicializar df
if "df" not in st.session_state:
    st.session_state.df = None

# Subir archivo
file = st.file_uploader("Sube tu archivo CSV", type="csv")

if file:
    st.session_state.df = pd.read_csv(file)
    st.success("Archivo cargado correctamente")
    st.dataframe(st.session_state.df.head())

df = st.session_state.df
if df is None:
    st.stop()

# ======================================================
# VARIABLES DEL DATASET
# ======================================================

numeric_cols = ["Puntaje_SCA"]
cat_cols = ["Perfil_Catador", "Variedad_Codigo", "Variedad_Nombre"]

# ======================================================
# INFORMACIÓN GENERAL
# ======================================================
st.header(" Información General del Dataset")

col1, col2, col3 = st.columns(3)
col1.metric("Filas", df.shape[0])
col2.metric("Columnas", df.shape[1])
col3.metric("Valores nulos", df.isna().sum().sum())

st.write("### Vista previa del dataset")
st.dataframe(df.head())

# ======================================================
# ESTADÍSTICAS
# ======================================================
st.header(" Estadísticas Descriptivas")
st.dataframe(df[numeric_cols].describe().transpose())

# ======================================================
# NULOS
# ======================================================

st.header("Porcentaje de Valores Nulos por Tipo de Columna")

# Crear DataFrame con tipo de dato y porcentaje de nulos
nulos = pd.DataFrame({
    "Tipo": df.dtypes,
    "Porcentaje_Nulos": df.isna().mean() * 100
}).reset_index()

nulos.columns = ["Columna", "Tipo", "Porcentaje_Nulos"]

# Mostrar tabla
st.dataframe(nulos)


# ======================================================
# RELACIÓN ENTRE VARIABLES
# ======================================================
st.header(" Relación entre Perfil del Catador y Puntaje")

fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df, x="Perfil_Catador", y="Puntaje_SCA", ax=ax)
ax.set_title("Puntaje SCA según el Perfil del Catador")
st.pyplot(fig)

