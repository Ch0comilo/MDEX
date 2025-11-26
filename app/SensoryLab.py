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

numeric_cols = ["Catador_ID", "Puntaje_SCA"]
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
st.header(" Valores Nulos por Columna")

nulos = df.isna().sum().reset_index()
nulos.columns = ["Columna", "Nulos"]
st.bar_chart(nulos.set_index("Columna"))

# ======================================================
# DISTRIBUCIONES NUMÉRICAS
# ======================================================
st.header(" Distribución del Puntaje SCA")

fig, ax = plt.subplots()
sns.histplot(df["Puntaje_SCA"].dropna(), kde=True, ax=ax)
ax.set_title("Distribución del Puntaje SCA")
st.pyplot(fig)

# ======================================================
# CATEGÓRICAS
# ======================================================
st.header(" Análisis de Variables Categóricas")

for col in cat_cols:
    st.subheader(f"Frecuencia de {col}")

    fig, ax = plt.subplots(figsize=(8, 4))
    df[col].value_counts().plot(kind="bar", ax=ax)
    ax.set_title(f"Frecuencia de {col}")
    st.pyplot(fig)

# ======================================================
# RELACIÓN ENTRE VARIABLES
# ======================================================
st.header(" Relación entre Perfil del Catador y Puntaje")

fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df, x="Perfil_Catador", y="Puntaje_SCA", ax=ax)
ax.set_title("Puntaje SCA según el Perfil del Catador")
st.pyplot(fig)

st.header(" Transformaciones a valores numéricos")

# Creamos una copia solo para correlación
df_corr = df.copy()

# Variedad A-E → 1-5
variedad_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
df_corr["Variedad_Num"] = df_corr["Variedad_Codigo"].map(variedad_map)

# Perfil Generoso/Estricto → 1/2
perfil_map = {"Generoso": 1, "Estricto": 2}
df_corr["Perfil_Num"] = df_corr["Perfil_Catador"].map(perfil_map)

st.subheader(" Mapeos utilizados")
st.write("### Variedad_Codigo → Variedad_Num")
st.dataframe(pd.DataFrame(variedad_map.items(), columns=["Variedad_Codigo", "Código_Numérico"]))

st.write("### Perfil_Catador → Perfil_Num")
st.dataframe(pd.DataFrame(perfil_map.items(), columns=["Perfil_Catador", "Código_Numérico"]))

# Warnings por valores desconocidos
if df_corr["Variedad_Num"].isna().sum() > 0:
    st.warning(" Hay valores en Variedad_Codigo que no son A–E.")

if df_corr["Perfil_Num"].isna().sum() > 0:
    st.warning(" Hay valores en Perfil_Catador que no son Generoso/Estricto.")


# ======================================================
# MATRIZ DE CORRELACIÓN — SOLO CON df_corr
# ======================================================
st.header(" Matriz de Correlación ")

corr_cols = ["Catador_ID", "Puntaje_SCA", "Variedad_Num", "Perfil_Num"]

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(df_corr[corr_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
ax.set_title("Matriz de Correlación con Variables Transformadas ")
st.pyplot(fig)