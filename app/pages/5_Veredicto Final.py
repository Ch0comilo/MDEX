# Calcular el café con el puntaje más alto ajustado
cafe_ganador = resultados.loc[resultados['Media Ajustada'].idxmax()]

# Mostrar el café ganador
st.subheader("Veredicto Final")
st.write(f"El café ganador es: {cafe_ganador['Café']}")
st.write(f"Puntaje Ajustado: {cafe_ganador['Media Ajustada']:.2f}")

# Determinar la eficiencia del diseño BIBD
# La eficiencia se calcula como la proporción de la varianza de un diseño BIBD comparado con un diseño completo hipotético
eficiencia = (sum(resultados['Media Ajustada']) / sum(resultados['Media Simple'])) * 100
st.write(f"Eficiencia del diseño BIBD: {eficiencia:.2f}%")
