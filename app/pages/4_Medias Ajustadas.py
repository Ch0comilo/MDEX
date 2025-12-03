import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import plotly.express as px

# Cargar o recuperar DataFrame
df = st.session_state.get('df')
if df is None:
    try:
        df = pd.read_csv('datos_cata_cafe_bibd.csv')
        st.info('Cargando `datos_cata_cafe_bibd.csv` del proyecto')
    except Exception:
        st.error('No hay DataFrame cargado. Sube un CSV en la página principal.')
        st.stop()

st.title('Medias Ajustadas')

# Medias simples por variedad
medias_simples = df.groupby('Variedad_Codigo')['Puntaje_SCA'].mean().sort_index()

# Ajuste: modelo con tratamiento (Variedad) y bloque (Catador)
resultados = st.session_state.get('resultados')
if resultados is None:
    try:
        modelo = smf.ols('Puntaje_SCA ~ C(Variedad_Codigo) + C(Catador_ID)', data=df).fit()

        # Para cada variedad, predecimos para cada catador y promediamos
        variedades = sorted(df['Variedad_Codigo'].unique())
        catadores = sorted(df['Catador_ID'].unique())

        medias_ajustadas = []
        for v in variedades:
            # construir DataFrame de predicción: la variedad v, para todos los catadores
            pred_df = pd.DataFrame({
                'Variedad_Codigo': [v] * len(catadores),
                'Catador_ID': catadores,
            })
            preds = modelo.predict(pred_df)
            medias_ajustadas.append(np.mean(preds))

        resultados = pd.DataFrame({
            'Café': variedades,
            'Media Simple': [medias_simples.get(v, np.nan) for v in variedades],
            'Media Ajustada': medias_ajustadas,
        })

        # Guardar para otras páginas
        st.session_state['resultados'] = resultados

    except Exception as e:
        st.error(f'Error al ajustar modelo: {e}')
        # En caso de fallo, construir al menos el dataframe de medias simples
        resultados = pd.DataFrame({
            'Café': medias_simples.index.tolist(),
            'Media Simple': medias_simples.values,
        })

st.subheader('Resultados')
st.dataframe(resultados)

# -------------------------------
# Gráfica interactiva: Media Simple vs Media Ajustada (Plotly)
# -------------------------------
try:
    plot_df = resultados[['Café', 'Media Simple', 'Media Ajustada']].copy()
    # convertir a formato largo para Plotly
    long_df = plot_df.melt(id_vars='Café',
                           value_vars=['Media Simple', 'Media Ajustada'],
                           var_name='Tipo', value_name='Puntaje')

    # preparar customdata por variedad (simple, ajustada, diferencia, pct)
    simple_map = plot_df.set_index('Café')['Media Simple'].to_dict()
    ajust_map = plot_df.set_index('Café')['Media Ajustada'].to_dict()
    custom_list = []
    for _, row in long_df.iterrows():
        cafe = row['Café']
        s = simple_map.get(cafe, np.nan)
        a = ajust_map.get(cafe, np.nan)
        diff = a - s if (not np.isnan(a) and not np.isnan(s)) else np.nan
        pct = (diff / s * 100) if (not np.isnan(diff) and s != 0) else np.nan
        custom_list.append([s, a, diff, pct])
    long_df['custom_s'] = [c[0] for c in custom_list]
    long_df['custom_a'] = [c[1] for c in custom_list]
    long_df['custom_diff'] = [c[2] for c in custom_list]
    long_df['custom_pct'] = [c[3] for c in custom_list]

    fig = px.bar(
        long_df,
        x='Café',
        y='Puntaje',
        color='Tipo',
        barmode='group',
        labels={'Puntaje': 'Puntaje', 'Café': 'Variedad'},
        title='Comparación: Media Simple vs Media Ajustada',
        height=420,
        hover_data={'custom_s': False, 'custom_a': False, 'custom_diff': False, 'custom_pct': False},
    )

    # Mostrar valores en el hover incluyendo ambas medias y diferencia
    hovertpl = (
        '%{x}<br>'
        'Tipo: %{legendgroup}<br>'
        'Valor (barra): %{y:.2f}<br>'
        'Media Simple: %{customdata[0]:.2f}<br>'
        'Media Ajustada: %{customdata[1]:.2f}<br>'
        'Diferencia: %{customdata[2]:.2f} (%{customdata[3]:.1f}%)<extra></extra>'
    )

    # attach customdata
    fig.update_traces(customdata=long_df[['custom_s', 'custom_a', 'custom_diff', 'custom_pct']].values)
    fig.update_traces(hovertemplate=hovertpl)

    st.subheader('Comparativa de Medias')
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info(f'No se pudo generar la gráfica interactiva: {e}')

# -------------------------------
# Mostrar qué catadores puntuaron cada variedad
# -------------------------------
st.subheader('Catadores por Variedad')
try:
    # agrupar catadores y mostrar puntajes individuales
    grouped = df.groupby('Variedad_Codigo')
    for variedad, group in grouped:
        with st.expander(f"Variedad {variedad} — {len(group)} puntuaciones"):
            # mostrar catadores únicos con su perfil (Generoso/Estricto)
            if 'Perfil_Catador' in group.columns:
                cat_perf = (
                    group[['Catador_ID', 'Perfil_Catador']]
                    .drop_duplicates()
                    .sort_values('Catador_ID')
                    .reset_index(drop=True)
                )
                st.write('Catadores únicos y perfil:')
                st.dataframe(cat_perf)
            else:
                catadores = sorted(group['Catador_ID'].unique())
                st.write('Catadores únicos:', catadores)

            # mostrar tabla con Catador_ID, Perfil_Catador y Puntaje_SCA
            cols = ['Catador_ID', 'Puntaje_SCA']
            if 'Perfil_Catador' in group.columns:
                cols.insert(1, 'Perfil_Catador')
            st.dataframe(group[cols].reset_index(drop=True))
except Exception as e:
    st.info(f'No se pudo listar los catadores por variedad: {e}')

