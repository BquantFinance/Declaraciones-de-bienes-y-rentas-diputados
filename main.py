import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Análisis de Datos del Congreso",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 30px;
        color: #856404;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    h2 {
        color: #334155;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🏛️ Análisis de Datos del Congreso de los Diputados")
st.markdown("### Explorador de Declaraciones Patrimoniales y de Ingresos")

# Disclaimer
st.markdown("""
<div class="disclaimer-box">
<h4>⚠️ Descargo de responsabilidad</h4>
<p><strong>Esta aplicación recopila y organiza información pública disponible en la página web del Congreso de los Diputados, incluyendo documentos en formato PDF.</strong> La aplicación no pertenece ni está vinculada de ninguna manera al Congreso de los Diputados, ni cuenta con su aval, autorización o patrocinio.</p>
<p>El contenido mostrado se ofrece únicamente con fines informativos y de acceso público. Aunque se procura garantizar la precisión y actualización de los datos, <strong>la aplicación puede contener errores, inexactitudes u omisiones, así como información incompleta o desactualizada</strong>. Para la consulta oficial, íntegra y auténtica de los documentos, se recomienda acudir directamente a la página web del Congreso de los Diputados.</p>
<p>El uso de esta aplicación es responsabilidad exclusiva del usuario.</p>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('datos_congreso_estructura_oficial.csv')
    # Clean data
    df['TOTAL_INGRESOS_DECLARADOS'] = pd.to_numeric(df['TOTAL_INGRESOS_DECLARADOS'], errors='coerce')
    df['TOTAL_ACTIVOS_LIQUIDOS'] = pd.to_numeric(df['TOTAL_ACTIVOS_LIQUIDOS'], errors='coerce')
    df['POSICION_NETA_LIQUIDA'] = pd.to_numeric(df['POSICION_NETA_LIQUIDA'], errors='coerce')
    df['DEPOSITOS_SALDO_TOTAL'] = pd.to_numeric(df['DEPOSITOS_SALDO_TOTAL'], errors='coerce')
    df['DEUDAS_SALDO_PENDIENTE_TOTAL'] = pd.to_numeric(df['DEUDAS_SALDO_PENDIENTE_TOTAL'], errors='coerce')
    
    # Normalize CARGO values
    df['CARGO'] = df['CARGO'].str.title()
    df['CARGO'] = df['CARGO'].replace({
        'Diputado': 'Diputado/a',
        'Diputada': 'Diputado/a',
        'Senador': 'Senador/a'
    })
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filtros")

# Legislature filter
legislaturas = sorted(df['LEGISLATURA'].dropna().unique())
selected_legislatura = st.sidebar.multiselect(
    "Legislatura",
    options=legislaturas,
    default=legislaturas
)

# Role filter
cargos = sorted(df['CARGO'].dropna().unique())
selected_cargo = st.sidebar.multiselect(
    "Cargo",
    options=cargos,
    default=cargos
)

# Circumscription filter
circunscripciones = sorted(df['CIRCUNSCRIPCION'].dropna().unique())
selected_circunscripcion = st.sidebar.multiselect(
    "Circunscripción",
    options=circunscripciones,
    default=circunscripciones[:10] if len(circunscripciones) > 10 else circunscripciones
)

# Income range filter
st.sidebar.subheader("Rango de Ingresos Declarados")
min_income = st.sidebar.number_input("Mínimo (€)", value=0, step=1000)
max_income = st.sidebar.number_input("Máximo (€)", value=int(df['TOTAL_INGRESOS_DECLARADOS'].max()), step=1000)

# Apply filters
filtered_df = df[
    (df['LEGISLATURA'].isin(selected_legislatura)) &
    (df['CARGO'].isin(selected_cargo)) &
    (df['CIRCUNSCRIPCION'].isin(selected_circunscripcion)) &
    (df['TOTAL_INGRESOS_DECLARADOS'] >= min_income) &
    (df['TOTAL_INGRESOS_DECLARADOS'] <= max_income)
]

# Key metrics
st.markdown("## 📊 Resumen General")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Parlamentarios",
        f"{len(filtered_df):,}",
        f"{len(filtered_df)/len(df)*100:.1f}% del total"
    )

with col2:
    avg_income = filtered_df['TOTAL_INGRESOS_DECLARADOS'].mean()
    st.metric(
        "Ingreso Promedio",
        f"€{avg_income:,.0f}",
        "Declarado anual"
    )

with col3:
    median_assets = filtered_df['TOTAL_ACTIVOS_LIQUIDOS'].median()
    st.metric(
        "Mediana Activos Líquidos",
        f"€{median_assets:,.0f}",
        "Valor mediano"
    )

with col4:
    avg_deposits = filtered_df['DEPOSITOS_SALDO_TOTAL'].mean()
    st.metric(
        "Saldo Promedio en Depósitos",
        f"€{avg_deposits:,.0f}",
        "En cuentas bancarias"
    )

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Distribución de Ingresos", "🏛️ Análisis por Cargo", 
                                         "🗺️ Análisis Geográfico", "💰 Patrimonio", "📋 Datos Detallados"])

with tab1:
    st.markdown("### Distribución de Ingresos Declarados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Income distribution histogram
        fig_hist = px.histogram(
            filtered_df,
            x='TOTAL_INGRESOS_DECLARADOS',
            nbins=50,
            title='Distribución de Ingresos Totales Declarados',
            labels={'TOTAL_INGRESOS_DECLARADOS': 'Ingresos (€)', 'count': 'Número de Parlamentarios'},
            color_discrete_sequence=['#667eea']
        )
        fig_hist.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickformat=',.0f',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot by legislature
        fig_box = px.box(
            filtered_df,
            x='LEGISLATURA',
            y='TOTAL_INGRESOS_DECLARADOS',
            title='Ingresos por Legislatura',
            labels={'TOTAL_INGRESOS_DECLARADOS': 'Ingresos (€)', 'LEGISLATURA': 'Legislatura'},
            color='LEGISLATURA',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig_box.update_layout(
            showlegend=False,
            height=400,
            yaxis_tickformat=',.0f',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Income percentiles
    st.markdown("### Percentiles de Ingresos")
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    income_percentiles = filtered_df['TOTAL_INGRESOS_DECLARADOS'].quantile([p/100 for p in percentiles])
    
    fig_percentiles = go.Figure(data=[
        go.Bar(
            x=[f"P{p}" for p in percentiles],
            y=income_percentiles.values,
            text=[f"€{v:,.0f}" for v in income_percentiles.values],
            textposition='auto',
            marker_color='#764ba2'
        )
    ])
    fig_percentiles.update_layout(
        title='Percentiles de Ingresos Declarados',
        xaxis_title='Percentil',
        yaxis_title='Ingresos (€)',
        yaxis_tickformat=',.0f',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_percentiles, use_container_width=True)

with tab2:
    st.markdown("### Análisis Comparativo por Cargo")
    
    # Average income by role
    income_by_cargo = filtered_df.groupby('CARGO').agg({
        'TOTAL_INGRESOS_DECLARADOS': ['mean', 'median', 'count'],
        'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
        'DEPOSITOS_SALDO_TOTAL': 'mean'
    }).round(2)
    
    income_by_cargo.columns = ['Ingreso Medio', 'Ingreso Mediano', 'Cantidad', 
                                'Activos Líquidos Medio', 'Depósitos Medio']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart for average income by role
        fig_cargo = px.bar(
            income_by_cargo.reset_index(),
            x='CARGO',
            y='Ingreso Medio',
            title='Ingreso Medio por Cargo',
            text='Ingreso Medio',
            color='Ingreso Medio',
            color_continuous_scale='Viridis'
        )
        fig_cargo.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
        fig_cargo.update_layout(
            showlegend=False,
            height=400,
            yaxis_tickformat=',.0f',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_cargo, use_container_width=True)
    
    with col2:
        # Comparison of median vs mean
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Bar(
            name='Media',
            x=income_by_cargo.index,
            y=income_by_cargo['Ingreso Medio'],
            marker_color='#667eea'
        ))
        fig_comparison.add_trace(go.Bar(
            name='Mediana',
            x=income_by_cargo.index,
            y=income_by_cargo['Ingreso Mediano'],
            marker_color='#764ba2'
        ))
        fig_comparison.update_layout(
            title='Media vs Mediana de Ingresos por Cargo',
            barmode='group',
            height=400,
            yaxis_tickformat=',.0f',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Display detailed table
    st.markdown("### Estadísticas Detalladas por Cargo")
    st.dataframe(
        income_by_cargo.style.format({
            'Ingreso Medio': '€{:,.0f}',
            'Ingreso Mediano': '€{:,.0f}',
            'Activos Líquidos Medio': '€{:,.0f}',
            'Depósitos Medio': '€{:,.0f}',
            'Cantidad': '{:.0f}'
        }),
        use_container_width=True
    )

with tab3:
    st.markdown("### Análisis Geográfico por Circunscripción")
    
    # Top circumscriptions by average income
    income_by_circ = filtered_df.groupby('CIRCUNSCRIPCION').agg({
        'TOTAL_INGRESOS_DECLARADOS': ['mean', 'count']
    }).round(2)
    income_by_circ.columns = ['Ingreso Medio', 'Cantidad']
    income_by_circ = income_by_circ.sort_values('Ingreso Medio', ascending=False)
    
    # Top 20 circumscriptions
    top_20_circ = income_by_circ.head(20)
    
    fig_circ = px.bar(
        top_20_circ.reset_index(),
        x='Ingreso Medio',
        y='CIRCUNSCRIPCION',
        orientation='h',
        title='Top 20 Circunscripciones por Ingreso Medio Declarado',
        text='Ingreso Medio',
        color='Ingreso Medio',
        color_continuous_scale='Plasma'
    )
    fig_circ.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
    fig_circ.update_layout(
        showlegend=False,
        height=600,
        xaxis_tickformat=',.0f',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_circ, use_container_width=True)
    
    # Scatter plot: Income vs Assets by Circumscription
    circ_summary = filtered_df.groupby('CIRCUNSCRIPCION').agg({
        'TOTAL_INGRESOS_DECLARADOS': 'mean',
        'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
        'NOMBRE_Y_APELLIDOS': 'count'
    }).reset_index()
    circ_summary.columns = ['Circunscripción', 'Ingreso Medio', 'Activos Líquidos Medio', 'Parlamentarios']
    
    fig_scatter = px.scatter(
        circ_summary,
        x='Ingreso Medio',
        y='Activos Líquidos Medio',
        size='Parlamentarios',
        hover_data=['Circunscripción'],
        title='Relación entre Ingresos y Activos Líquidos por Circunscripción',
        labels={'Ingreso Medio': 'Ingreso Medio (€)', 'Activos Líquidos Medio': 'Activos Líquidos Medio (€)'},
        color='Parlamentarios',
        color_continuous_scale='Viridis'
    )
    fig_scatter.update_layout(
        height=500,
        xaxis_tickformat=',.0f',
        yaxis_tickformat=',.0f',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    st.markdown("### Análisis de Patrimonio y Activos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Asset categories analysis
        asset_data = {
            'Categoría': ['Depósitos Bancarios', 'Activos Líquidos', 'Posición Neta'],
            'Media': [
                filtered_df['DEPOSITOS_SALDO_TOTAL'].mean(),
                filtered_df['TOTAL_ACTIVOS_LIQUIDOS'].mean(),
                filtered_df['POSICION_NETA_LIQUIDA'].mean()
            ],
            'Mediana': [
                filtered_df['DEPOSITOS_SALDO_TOTAL'].median(),
                filtered_df['TOTAL_ACTIVOS_LIQUIDOS'].median(),
                filtered_df['POSICION_NETA_LIQUIDA'].median()
            ]
        }
        
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Bar(
            name='Media',
            x=asset_data['Categoría'],
            y=asset_data['Media'],
            text=[f"€{v:,.0f}" for v in asset_data['Media']],
            textposition='auto',
            marker_color='#667eea'
        ))
        fig_assets.add_trace(go.Bar(
            name='Mediana',
            x=asset_data['Categoría'],
            y=asset_data['Mediana'],
            text=[f"€{v:,.0f}" for v in asset_data['Mediana']],
            textposition='auto',
            marker_color='#764ba2'
        ))
        fig_assets.update_layout(
            title='Comparación de Activos: Media vs Mediana',
            barmode='group',
            height=400,
            yaxis_tickformat=',.0f',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_assets, use_container_width=True)
    
    with col2:
        # Debt analysis
        debt_data = filtered_df[filtered_df['DEUDAS_SALDO_PENDIENTE_TOTAL'] > 0]
        
        if len(debt_data) > 0:
            fig_debt = px.histogram(
                debt_data,
                x='DEUDAS_SALDO_PENDIENTE_TOTAL',
                nbins=30,
                title='Distribución de Deudas Pendientes',
                labels={'DEUDAS_SALDO_PENDIENTE_TOTAL': 'Deuda Pendiente (€)', 'count': 'Número de Parlamentarios'},
                color_discrete_sequence=['#e74c3c']
            )
            fig_debt.update_layout(
                showlegend=False,
                height=400,
                xaxis_tickformat=',.0f',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_debt, use_container_width=True)
        else:
            st.info("No hay datos de deudas pendientes en la selección actual")
    
    # Properties analysis
    st.markdown("### Análisis de Propiedades Inmobiliarias")
    
    property_cols = ['BIENES_NUM_INMUEBLES_URBANOS', 'BIENES_NUM_INMUEBLES_RUSTICOS', 'VEHICULOS_NUM_TOTAL']
    property_data = filtered_df[property_cols].mean()
    
    fig_properties = go.Figure(data=[
        go.Bar(
            x=['Inmuebles Urbanos', 'Inmuebles Rústicos', 'Vehículos'],
            y=property_data.values,
            text=[f"{v:.1f}" for v in property_data.values],
            textposition='auto',
            marker_color=['#3498db', '#2ecc71', '#f39c12']
        )
    ])
    fig_properties.update_layout(
        title='Promedio de Propiedades por Parlamentario',
        xaxis_title='Tipo de Propiedad',
        yaxis_title='Cantidad Promedio',
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_properties, use_container_width=True)

with tab5:
    st.markdown("### Explorador de Datos Detallados")
    
    # Search functionality
    search_term = st.text_input("🔎 Buscar por nombre:", "")
    
    if search_term:
        display_df = filtered_df[filtered_df['NOMBRE_Y_APELLIDOS'].str.contains(search_term, case=False, na=False)]
    else:
        display_df = filtered_df
    
    # Select columns to display
    default_cols = ['NOMBRE_Y_APELLIDOS', 'CARGO', 'CIRCUNSCRIPCION', 'LEGISLATURA',
                    'TOTAL_INGRESOS_DECLARADOS', 'TOTAL_ACTIVOS_LIQUIDOS', 'DEPOSITOS_SALDO_TOTAL']
    
    selected_columns = st.multiselect(
        "Seleccionar columnas a mostrar:",
        options=df.columns.tolist(),
        default=default_cols
    )
    
    # Display filtered data
    st.markdown(f"**Mostrando {len(display_df)} registros**")
    
    # Format currency columns
    currency_cols = ['TOTAL_INGRESOS_DECLARADOS', 'TOTAL_ACTIVOS_LIQUIDOS', 
                     'DEPOSITOS_SALDO_TOTAL', 'POSICION_NETA_LIQUIDA',
                     'DEUDAS_SALDO_PENDIENTE_TOTAL', 'DEUDAS_IMPORTE_CONCEDIDO_TOTAL']
    
    format_dict = {col: '€{:,.2f}' for col in currency_cols if col in selected_columns}
    
    st.dataframe(
        display_df[selected_columns].style.format(format_dict, na_rep='-'),
        use_container_width=True,
        height=600
    )
    
    # Download button
    csv = display_df[selected_columns].to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name='datos_congreso_filtrados.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📊 Datos procesados desde fuentes públicas del Congreso de los Diputados</p>
    <p>Esta aplicación es independiente y no tiene afiliación oficial con el Congreso</p>
</div>
""", unsafe_allow_html=True)
