import streamlit as st
import pandas as pd


def main():
    st.title("Veredicto Final")

    resultados = st.session_state.get("resultados")
    if resultados is None:
        st.error(
            (
                "No se encontraron resultados. Ejecuta primero el ajuste en "
                "'Ajuste Intrabloque' o en 'Medias Ajustadas' para generar las medias."
            )
        )
        return

    if "Media Ajustada" not in resultados.columns:
        st.warning(
            (
                "Los resultados no contienen la columna 'Media Ajustada'. "
                "Asegúrate de ejecutar el ajuste antes de ver el veredicto."
            )
        )

    # Determinar ganador de forma segura
    try:
        series = resultados["Media Ajustada"].dropna()
        if series.empty:
            st.info("No hay medias ajustadas válidas para determinar un ganador.")
            return

        idx = series.idxmax()
        ganador = resultados.loc[idx]

        st.subheader("Veredicto Final")
        st.write(f"El café ganador es: {ganador['Café']}")
        try:
            st.write(f"Puntaje Ajustado: {ganador['Media Ajustada']:.2f}")
        except Exception:
            st.write("Puntaje Ajustado:", ganador.get("Media Ajustada"))

    except Exception as e:
        st.error(f"Error al determinar el ganador: {e}")
        return

    # Calcular eficiencia aproximada si están las medias simples
    if "Media Simple" in resultados.columns:
        try:
            suma_aj = resultados["Media Ajustada"].sum()
            suma_sim = resultados["Media Simple"].sum()
            if suma_sim == 0 or pd.isna(suma_sim):
                st.info(
                    "No se puede calcular eficiencia: suma de medias simples inválida."
                )
            else:
                eficiencia = (suma_aj / suma_sim) * 100
                st.write(f"Eficiencia del diseño (aprox.): {eficiencia:.2f}%")
        except Exception as e:
            st.info(f"No fue posible calcular eficiencia: {e}")


main()
