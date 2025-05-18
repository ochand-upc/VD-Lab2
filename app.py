import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import json

# Configurar el título y descripción de la aplicación
st.set_page_config(
    page_title="Himalayan Expeditions Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("🏔️ Himalayan Expeditions Interactive Dashboard")
st.markdown("""
This dashboard provides insights into Himalayan expedition data, allowing you to explore patterns across routes, 
peaks, success rates, countries, and expedition characteristics. Use the controls in the sidebar to filter the data
and interact with the visualizations to discover interesting patterns.
""")

# Desactivar el límite de filas para Altair
alt.data_transformers.disable_max_rows()

# Función para cargar datos
@st.cache_data
def load_data():
    # Rutas para los archivos de datos
    data_dir = "input_data"
    
    # Cargar datos principal
    exped_path = os.path.join(data_dir, "exped_tidy.csv")
    peaks_path = os.path.join(data_dir, "peaks_tidy.csv")
    coords_path = os.path.join(data_dir, "unique_peaks_coords.csv")
    
    exped_df = pd.read_csv(exped_path)
    peaks_df = pd.read_csv(peaks_path)
    coords_df = pd.read_csv(coords_path)
    
    return exped_df, peaks_df, coords_df

# Cargar los datos
with st.spinner("Loading data..."):
    exped_df, peaks_df, coords_df = load_data()

# Función para limpiar y procesar los datos
@st.cache_data
def process_data(exped_df, peaks_df, coords_df):
    # Limpieza del dataset de expediciones
    df_clean = exped_df.copy()
    
    # Unificar valores nulos para rutas
    route_columns = ['ROUTE1', 'ROUTE2', 'ROUTE3', 'ROUTE4']
    for col in route_columns:
        df_clean[col] = df_clean[col].replace('NA', np.nan).replace('', np.nan)
    
    # Convertir columnas de éxito en booleanas explícitas
    success_columns = ['SUCCESS1', 'SUCCESS2', 'SUCCESS3', 'SUCCESS4']
    for col in success_columns:
        df_clean[col] = df_clean[col].fillna(False).astype(bool)
    
    # Asegurarse de que TOTDAYS sea numérico
    df_clean['TOTDAYS'] = pd.to_numeric(df_clean['TOTDAYS'], errors='coerce')
    
    # Crear año como entero para facilitar filtrado
    df_clean['YEAR_INT'] = pd.to_numeric(df_clean['YEAR'], errors='coerce')
    
    # Verificar que al menos tengamos PEAKID y YEAR en todos los registros
    df_clean = df_clean.dropna(subset=['PEAKID', 'YEAR_INT'])
    
    # Crear un indicador de éxito general para la expedición
    df_clean['ANY_SUCCESS'] = df_clean[success_columns].any(axis=1)
    
    # Merge con datos de picos y coordenadas
    df_merged = pd.merge(df_clean, peaks_df[['PEAKID', 'PKNAME', 'HEIGHTM', 'HIMAL_FACTOR', 'REGION_FACTOR']], 
                         on='PEAKID', how='left')
    df_merged = pd.merge(df_merged, coords_df, on='PEAKID', how='left')
    
    # Crear una versión filtrada con solo los picos más populares
    peak_counts = df_merged['PEAKID'].value_counts()
    top_peaks = peak_counts[peak_counts >= 30].index.tolist()
    df_top_peaks = df_merged[df_merged['PEAKID'].isin(top_peaks)]
    
    # Crear bins para décadas
    df_merged['decade'] = (df_merged['YEAR_INT'] // 10) * 10
    df_merged['decade'] = df_merged['decade'].astype(str) + 's'
    
    # Crear períodos de tiempo (cada 5 años)
    df_merged['period'] = (df_merged['YEAR_INT'] // 5) * 5
    df_merged['period'] = df_merged['period'].astype(str) + '-' + (df_merged['period'] + 4).astype(str)
    
    return df_merged, top_peaks

# Procesar los datos
with st.spinner("Processing data..."):
    df_merged, top_peaks = process_data(exped_df, peaks_df, coords_df)

# Preparar datos para visualizaciones específicas
@st.cache_data
def prepare_route_success_data(df_merged):
    # Expandir datos para pares ruta-éxito
    route_success_pairs = []
    
    for _, row in df_merged.iterrows():
        for i in range(1, 5):  # Para ROUTE1-4 y SUCCESS1-4
            route_col = f'ROUTE{i}'
            success_col = f'SUCCESS{i}'
            
            if pd.notna(row[route_col]):
                route_success_pairs.append({
                    'EXPID': row['EXPID'],
                    'PEAKID': row['PEAKID'],
                    'PKNAME': row['PKNAME'],
                    'YEAR': row['YEAR'],
                    'SEASON_FACTOR': row['SEASON_FACTOR'],
                    'ROUTE': row[route_col],
                    'SUCCESS': row[success_col],
                    'HEIGHTM': row['HEIGHTM']
                })
    
    routes_df = pd.DataFrame(route_success_pairs)
    
    # Calcular tasas de éxito por ruta y pico
    route_success_rates = routes_df.groupby(['PEAKID', 'PKNAME', 'ROUTE']).agg(
        total_attempts=('SUCCESS', 'count'),
        successful_attempts=('SUCCESS', 'sum'),
        height=('HEIGHTM', 'first')
    ).reset_index()
    
    route_success_rates['success_rate'] = route_success_rates['successful_attempts'] / route_success_rates['total_attempts']
    
    # Filtrar rutas con al menos 5 intentos
    route_success_rates = route_success_rates[route_success_rates['total_attempts'] >= 5]
    
    return route_success_rates

@st.cache_data
def prepare_country_data(df_merged):
    # Contar expediciones por país y década
    country_expeditions = df_merged.groupby(['HOST_FACTOR', 'decade']).size().reset_index(name='count')
    
    # Identificar los países más activos
    top_countries = df_merged['HOST_FACTOR'].value_counts().head(10).index.tolist()
    
    # Filtrar para los países más activos
    country_expeditions_top = country_expeditions[country_expeditions['HOST_FACTOR'].isin(top_countries)]
    
    # Expediciones por país para cada pico
    country_exped_by_peak = df_merged.groupby(['PEAKID', 'PKNAME', 'HOST_FACTOR']).size().reset_index(name='count')
    country_exped_by_peak = country_exped_by_peak.sort_values('count', ascending=False)
    
    return country_expeditions_top, country_exped_by_peak

@st.cache_data
def prepare_duration_data(df_merged):
    # Filtrar registros con información de duración válida
    duration_df = df_merged.dropna(subset=['TOTDAYS', 'ANY_SUCCESS'])
    duration_df = duration_df[duration_df['TOTDAYS'] > 0]
    
    # Crear bins para duración
    duration_bins = [0, 15, 30, 45, 60, 75, 90, 365]
    duration_labels = ['1-15', '16-30', '31-45', '46-60', '61-75', '76-90', '90+'] 
    duration_df['duration_bin'] = pd.cut(duration_df['TOTDAYS'], bins=duration_bins, labels=duration_labels, right=False)
    
    # Calcular tasas de éxito por pico, temporada y bin de duración
    duration_success = duration_df.groupby(['PEAKID', 'PKNAME', 'SEASON_FACTOR', 'duration_bin']).agg(
        total=('EXPID', 'count'),
        success=('ANY_SUCCESS', 'sum')
    ).reset_index()
    
    duration_success['success_rate'] = duration_success['success'] / duration_success['total']
    
    # Filtrar para tener al menos 3 expediciones en cada bin
    duration_success = duration_success[duration_success['total'] >= 3]
    
    # Preparar datos para la visualización general
    duration_avg = duration_df.groupby(['PEAKID', 'PKNAME', 'ANY_SUCCESS']).agg(
        avg_duration=('TOTDAYS', 'mean'),
        count=('EXPID', 'count')
    ).reset_index()
    
    return duration_success, duration_avg, duration_df

@st.cache_data
def prepare_termination_data(df_merged):
    # Filtrar registros con razones de terminación conocidas
    termination_df = df_merged.dropna(subset=['TERMREASON_FACTOR'])
    
    # Agrupar las razones menos comunes como "Other"
    reason_counts = termination_df['TERMREASON_FACTOR'].value_counts()
    common_reasons = reason_counts[reason_counts >= 100].index.tolist()
    termination_df['reason_grouped'] = termination_df['TERMREASON_FACTOR'].apply(
        lambda x: x if x in common_reasons else 'Other reasons')
    
    # Calcular distribución de razones por pico y período
    term_evolution = termination_df.groupby(['PEAKID', 'PKNAME', 'period', 'reason_grouped']).size().reset_index(name='count')
    
    # Calcular porcentajes dentro de cada pico y período
    term_evolution = term_evolution.merge(
        term_evolution.groupby(['PEAKID', 'period'])['count'].sum().reset_index(name='total'),
        on=['PEAKID', 'period']
    )
    term_evolution['percentage'] = term_evolution['count'] / term_evolution['total'] * 100
    
    return term_evolution, termination_df

# Preparar datos para las visualizaciones
with st.spinner("Preparing visualization data..."):
    route_success_rates = prepare_route_success_data(df_merged)
    country_expeditions_top, country_exped_by_peak = prepare_country_data(df_merged)
    duration_success, duration_avg, duration_df = prepare_duration_data(df_merged)
    term_evolution, termination_df = prepare_termination_data(df_merged)

# Sidebar para filtros y controles
st.sidebar.header("Filters and Controls")

# Selector de pico
selected_peak = st.sidebar.selectbox(
    "Select Mountain Peak", 
    options=top_peaks,
    format_func=lambda x: f"{x} - {df_merged[df_merged['PEAKID'] == x]['PKNAME'].iloc[0]}"
)

# Selector de rango de años
min_year = int(df_merged['YEAR_INT'].min())
max_year = int(df_merged['YEAR_INT'].max())
year_range = st.sidebar.slider(
    "Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Selector de temporada para algunas visualizaciones
all_seasons = sorted(df_merged['SEASON_FACTOR'].dropna().unique().tolist())
selected_season = st.sidebar.selectbox(
    "Season (for duration analysis)",
    options=['All'] + all_seasons
)

# Aplicar filtros al dataset principal
filtered_df = df_merged[
    (df_merged['YEAR_INT'] >= year_range[0]) & 
    (df_merged['YEAR_INT'] <= year_range[1])
]

if selected_season != 'All':
    season_filter_df = filtered_df[filtered_df['SEASON_FACTOR'] == selected_season]
else:
    season_filter_df = filtered_df

# Información básica sobre el pico seleccionado
peak_info = df_merged[df_merged['PEAKID'] == selected_peak].iloc[0]

# Panel de información sobre el pico seleccionado
st.sidebar.markdown("---")
st.sidebar.header("Selected Peak Information")
st.sidebar.markdown(f"""
**Peak**: {peak_info['PKNAME']}  
**Height**: {peak_info['HEIGHTM']}m  
**Region**: {peak_info['REGION_FACTOR']}  
**Mountain Range**: {peak_info['HIMAL_FACTOR']}  
**Coordinates**: {peak_info['LATITUDE']:.4f}, {peak_info['LONGITUDE']:.4f}
""")

# Panel de estadísticas generales
st.sidebar.markdown("---")
st.sidebar.header("Overall Statistics")
total_expeditions = filtered_df[filtered_df['PEAKID'] == selected_peak].shape[0]
success_rate = filtered_df[(filtered_df['PEAKID'] == selected_peak) & (filtered_df['ANY_SUCCESS'])].shape[0] / total_expeditions if total_expeditions > 0 else 0
avg_duration = filtered_df[filtered_df['PEAKID'] == selected_peak]['TOTDAYS'].mean()

st.sidebar.markdown(f"""
**Total Expeditions**: {total_expeditions}  
**Overall Success Rate**: {success_rate:.1%}  
**Average Duration**: {avg_duration:.1f} days
""")

# Estructura del dashboard principal
st.markdown("## Himalayan Expeditions Analysis Dashboard")

# Dividir el dashboard en pestañas para cada pregunta principal
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🛤️ Routes & Success", 
    "🌏 Countries", 
    "⏱️ Duration & Success", 
    "❌ Termination Reasons"
])

# Tab 1: Overview --------------------------------------------------------
with tab1:
    st.markdown("### Overview of Himalayan Expeditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mapa de picos con datos de expediciones
        st.markdown("#### Geographic Distribution of Peaks")
        
        # Preparar datos para el mapa
        peak_counts = filtered_df.groupby('PEAKID').size().reset_index(name='expeditions')
        peak_success = filtered_df.groupby('PEAKID')['ANY_SUCCESS'].mean().reset_index(name='success_rate')
        peak_data = pd.merge(coords_df, peak_counts, on='PEAKID', how='inner')
        peak_data = pd.merge(peak_data, peak_success, on='PEAKID', how='inner')
        peak_data = pd.merge(peak_data, peaks_df[['PEAKID', 'PKNAME', 'HEIGHTM']], on='PEAKID', how='inner')
        
        # Destacar el pico seleccionado
        peak_data['selected'] = peak_data['PEAKID'] == selected_peak
        
        # Crear el mapa
        peaks_map = alt.Chart(peak_data).mark_circle().encode(
            longitude='LONGITUDE:Q',
            latitude='LATITUDE:Q',
            size=alt.Size('expeditions:Q', 
                         scale=alt.Scale(range=[100, 1000]), 
                         legend=alt.Legend(title="Number of Expeditions")),
            color=alt.Color('success_rate:Q', 
                          scale=alt.Scale(domain=[0, 0.5, 1], range=['#c22d2d', '#f7db4f', '#48c13d']), 
                          legend=alt.Legend(title="Success Rate")),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('HEIGHTM:Q', title='Height (m)'),
                alt.Tooltip('expeditions:Q', title='Expeditions'),
                alt.Tooltip('success_rate:Q', title='Success Rate', format='.1%')
            ],
            stroke=alt.condition(
                alt.datum.selected,
                alt.value('black'),
                alt.value(None)
            ),
            strokeWidth=alt.condition(
                alt.datum.selected,
                alt.value(2),
                alt.value(0)
            )
        ).properties(
            width=500,
            height=400
        ).project('mercator')
        
        st.altair_chart(peaks_map, use_container_width=True)
        
    with col2:
        # Evolución histórica de expediciones y tasas de éxito
        st.markdown("#### Historical Trends")
        
        # Preparar datos anuales
        yearly_data = filtered_df.groupby(['YEAR_INT']).agg(
            expeditions=('EXPID', 'count'),
            successes=('ANY_SUCCESS', 'sum')
        ).reset_index()
        yearly_data['success_rate'] = yearly_data['successes'] / yearly_data['expeditions']
        
        # Datos anuales para el pico seleccionado
        peak_yearly = filtered_df[filtered_df['PEAKID'] == selected_peak].groupby(['YEAR_INT']).agg(
            expeditions=('EXPID', 'count'),
            successes=('ANY_SUCCESS', 'sum')
        ).reset_index()
        peak_yearly['success_rate'] = peak_yearly['successes'] / peak_yearly['expeditions']
        
        # Doble eje Y para expediciones y tasa de éxito
        base = alt.Chart(yearly_data).encode(
            x=alt.X('YEAR_INT:O', axis=alt.Axis(title='Year'))
        )
        
        # Línea de expediciones
        line1 = base.mark_line(color='steelblue').encode(
            y=alt.Y('expeditions:Q', 
                   axis=alt.Axis(title='Number of Expeditions', titleColor='steelblue'))
        )
        
        # Línea de tasa de éxito
        line2 = base.mark_line(color='orange').encode(
            y=alt.Y('success_rate:Q', 
                   axis=alt.Axis(title='Success Rate', titleColor='orange', format='.0%'))
        )
        
        # Gráfico combinado
        historical_chart = alt.layer(line1, line2).resolve_scale(
            y='independent'
        ).properties(
            width=500,
            height=300,
            title='Overall Expeditions and Success Rates by Year'
        )
        
        # Gráfico para el pico seleccionado
        base_peak = alt.Chart(peak_yearly).encode(
            x=alt.X('YEAR_INT:O', axis=alt.Axis(title='Year'))
        )
        
        # Línea de expediciones para el pico seleccionado
        peak_line1 = base_peak.mark_line(color='steelblue').encode(
            y=alt.Y('expeditions:Q', 
                   axis=alt.Axis(title='Number of Expeditions', titleColor='steelblue'))
        )
        
        # Línea de tasa de éxito para el pico seleccionado
        peak_line2 = base_peak.mark_line(color='orange').encode(
            y=alt.Y('success_rate:Q', 
                   axis=alt.Axis(title='Success Rate', titleColor='orange', format='.0%'))
        )
        
        # Gráfico combinado para el pico seleccionado
        peak_chart = alt.layer(peak_line1, peak_line2).resolve_scale(
            y='independent'
        ).properties(
            width=500,
            height=300,
            title=f'Expeditions and Success Rates for {peak_info["PKNAME"]} by Year'
        )
        
        # Mostrar los dos gráficos
        st.altair_chart(historical_chart, use_container_width=True)
        st.altair_chart(peak_chart, use_container_width=True)
    
    # Estadísticas comparativas entre picos
    st.markdown("### Comparative Statistics Across Peaks")
    
    # Preparar datos para comparación
    peak_stats = filtered_df.groupby(['PEAKID', 'PKNAME']).agg(
        expeditions=('EXPID', 'count'),
        success_rate=('ANY_SUCCESS', 'mean'),
        avg_duration=('TOTDAYS', 'mean'),
        height=('HEIGHTM', 'first')
    ).reset_index()
    
    # Ordenar por número de expediciones
    peak_stats = peak_stats.sort_values('expeditions', ascending=False).head(20)
    
    # Gráfico de barras para comparar expediciones y tasas de éxito
    comparison_chart = alt.Chart(peak_stats).mark_bar().encode(
        x=alt.X('PKNAME:N', sort='-y', axis=alt.Axis(title='Peak', labelAngle=-45)),
        y=alt.Y('expeditions:Q', axis=alt.Axis(title='Number of Expeditions')),
        color=alt.Color('success_rate:Q', 
                       scale=alt.Scale(domain=[0, 0.5, 1], range=['#c22d2d', '#f7db4f', '#48c13d']),
                       legend=alt.Legend(title="Success Rate")),
        tooltip=[
            alt.Tooltip('PKNAME:N', title='Peak'),
            alt.Tooltip('height:Q', title='Height (m)'),
            alt.Tooltip('expeditions:Q', title='Expeditions'),
            alt.Tooltip('success_rate:Q', title='Success Rate', format='.1%'),
            alt.Tooltip('avg_duration:Q', title='Avg. Duration (days)', format='.1f')
        ]
    ).properties(
        width=800,
        height=400,
        title='Top 20 Peaks by Number of Expeditions'
    )
    
    st.altair_chart(comparison_chart, use_container_width=True)

# Tab 2: Routes & Success Rates ------------------------------------------
with tab2:
    st.markdown(f"### Success Rates by Route for {peak_info['PKNAME']}")
    st.markdown("""
    This visualization shows the success rates for different routes on the selected peak. The color of each bar indicates 
    the success rate, with green representing higher success rates and red representing lower success rates.
    """)
    
    # Filtrar datos de rutas para el pico seleccionado
    peak_routes = route_success_rates[route_success_rates['PEAKID'] == selected_peak]
    
    if not peak_routes.empty:
        # Ordenar rutas por tasa de éxito
        peak_routes = peak_routes.sort_values('success_rate', ascending=False)
        
        # Gráfico de barras para tasas de éxito por ruta
        route_chart = alt.Chart(peak_routes).mark_bar().encode(
            y=alt.Y('ROUTE:N', sort='-x', axis=alt.Axis(title='Route')),
            x=alt.X('success_rate:Q', 
                   axis=alt.Axis(title='Success Rate', format='.0%'), 
                   scale=alt.Scale(domain=[0, 1])),
            color=alt.Color('success_rate:Q', 
                          scale=alt.Scale(domain=[0, 0.25, 0.5, 0.75, 1.0], 
                                         range=['#c22d2d', '#e77e16', '#ffb533', '#d9e03f', '#48c13d']),
                          legend=alt.Legend(title='Success Rate')),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('ROUTE:N', title='Route'),
                alt.Tooltip('success_rate:Q', title='Success Rate', format='.1%'),
                alt.Tooltip('successful_attempts:Q', title='Successful Attempts'),
                alt.Tooltip('total_attempts:Q', title='Total Attempts')
            ]
        ).properties(
            width=700,
            height=400
        )
        
        st.altair_chart(route_chart, use_container_width=True)
        
        # Tabla de datos detallados
        st.markdown("#### Detailed Route Data")
        
        route_table = peak_routes[['ROUTE', 'total_attempts', 'successful_attempts', 'success_rate']].rename(
            columns={
                'ROUTE': 'Route',
                'total_attempts': 'Total Attempts',
                'successful_attempts': 'Successful Attempts',
                'success_rate': 'Success Rate'
            }
        )
        
        # Formatear la tasa de éxito
        route_table['Success Rate'] = route_table['Success Rate'].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(route_table, use_container_width=True)
    else:
        st.info(f"No route data available for {peak_info['PKNAME']} with the current filters.")

    # Comparación con otros picos
    st.markdown("### Route Success Comparison Across Peaks")
    
    # Obtener las rutas más comunes
    common_routes = route_success_rates['ROUTE'].value_counts().head(10).index.tolist()
    
    # Filtrar datos para las rutas comunes
    common_route_data = route_success_rates[route_success_rates['ROUTE'].isin(common_routes)]
    
    # Gráfico de barras agrupadas para comparar tasas de éxito por ruta y pico
    if not common_route_data.empty:
        route_comparison = alt.Chart(common_route_data).mark_bar().encode(
            x=alt.X('PKNAME:N', axis=alt.Axis(title='Peak', labelAngle=-45)),
            y=alt.Y('success_rate:Q', 
                   axis=alt.Axis(title='Success Rate', format='.0%'), 
                   scale=alt.Scale(domain=[0, 1])),
            color=alt.Color('ROUTE:N', legend=alt.Legend(title='Route')),
            column=alt.Column('ROUTE:N', header=alt.Header(labelAngle=-45)),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('ROUTE:N', title='Route'),
                alt.Tooltip('success_rate:Q', title='Success Rate', format='.1%'),
                alt.Tooltip('total_attempts:Q', title='Total Attempts')
            ]
        ).properties(
            width=120,
            height=300
        )
        
        st.altair_chart(route_comparison, use_container_width=True)
    else:
        st.info("Not enough common route data available with the current filters.")

# Tab 3: Countries -------------------------------------------------------
with tab3:
    st.markdown("### Expeditions Led by Countries Over Time")
    st.markdown("""
    These visualizations show which countries have led the most expeditions in different time periods. The line chart shows 
    trends over time, while the stacked bar chart shows the composition of expeditions by country in each decade.
    """)
    
    # Obtener los 10 países principales en general
    top_countries = filtered_df['HOST_FACTOR'].value_counts().head(10).index.tolist()
    
    # Datos de país por década filtrados
    country_decade_filtered = filtered_df[filtered_df['HOST_FACTOR'].isin(top_countries)].groupby(
        ['HOST_FACTOR', 'decade']
    ).size().reset_index(name='count')
    
    # Gráfico de líneas para la evolución de expediciones por país
    countries_chart = alt.Chart(country_decade_filtered).mark_line(point=True).encode(
        x=alt.X('decade:N', axis=alt.Axis(title='Decade')),
        y=alt.Y('count:Q', axis=alt.Axis(title='Number of Expeditions')),
        color=alt.Color('HOST_FACTOR:N', legend=alt.Legend(title='Host Country')),
        strokeWidth=alt.value(3),
        tooltip=[
            alt.Tooltip('HOST_FACTOR:N', title='Country'),
            alt.Tooltip('decade:N', title='Decade'),
            alt.Tooltip('count:Q', title='Expeditions')
        ]
    ).properties(
        width=700,
        height=400,
        title='Expeditions Led by Countries Over Time'
    )
    
    # Histograma apilado como complemento
    countries_stacked = alt.Chart(country_decade_filtered).mark_bar().encode(
        x=alt.X('decade:N', axis=alt.Axis(title='Decade')),
        y=alt.Y('count:Q', axis=alt.Axis(title='Number of Expeditions')),
        color=alt.Color('HOST_FACTOR:N', legend=None),
        tooltip=[
            alt.Tooltip('HOST_FACTOR:N', title='Country'),
            alt.Tooltip('decade:N', title='Decade'),
            alt.Tooltip('count:Q', title='Expeditions')
        ]
    ).properties(
        width=700,
        height=300,
        title='Stacked View of Expeditions by Country'
    )
    
    # Mostrar gráficos
    st.altair_chart(countries_chart, use_container_width=True)
    st.altair_chart(countries_stacked, use_container_width=True)
    
    # Expediciones por país para el pico seleccionado
    st.markdown(f"### Countries Leading Expeditions to {peak_info['PKNAME']}")
    
    # Filtrar datos para el pico seleccionado
    peak_countries = country_exped_by_peak[country_exped_by_peak['PEAKID'] == selected_peak].sort_values('count', ascending=False).head(10)
    
    if not peak_countries.empty:
        # Gráfico de barras para países con más expediciones al pico seleccionado
        peak_countries_chart = alt.Chart(peak_countries).mark_bar().encode(
            y=alt.Y('HOST_FACTOR:N', sort='-x', axis=alt.Axis(title='Country')),
            x=alt.X('count:Q', axis=alt.Axis(title='Number of Expeditions')),
            color=alt.Color('HOST_FACTOR:N', legend=None),
            tooltip=[
                alt.Tooltip('HOST_FACTOR:N', title='Country'),
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('count:Q', title='Expeditions')
            ]
        ).properties(
            width=700,
            height=400,
            title=f'Top 10 Countries Leading Expeditions to {peak_info["PKNAME"]}'
        )
        
        st.altair_chart(peak_countries_chart, use_container_width=True)
    else:
        st.info(f"No country data available for {peak_info['PKNAME']} with the current filters.")

# Tab 4: Duration & Success ---------------------------------------------
with tab4:
    st.markdown("### Relationship Between Expedition Duration and Success Rate")
    st.markdown("""
    These visualizations explore whether longer expeditions have a higher chance of summiting successfully for each peak, 
    and how this relationship varies by season.
    """)
    
    # Filtrar datos de duración para el pico seleccionado
    peak_duration = duration_success[duration_success['PEAKID'] == selected_peak]
    
    # Aplicar filtro de temporada si está seleccionado
    if selected_season != 'All':
        peak_duration = peak_duration[peak_duration['SEASON_FACTOR'] == selected_season]
    
    if not peak_duration.empty:
        # Gráfico de líneas para tasas de éxito por bin de duración y temporada
        duration_line = alt.Chart(peak_duration).mark_line(point=True).encode(
            x=alt.X('duration_bin:N', axis=alt.Axis(title='Expedition Duration (days)')),
            y=alt.Y('success_rate:Q', 
                   axis=alt.Axis(title='Success Rate', format='.0%'), 
                   scale=alt.Scale(domain=[0, 1])),
            color=alt.Color('SEASON_FACTOR:N', legend=alt.Legend(title='Season')),
            strokeWidth=alt.value(3),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('SEASON_FACTOR:N', title='Season'),
                alt.Tooltip('duration_bin:N', title='Duration (days)'),
                alt.Tooltip('success_rate:Q', title='Success Rate', format='.1%'),
                alt.Tooltip('total:Q', title='Total Expeditions')
            ]
        ).properties(
            width=700,
            height=400,
            title=f'Success Rate by Expedition Duration for {peak_info["PKNAME"]}'
        )
        
        st.altair_chart(duration_line, use_container_width=True)
        
        # Datos para el gráfico de distribución
        peak_duration_dist = filtered_df[
            (filtered_df['PEAKID'] == selected_peak) & 
            (filtered_df['TOTDAYS'] > 0)
        ]
        
        if selected_season != 'All':
            peak_duration_dist = peak_duration_dist[peak_duration_dist['SEASON_FACTOR'] == selected_season]
        
        # Histograma para la distribución de duración de expediciones
        if not peak_duration_dist.empty:
            duration_hist = alt.Chart(peak_duration_dist).mark_bar().encode(
                x=alt.X('TOTDAYS:Q', 
                       bin=alt.Bin(maxbins=30), 
                       axis=alt.Axis(title='Expedition Duration (days)')),
                y=alt.Y('count():Q', axis=alt.Axis(title='Number of Expeditions')),
                color=alt.Color('ANY_SUCCESS:N', 
                              scale=alt.Scale(domain=[True, False], range=['#48c13d', '#c22d2d']),
                              legend=alt.Legend(title='Summit Success')),
                tooltip=[
                    alt.Tooltip('ANY_SUCCESS:N', title='Success'),
                    alt.Tooltip('count():Q', title='Expeditions')
                ]
            ).properties(
                width=700,
                height=300,
                title=f'Distribution of Expedition Durations for {peak_info["PKNAME"]}'
            )
            
            st.altair_chart(duration_hist, use_container_width=True)
    else:
        st.info(f"No duration data available for {peak_info['PKNAME']} with the current filters.")
    
    # Comparación entre picos
    st.markdown("### Duration and Success Rate Comparison Across Peaks")
    
    # Preparar datos para la comparación
    duration_comparison = df_merged.groupby(['PEAKID', 'PKNAME', 'ANY_SUCCESS']).agg(
        avg_duration=('TOTDAYS', 'mean'),
        count=('EXPID', 'count')
    ).reset_index()
    
    # Filtrar para incluir solo picos con suficientes datos
    peak_counts = duration_comparison.groupby('PEAKID')['count'].sum()
    valid_peaks = peak_counts[peak_counts >= 20].index.tolist()
    duration_comparison = duration_comparison[duration_comparison['PEAKID'].isin(valid_peaks)]
    
    # Gráfico de dispersión para la comparación
    if not duration_comparison.empty:
        scatter_chart = alt.Chart(duration_comparison).mark_circle(size=100).encode(
            x=alt.X('avg_duration:Q', axis=alt.Axis(title='Average Expedition Duration (days)')),
            y=alt.Y('PKNAME:N', sort='x', axis=alt.Axis(title='Peak')),
            color=alt.Color('ANY_SUCCESS:N', 
                          scale=alt.Scale(domain=[True, False], range=['#48c13d', '#c22d2d']),
                          legend=alt.Legend(title='Summit Success')),
            size=alt.Size('count:Q', legend=alt.Legend(title='Number of Expeditions')),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('ANY_SUCCESS:N', title='Success'),
                alt.Tooltip('avg_duration:Q', title='Avg. Duration (days)', format='.1f'),
                alt.Tooltip('count:Q', title='Expeditions')
            ]
        ).properties(
            width=700,
            height=500,
            title='Relationship Between Expedition Duration and Success Across Peaks'
        )
        
        st.altair_chart(scatter_chart, use_container_width=True)
    else:
        st.info("Not enough data available for cross-peak duration comparison with the current filters.")

# Tab 5: Termination Reasons ---------------------------------------------
with tab5:
    st.markdown("### Evolution of Termination Reasons Over Time")
    st.markdown("""
    These visualizations show how the reasons for expedition termination have evolved over the years for each peak.
    The stacked area chart shows the proportion of different reasons, while the line chart allows tracking specific reasons.
    """)
    
    # Filtrar datos de terminación para el pico seleccionado
    peak_termination = term_evolution[term_evolution['PEAKID'] == selected_peak]
    
    if not peak_termination.empty:
        # Gráfico de área apilada para la evolución de razones
        termination_area = alt.Chart(peak_termination).mark_area().encode(
            x=alt.X('period:N', axis=alt.Axis(title='Time Period', labelAngle=-45)),
            y=alt.Y('percentage:Q', axis=alt.Axis(title='Percentage of Expeditions'), stack='normalize'),
            color=alt.Color('reason_grouped:N', 
                          scale=alt.Scale(scheme='category20'),
                          legend=alt.Legend(title='Termination Reason')),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('period:N', title='Period'),
                alt.Tooltip('reason_grouped:N', title='Termination Reason'),
                alt.Tooltip('percentage:Q', title='Percentage', format='.1f'),
                alt.Tooltip('count:Q', title='Expeditions'),
                alt.Tooltip('total:Q', title='Total in Period')
            ]
        ).properties(
            width=700,
            height=400,
            title=f'Evolution of Termination Reasons for {peak_info["PKNAME"]}'
        )
        
        # Gráfico de líneas para la evolución de razones específicas
        termination_line = alt.Chart(peak_termination).mark_line(point=True).encode(
            x=alt.X('period:N', axis=alt.Axis(title='Time Period', labelAngle=-45)),
            y=alt.Y('percentage:Q', axis=alt.Axis(title='Percentage of Expeditions')),
            color=alt.Color('reason_grouped:N', scale=alt.Scale(scheme='category20'), legend=None),
            strokeWidth=alt.value(3),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('period:N', title='Period'),
                alt.Tooltip('reason_grouped:N', title='Termination Reason'),
                alt.Tooltip('percentage:Q', title='Percentage', format='.1f'),
                alt.Tooltip('count:Q', title='Expeditions'),
                alt.Tooltip('total:Q', title='Total in Period')
            ]
        ).properties(
            width=700,
            height=300,
            title='Trend of Specific Termination Reasons'
        )
        
        # Mostrar gráficos
        st.altair_chart(termination_area, use_container_width=True)
        st.altair_chart(termination_line, use_container_width=True)
        
        # Gráfico de barras para totales generales
        termination_totals = peak_termination.groupby('reason_grouped')['count'].sum().reset_index()
        termination_totals = termination_totals.sort_values('count', ascending=False)
        
        termination_bars = alt.Chart(termination_totals).mark_bar().encode(
            y=alt.Y('reason_grouped:N', sort='-x', axis=alt.Axis(title='Termination Reason')),
            x=alt.X('count:Q', axis=alt.Axis(title='Number of Expeditions')),
            color=alt.Color('reason_grouped:N', scale=alt.Scale(scheme='category20'), legend=None),
            tooltip=[
                alt.Tooltip('reason_grouped:N', title='Termination Reason'),
                alt.Tooltip('count:Q', title='Expeditions')
            ]
        ).properties(
            width=700,
            height=300,
            title=f'Total Expeditions by Termination Reason for {peak_info["PKNAME"]}'
        )
        
        st.altair_chart(termination_bars, use_container_width=True)
    else:
        st.info(f"No termination reason data available for {peak_info['PKNAME']} with the current filters.")
    
    # Comparación entre picos
    st.markdown("### Termination Reasons Comparison Across Peaks")
    
    # Preparar datos para la comparación
    term_comparison = termination_df.groupby(['PEAKID', 'PKNAME', 'reason_grouped']).size().reset_index(name='count')
    term_comparison = term_comparison.merge(
        term_comparison.groupby(['PEAKID'])['count'].sum().reset_index(name='total'),
        on=['PEAKID']
    )
    term_comparison['percentage'] = term_comparison['count'] / term_comparison['total'] * 100
    
    # Filtrar para incluir solo los picos principales
    term_comparison = term_comparison[term_comparison['PEAKID'].isin(top_peaks)]
    
    # Mostrar solo las razones más comunes
    common_reasons = termination_df['reason_grouped'].value_counts().head(5).index.tolist()
    term_comparison = term_comparison[term_comparison['reason_grouped'].isin(common_reasons)]
    
    # Crear gráfico de calor para comparación
    if not term_comparison.empty:
        heatmap = alt.Chart(term_comparison).mark_rect().encode(
            x=alt.X('PKNAME:N', axis=alt.Axis(title='Peak', labelAngle=-45)),
            y=alt.Y('reason_grouped:N', axis=alt.Axis(title='Termination Reason')),
            color=alt.Color('percentage:Q',
                          scale=alt.Scale(scheme='viridis'),
                          legend=alt.Legend(title='Percentage of Expeditions')),
            tooltip=[
                alt.Tooltip('PKNAME:N', title='Peak'),
                alt.Tooltip('reason_grouped:N', title='Termination Reason'),
                alt.Tooltip('percentage:Q', title='Percentage', format='.1f'),
                alt.Tooltip('count:Q', title='Expeditions'),
                alt.Tooltip('total:Q', title='Total Expeditions')
            ]
        ).properties(
            width=700,
            height=300,
            title='Comparison of Termination Reasons Across Peaks'
        )
        
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Not enough data available for cross-peak termination reason comparison with the current filters.")

# Información sobre el proyecto
st.sidebar.markdown("---")
st.sidebar.markdown("### About this Project")
st.sidebar.info("""
This dashboard was created as part of a Himalayan Expeditions Data Visualization project. 
It allows exploration of patterns and relationships across routes, peaks, success rates, 
countries, and expedition characteristics.

**Author**: Claude 3.7 Sonnet
""")
