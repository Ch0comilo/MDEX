import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.title(" Matriz de Incidencia ")

# Obtener dataframe
df_original = st.session_state.get("df")

if df_original is None:
    st.error("No se ha cargado ningún archivo desde la página principal.")
    st.stop()

df = df_original.copy()

# Selección de columna que representa la variedad
variedad = st.selectbox(
    "Selecciona la columna que representa la variedad del café:",
    ["Variedad_Codigo", "Variedad_Nombre"]
)

# Filas = Catadores
catadores = df["Catador_ID"].unique()

# Columnas = Variedades
variedades = df[variedad].unique()

# -----------------------------------------------
# MATRIZ Catador × Café CON PUNTAJES REALES
# -----------------------------------------------
matriz = pd.DataFrame(index=[f"#{i}" for i in catadores], columns=variedades)

for _, row in df.iterrows():
    cat = f"#{row['Catador_ID']}"
    cafe = row[variedad]
    score = row["Puntaje_SCA"]
    matriz.loc[cat, cafe] = score

# Mostrar matriz EXACTA como la imagen
st.write("###  Matriz de Puntajes Reales (catadores vs variedades)")
st.dataframe(matriz)

# -----------------------------------------------
# HEATMAP con puntajes dentro de cada celda
# -----------------------------------------------

st.write("###  Heatmap de Puntajes ")

# Convertir a float, reemplazar None por NaN
heatmap_data = matriz.astype(float)

plt.figure(figsize=(12, 6))
sns.heatmap(
    heatmap_data,
    annot=True,        # muestra los puntajes dentro del cuadro
    fmt=".2f",         # formato de decimales
    cmap="viridis",    # mapa de colores
    linewidths=0.5,
    linecolor="black"
)
st.pyplot(plt)
