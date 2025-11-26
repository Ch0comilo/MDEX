import pandas as pd
import numpy as np

# Cargar los datos del CSV
df = pd.read_csv('datos_cata_cafe_bibd.csv')

# Variables
t = 5  # Número de cafés
k = 3  # Tamaño del bloque
b = 10  # Número de catadores
lambda_val = 3  # Lambda, veces que un par de cafés se encuentra junto

# Calcular las medias simples
simple_means = df.mean()

# Ajuste de medias: Calculando Q_i (Total Ajustado de cada café)
# Q_i = Y_{i.} - (1/k) * sum(B_j) donde B_j es el bloque que incluye al café i
Q_i = []
for i in range(t):
    total_cafe_i = df.iloc[:, i].sum()  # Suma total del puntaje para cada café
    promedio_bloques = df.mean(axis=1).mean()  # Promedio de los bloques
    Q_i.append(total_cafe_i - (1/k) * promedio_bloques)

# Calcular medias ajustadas usando la fórmula LSMeans
adjusted_means = [(k * Q) / (lambda_val * t) for Q in Q_i]

# Crear dataframe de resultados
resultados = pd.DataFrame({
    'Café': ['A', 'B', 'C', 'D', 'E'],
    'Media Simple': simple_means,
    'Media Ajustada': adjusted_means
})

# Mostrar resultados
import streamlit as st
st.title("Análisis de Cafés - Medias Ajustadas")
st.write("A continuación se presentan las medias simples y ajustadas de cada café:")

st.dataframe(resultados)

