import streamlit as st
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

st.title("Ajuste Intrabloque (BIBD)")

df = st.session_state.get("df")  # <-- Usar el df cargado previamente

if df is None:
    st.error("Primero debes cargar un DataFrame en la sección anterior.")
    st.stop()

st.subheader("Datos cargados")
st.write(df)

# ============================================================
#      CONFIGURACIÓN DE VARIABLES
# ============================================================

st.subheader("Selecciona las columnas del experimento")

col_bloque = st.selectbox("Columna de Bloques", df.columns)
col_trat = st.selectbox("Columna de Tratamientos", df.columns)
col_resp = st.selectbox("Columna de Respuesta", df.columns)

# ============================================================
#      AJUSTE INTRABLOQUE (Modelo de Bloques Completos)
# ============================================================

if st.button("Ajustar Modelo Intrabloque"):
    st.subheader("Modelo Lineal del Diseño en Bloques")

    # --------------------------------------------------------
    # MODELO: Y = μ + Tratamiento + Bloque + error
    # --------------------------------------------------------

    formula = f"{col_resp} ~ C({col_trat}) + C({col_bloque})"

    try:
        modelo = smf.ols(formula, data=df).fit()
        anova_table = sm.stats.anova_lm(modelo, typ=2)

        st.write("### Tabla ANOVA")
        st.write(anova_table)

        # ----------------------------------------------------
        #   EFECTOS AJUSTADOS
        # ----------------------------------------------------
        st.subheader("Estimaciones del Modelo")
        st.write(modelo.summary())

        # ----------------------------------------------------
        #   PROMEDIOS AJUSTADOS POR TRATAMIENTO
        # ----------------------------------------------------
        st.subheader("Medias Ajustadas por Tratamiento (LSMeans)")

        medios_ajustados = (
            df.assign(pred=modelo.fittedvalues)
            .groupby(col_trat)["pred"]
            .mean()
        )

        st.write(medios_ajustados)

    except Exception as e:
        st.error(f"Error al ajustar el modelo: {e}")
