import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Análisis de Datos del Congreso - by @Gsnchez",
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
    .deputy-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .info-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #667eea;
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
    .author-credit {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
        font-weight: bold;
    }
    .author-credit a {
        color: white;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🏛️ Análisis de Datos del Congreso de los Diputados")
st.markdown("### Explorador Completo de Declaraciones Patrimoniales y de Ingresos")

# Author credit
st.markdown("""
<div class="author-credit">
    📊 Desarrollado por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a> (X/Twitter)
</div>
""", unsafe_allow_html=True)

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
    
    # Convert numeric columns
    numeric_columns = [
        'TOTAL_INGRESOS_DECLARADOS', 'TOTAL_ACTIVOS_LIQUIDOS', 'POSICION_NETA_LIQUIDA',
        'DEPOSITOS_SALDO_TOTAL', 'DEUDAS_SALDO_PENDIENTE_TOTAL', 'DEUDAS_IMPORTE_CONCEDIDO_TOTAL',
        'CANTIDAD_PAGADA_POR_IRPF', 'RENTAS_TOTAL_SALARIALES', 'RENTAS_TOTAL_DIVIDENDOS',
        'RENTAS_TOTAL_INTERESES', 'RENTAS_TOTAL_OTRAS', 'depositos_saldo_total_directo',
        'OTROS_NO_DECLARADOS_VALOR_TOTAL'
    ]
    
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert integer columns
    integer_columns = [
        'RENTAS_NUM_PERCEPCIONES_SALARIALES', 'RENTAS_NUM_DIVIDENDOS', 'RENTAS_NUM_INTERESES',
        'RENTAS_NUM_OTRAS', 'BIENES_NUM_INMUEBLES_URBANOS', 'BIENES_NUM_INMUEBLES_RUSTICOS',
        'BIENES_NUM_SOCIEDADES_NO_COTIZADAS', 'DEPOSITOS_NUM_CUENTAS', 'OTROS_BIENES_NUM_DEUDA_PUBLICA',
        'OTROS_BIENES_NUM_ACCIONES', 'OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT', 'VEHICULOS_NUM_TOTAL',
        'OTROS_NO_DECLARADOS_NUM', 'DEUDAS_NUM_TOTAL'
    ]
    
    for col in integer_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('Int64')
    
    # Normalize CARGO values
    df['CARGO'] = df['CARGO'].str.title()
    df['CARGO'] = df['CARGO'].replace({
        'Diputado': 'Diputado/a',
        'Diputada': 'Diputado/a',
        'Senador': 'Senador/a'
    })
    
    # Parse dates
    df['FECHA_ELECCION_PARLAMENTARIO'] = pd.to_datetime(df['FECHA_ELECCION_PARLAMENTARIO'], errors='coerce')
    df['FECHA_PRESENTACION_CREDENCIAL_CAMARA'] = pd.to_datetime(df['FECHA_PRESENTACION_CREDENCIAL_CAMARA'], errors='coerce')
    
    return df

df = load_data()

# Main navigation
main_tab = st.selectbox(
    "🔍 Selecciona el tipo de análisis:",
    ["📊 Análisis Agregado", "👤 Análisis Individual por Diputado/Senador"]
)

if main_tab == "👤 Análisis Individual por Diputado/Senador":
    st.markdown("## 👤 Análisis Individual de Parlamentarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Legislature selector
        selected_leg = st.selectbox(
            "Selecciona Legislatura:",
            options=sorted(df['LEGISLATURA'].dropna().unique()),
            index=0
        )
    
    # Filter by selected legislature
    df_leg = df[df['LEGISLATURA'] == selected_leg]
    
    with col2:
        # Name selector
        names = sorted(df_leg['NOMBRE_Y_APELLIDOS'].dropna().unique())
        selected_name = st.selectbox(
            "Selecciona Parlamentario/a:",
            options=names,
            index=0 if names else None
        )
    
    if selected_name:
        # Get deputy data
        deputy_data = df_leg[df_leg['NOMBRE_Y_APELLIDOS'] == selected_name].iloc[0]
        
        # Deputy header card
        st.markdown(f"""
        <div class="deputy-card">
            <h2 style="color: white; margin-top: 0;">{deputy_data['NOMBRE_Y_APELLIDOS']}</h2>
            <p style="font-size: 18px;">📍 {deputy_data['CIRCUNSCRIPCION']} | 🏛️ {deputy_data['CARGO']} | 📅 Legislatura {deputy_data['LEGISLATURA']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for individual analysis
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Información Personal", 
            "💰 Ingresos", 
            "🏠 Propiedades", 
            "💳 Activos Financieros",
            "📊 Deudas",
            "📄 Otros Datos"
        ])
        
        with tab1:
            st.markdown("### Información Personal y Parlamentaria")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Estado Civil:** {deputy_data['ESTADO_CIVIL'] if pd.notna(deputy_data['ESTADO_CIVIL']) else 'No declarado'}")
                st.info(f"**Régimen Económico Matrimonial:** {deputy_data['REGIMEN_ECONOMICO_MATRIMONIAL'] if pd.notna(deputy_data['REGIMEN_ECONOMICO_MATRIMONIAL']) else 'No declarado'}")
            with col2:
                if pd.notna(deputy_data['FECHA_ELECCION_PARLAMENTARIO']):
                    st.info(f"**Fecha de Elección:** {deputy_data['FECHA_ELECCION_PARLAMENTARIO'].strftime('%d/%m/%Y')}")
                if pd.notna(deputy_data['FECHA_PRESENTACION_CREDENCIAL_CAMARA']):
                    st.info(f"**Presentación Credencial:** {deputy_data['FECHA_PRESENTACION_CREDENCIAL_CAMARA'].strftime('%d/%m/%Y')}")
            
            if pd.notna(deputy_data['OBSERVACIONES']) and deputy_data['OBSERVACIONES'].strip():
                st.markdown("### 📝 Observaciones")
                st.write(deputy_data['OBSERVACIONES'])
        
        with tab2:
            st.markdown("### Declaración de Ingresos")
            
            # Income summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Ingresos Declarados", f"€{deputy_data['TOTAL_INGRESOS_DECLARADOS']:,.2f}")
            with col2:
                st.metric("IRPF Pagado", f"€{deputy_data['CANTIDAD_PAGADA_POR_IRPF']:,.2f}" if pd.notna(deputy_data['CANTIDAD_PAGADA_POR_IRPF']) else "No declarado")
            with col3:
                st.metric("Ingresos Salariales", f"€{deputy_data['RENTAS_TOTAL_SALARIALES']:,.2f}" if pd.notna(deputy_data['RENTAS_TOTAL_SALARIALES']) else "€0")
            with col4:
                st.metric("Otros Ingresos", f"€{deputy_data['RENTAS_TOTAL_OTRAS']:,.2f}" if pd.notna(deputy_data['RENTAS_TOTAL_OTRAS']) else "€0")
            
            # Income breakdown
            st.markdown("#### Desglose de Ingresos")
            income_data = {
                'Tipo de Ingreso': ['Salarios', 'Dividendos', 'Intereses', 'Otros'],
                'Cantidad': [
                    deputy_data['RENTAS_TOTAL_SALARIALES'] if pd.notna(deputy_data['RENTAS_TOTAL_SALARIALES']) else 0,
                    deputy_data['RENTAS_TOTAL_DIVIDENDOS'] if pd.notna(deputy_data['RENTAS_TOTAL_DIVIDENDOS']) else 0,
                    deputy_data['RENTAS_TOTAL_INTERESES'] if pd.notna(deputy_data['RENTAS_TOTAL_INTERESES']) else 0,
                    deputy_data['RENTAS_TOTAL_OTRAS'] if pd.notna(deputy_data['RENTAS_TOTAL_OTRAS']) else 0
                ],
                'Número de Percepciones': [
                    int(deputy_data['RENTAS_NUM_PERCEPCIONES_SALARIALES']) if pd.notna(deputy_data['RENTAS_NUM_PERCEPCIONES_SALARIALES']) else 0,
                    int(deputy_data['RENTAS_NUM_DIVIDENDOS']) if pd.notna(deputy_data['RENTAS_NUM_DIVIDENDOS']) else 0,
                    int(deputy_data['RENTAS_NUM_INTERESES']) if pd.notna(deputy_data['RENTAS_NUM_INTERESES']) else 0,
                    int(deputy_data['RENTAS_NUM_OTRAS']) if pd.notna(deputy_data['RENTAS_NUM_OTRAS']) else 0
                ]
            }
            
            income_df = pd.DataFrame(income_data)
            income_df = income_df[income_df['Cantidad'] > 0]
            
            if not income_df.empty:
                fig = px.pie(income_df, values='Cantidad', names='Tipo de Ingreso', 
                           title='Distribución de Ingresos por Tipo',
                           color_discrete_sequence=px.colors.sequential.Plasma)
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(income_df.style.format({'Cantidad': '€{:,.2f}'}), use_container_width=True)
            
            # Income details
            if pd.notna(deputy_data['RENTAS_DETALLE_SALARIALES']) and deputy_data['RENTAS_DETALLE_SALARIALES'].strip():
                st.markdown("#### Detalle de Ingresos Salariales")
                st.info(deputy_data['RENTAS_DETALLE_SALARIALES'])
            
            if pd.notna(deputy_data['RENTAS_DETALLE_OTRAS']) and deputy_data['RENTAS_DETALLE_OTRAS'].strip():
                st.markdown("#### Detalle de Otros Ingresos")
                st.info(deputy_data['RENTAS_DETALLE_OTRAS'])
        
        with tab3:
            st.markdown("### Propiedades e Inmuebles")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                urban = int(deputy_data['BIENES_NUM_INMUEBLES_URBANOS']) if pd.notna(deputy_data['BIENES_NUM_INMUEBLES_URBANOS']) else 0
                st.metric("Inmuebles Urbanos", urban)
            with col2:
                rustic = int(deputy_data['BIENES_NUM_INMUEBLES_RUSTICOS']) if pd.notna(deputy_data['BIENES_NUM_INMUEBLES_RUSTICOS']) else 0
                st.metric("Inmuebles Rústicos", rustic)
            with col3:
                vehicles = int(deputy_data['VEHICULOS_NUM_TOTAL']) if pd.notna(deputy_data['VEHICULOS_NUM_TOTAL']) else 0
                st.metric("Vehículos", vehicles)
            
            # Property details
            if pd.notna(deputy_data['BIENES_DETALLE_INMUEBLES_URBANOS']) and deputy_data['BIENES_DETALLE_INMUEBLES_URBANOS'].strip():
                st.markdown("#### Detalle Inmuebles Urbanos")
                st.info(deputy_data['BIENES_DETALLE_INMUEBLES_URBANOS'])
            
            if pd.notna(deputy_data['BIENES_DETALLE_INMUEBLES_RUSTICOS']) and deputy_data['BIENES_DETALLE_INMUEBLES_RUSTICOS'].strip():
                st.markdown("#### Detalle Inmuebles Rústicos")
                st.info(deputy_data['BIENES_DETALLE_INMUEBLES_RUSTICOS'])
            
            if pd.notna(deputy_data['VEHICULOS_DESCRIPCION']) and deputy_data['VEHICULOS_DESCRIPCION'].strip():
                st.markdown("#### Descripción de Vehículos")
                st.info(deputy_data['VEHICULOS_DESCRIPCION'])
            
            # Non-listed companies
            if int(deputy_data['BIENES_NUM_SOCIEDADES_NO_COTIZADAS']) > 0:
                st.markdown("#### Sociedades No Cotizadas")
                st.metric("Número de Sociedades", int(deputy_data['BIENES_NUM_SOCIEDADES_NO_COTIZADAS']))
                if pd.notna(deputy_data['BIENES_DETALLE_SOCIEDADES_NO_COTIZADAS']):
                    st.info(deputy_data['BIENES_DETALLE_SOCIEDADES_NO_COTIZADAS'])
        
        with tab4:
            st.markdown("### Activos Financieros y Depósitos")
            
            # Financial metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Activos Líquidos", f"€{deputy_data['TOTAL_ACTIVOS_LIQUIDOS']:,.2f}")
            with col2:
                st.metric("Saldo en Depósitos", f"€{deputy_data['DEPOSITOS_SALDO_TOTAL']:,.2f}")
            with col3:
                st.metric("Posición Neta Líquida", f"€{deputy_data['POSICION_NETA_LIQUIDA']:,.2f}")
            
            # Account details
            if int(deputy_data['DEPOSITOS_NUM_CUENTAS']) > 0:
                st.markdown("#### Cuentas y Depósitos")
                st.info(f"Número de cuentas: {int(deputy_data['DEPOSITOS_NUM_CUENTAS'])}")
                if pd.notna(deputy_data['DEPOSITOS_DETALLE_CUENTAS']) and deputy_data['DEPOSITOS_DETALLE_CUENTAS'].strip():
                    st.write("Detalle:", deputy_data['DEPOSITOS_DETALLE_CUENTAS'])
            
            # Other financial assets
            st.markdown("#### Otros Activos Financieros")
            
            financial_assets = []
            if int(deputy_data['OTROS_BIENES_NUM_DEUDA_PUBLICA']) > 0:
                financial_assets.append(f"Deuda Pública: {int(deputy_data['OTROS_BIENES_NUM_DEUDA_PUBLICA'])} títulos")
            if int(deputy_data['OTROS_BIENES_NUM_ACCIONES']) > 0:
                financial_assets.append(f"Acciones: {int(deputy_data['OTROS_BIENES_NUM_ACCIONES'])} posiciones")
            if int(deputy_data['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT']) > 0:
                financial_assets.append(f"Sociedades (>5%): {int(deputy_data['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT'])}")
            
            if financial_assets:
                for asset in financial_assets:
                    st.info(asset)
            else:
                st.write("No se declaran otros activos financieros")
            
            # Asset details
            if pd.notna(deputy_data['OTROS_BIENES_DETALLE_ACCIONES']) and deputy_data['OTROS_BIENES_DETALLE_ACCIONES'].strip():
                st.markdown("##### Detalle de Acciones")
                st.write(deputy_data['OTROS_BIENES_DETALLE_ACCIONES'])
            
            if pd.notna(deputy_data['OTROS_BIENES_DETALLE_SOCIEDADES_MAS_5PCT']) and deputy_data['OTROS_BIENES_DETALLE_SOCIEDADES_MAS_5PCT'].strip():
                st.markdown("##### Detalle de Sociedades (>5%)")
                st.write(deputy_data['OTROS_BIENES_DETALLE_SOCIEDADES_MAS_5PCT'])
        
        with tab5:
            st.markdown("### Deudas y Obligaciones Financieras")
            
            if int(deputy_data['DEUDAS_NUM_TOTAL']) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Número de Deudas", int(deputy_data['DEUDAS_NUM_TOTAL']))
                with col2:
                    st.metric("Importe Concedido Total", f"€{deputy_data['DEUDAS_IMPORTE_CONCEDIDO_TOTAL']:,.2f}" if pd.notna(deputy_data['DEUDAS_IMPORTE_CONCEDIDO_TOTAL']) else "No declarado")
                with col3:
                    st.metric("Saldo Pendiente Total", f"€{deputy_data['DEUDAS_SALDO_PENDIENTE_TOTAL']:,.2f}" if pd.notna(deputy_data['DEUDAS_SALDO_PENDIENTE_TOTAL']) else "No declarado")
                
                if pd.notna(deputy_data['DEUDAS_DESCRIPCION_ACREEDOR']) and deputy_data['DEUDAS_DESCRIPCION_ACREEDOR'].strip():
                    st.markdown("#### Descripción de Acreedores")
                    st.info(deputy_data['DEUDAS_DESCRIPCION_ACREEDOR'])
            else:
                st.info("No se declaran deudas pendientes")
        
        with tab6:
            st.markdown("### Otros Bienes y Derechos No Declarados")
            
            if int(deputy_data['OTROS_NO_DECLARADOS_NUM']) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Número de Otros Bienes", int(deputy_data['OTROS_NO_DECLARADOS_NUM']))
                with col2:
                    st.metric("Valor Total", f"€{deputy_data['OTROS_NO_DECLARADOS_VALOR_TOTAL']:,.2f}" if pd.notna(deputy_data['OTROS_NO_DECLARADOS_VALOR_TOTAL']) else "No valorado")
                
                if pd.notna(deputy_data['OTROS_NO_DECLARADOS_DESCRIPCION']) and deputy_data['OTROS_NO_DECLARADOS_DESCRIPCION'].strip():
                    st.markdown("#### Descripción")
                    st.info(deputy_data['OTROS_NO_DECLARADOS_DESCRIPCION'])
            else:
                st.info("No se declaran otros bienes o derechos")
            
            # Comparison with peers
            st.markdown("### 📊 Comparación con otros parlamentarios")
            
            # Get comparison data
            comparison_df = df_leg[df_leg['CARGO'] == deputy_data['CARGO']]
            
            # Create comparison metrics
            col1, col2 = st.columns(2)
            
            with col1:
                # Income percentile
                income_percentile = (comparison_df['TOTAL_INGRESOS_DECLARADOS'] <= deputy_data['TOTAL_INGRESOS_DECLARADOS']).mean() * 100
                st.metric(
                    "Percentil de Ingresos",
                    f"{income_percentile:.1f}%",
                    f"Entre {deputy_data['CARGO']}s de la {selected_leg} legislatura"
                )
            
            with col2:
                # Assets percentile
                assets_percentile = (comparison_df['TOTAL_ACTIVOS_LIQUIDOS'] <= deputy_data['TOTAL_ACTIVOS_LIQUIDOS']).mean() * 100
                st.metric(
                    "Percentil de Activos Líquidos",
                    f"{assets_percentile:.1f}%",
                    f"Entre {deputy_data['CARGO']}s de la {selected_leg} legislatura"
                )

else:  # Aggregate Analysis
    st.markdown("## 📊 Análisis Agregado")
    
    # Sidebar filters for aggregate analysis
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
    
    # Civil status filter
    estados_civiles = df['ESTADO_CIVIL'].dropna().unique()
    selected_estado_civil = st.sidebar.multiselect(
        "Estado Civil",
        options=estados_civiles,
        default=estados_civiles
    )
    
    # Apply filters
    filtered_df = df[
        (df['LEGISLATURA'].isin(selected_legislatura)) &
        (df['CARGO'].isin(selected_cargo)) &
        (df['CIRCUNSCRIPCION'].isin(selected_circunscripcion)) &
        (df['ESTADO_CIVIL'].isin(selected_estado_civil)) &
        (df['TOTAL_INGRESOS_DECLARADOS'] >= min_income) &
        (df['TOTAL_INGRESOS_DECLARADOS'] <= max_income)
    ]
    
    # Key metrics
    st.markdown("### 📈 Métricas Principales")
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            "Mediana Activos",
            f"€{median_assets:,.0f}",
            "Activos líquidos"
        )
    
    with col4:
        avg_irpf = filtered_df['CANTIDAD_PAGADA_POR_IRPF'].mean()
        st.metric(
            "IRPF Promedio",
            f"€{avg_irpf:,.0f}",
            "Impuesto pagado"
        )
    
    with col5:
        avg_debt = filtered_df['DEUDAS_SALDO_PENDIENTE_TOTAL'].mean()
        st.metric(
            "Deuda Promedio",
            f"€{avg_debt:,.0f}",
            "Saldo pendiente"
        )
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💰 Ingresos", 
        "🏛️ Por Cargo", 
        "🗺️ Geográfico", 
        "🏠 Patrimonio",
        "💳 Activos Financieros",
        "📊 Análisis Temporal",
        "📋 Datos Raw"
    ])
    
    with tab1:
        st.markdown("### Análisis de Ingresos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Income distribution
            fig_hist = px.histogram(
                filtered_df,
                x='TOTAL_INGRESOS_DECLARADOS',
                nbins=50,
                title='Distribución de Ingresos Totales',
                labels={'TOTAL_INGRESOS_DECLARADOS': 'Ingresos (€)', 'count': 'Parlamentarios'},
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(
                showlegend=False,
                height=400,
                xaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Income composition
            st.markdown("#### Composición de Ingresos")
            income_types = ['RENTAS_TOTAL_SALARIALES', 'RENTAS_TOTAL_DIVIDENDOS', 
                          'RENTAS_TOTAL_INTERESES', 'RENTAS_TOTAL_OTRAS']
            income_means = [filtered_df[col].mean() for col in income_types]
            
            fig_comp = px.pie(
                values=income_means,
                names=['Salarios', 'Dividendos', 'Intereses', 'Otros'],
                title='Composición Media de Ingresos',
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col2:
            # Box plot by legislature
            fig_box = px.box(
                filtered_df,
                x='LEGISLATURA',
                y='TOTAL_INGRESOS_DECLARADOS',
                title='Ingresos por Legislatura',
                color='LEGISLATURA',
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_box.update_layout(
                showlegend=False,
                height=400,
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
            # IRPF analysis
            st.markdown("#### Análisis IRPF")
            filtered_df['IRPF_Rate'] = (filtered_df['CANTIDAD_PAGADA_POR_IRPF'] / filtered_df['TOTAL_INGRESOS_DECLARADOS'] * 100)
            avg_rate = filtered_df['IRPF_Rate'].mean()
            
            fig_irpf = px.scatter(
                filtered_df,
                x='TOTAL_INGRESOS_DECLARADOS',
                y='CANTIDAD_PAGADA_POR_IRPF',
                title=f'IRPF vs Ingresos (Tasa media: {avg_rate:.1f}%)',
                labels={'TOTAL_INGRESOS_DECLARADOS': 'Ingresos (€)', 
                       'CANTIDAD_PAGADA_POR_IRPF': 'IRPF Pagado (€)'},
                color='LEGISLATURA',
                opacity=0.6
            )
            fig_irpf.update_layout(
                height=400,
                xaxis_tickformat=',.0f',
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_irpf, use_container_width=True)
        
        # Percentiles
        st.markdown("#### Percentiles de Ingresos")
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
            title='Distribución por Percentiles',
            xaxis_title='Percentil',
            yaxis_title='Ingresos (€)',
            yaxis_tickformat=',.0f',
            height=400
        )
        st.plotly_chart(fig_percentiles, use_container_width=True)
    
    with tab2:
        st.markdown("### Análisis por Cargo")
        
        # Comprehensive comparison by role
        cargo_stats = filtered_df.groupby('CARGO').agg({
            'TOTAL_INGRESOS_DECLARADOS': ['mean', 'median', 'std', 'count'],
            'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
            'DEPOSITOS_SALDO_TOTAL': 'mean',
            'CANTIDAD_PAGADA_POR_IRPF': 'mean',
            'DEUDAS_SALDO_PENDIENTE_TOTAL': 'mean',
            'BIENES_NUM_INMUEBLES_URBANOS': 'mean',
            'VEHICULOS_NUM_TOTAL': 'mean'
        }).round(2)
        
        cargo_stats.columns = ['Ingreso_Media', 'Ingreso_Mediana', 'Ingreso_StdDev', 'Cantidad',
                               'Activos_Media', 'Depositos_Media', 'IRPF_Media', 
                               'Deuda_Media', 'Inmuebles_Media', 'Vehiculos_Media']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Income comparison
            fig_cargo = go.Figure()
            fig_cargo.add_trace(go.Bar(
                name='Media',
                x=cargo_stats.index,
                y=cargo_stats['Ingreso_Media'],
                marker_color='#667eea'
            ))
            fig_cargo.add_trace(go.Bar(
                name='Mediana',
                x=cargo_stats.index,
                y=cargo_stats['Ingreso_Mediana'],
                marker_color='#764ba2'
            ))
            fig_cargo.update_layout(
                title='Comparación de Ingresos por Cargo',
                barmode='group',
                height=400,
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_cargo, use_container_width=True)
        
        with col2:
            # Asset comparison
            fig_assets = go.Figure()
            fig_assets.add_trace(go.Bar(
                name='Activos Líquidos',
                x=cargo_stats.index,
                y=cargo_stats['Activos_Media'],
                marker_color='#3498db'
            ))
            fig_assets.add_trace(go.Bar(
                name='Depósitos',
                x=cargo_stats.index,
                y=cargo_stats['Depositos_Media'],
                marker_color='#2ecc71'
            ))
            fig_assets.update_layout(
                title='Comparación de Activos por Cargo',
                barmode='group',
                height=400,
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_assets, use_container_width=True)
        
        # Property comparison
        st.markdown("#### Comparación de Propiedades por Cargo")
        fig_props = go.Figure()
        fig_props.add_trace(go.Bar(
            name='Inmuebles Urbanos (promedio)',
            x=cargo_stats.index,
            y=cargo_stats['Inmuebles_Media'],
            marker_color='#e74c3c'
        ))
        fig_props.add_trace(go.Bar(
            name='Vehículos (promedio)',
            x=cargo_stats.index,
            y=cargo_stats['Vehiculos_Media'],
            marker_color='#f39c12'
        ))
        fig_props.update_layout(
            title='Propiedades Promedio por Cargo',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_props, use_container_width=True)
        
        # Detailed table
        st.markdown("#### Estadísticas Detalladas por Cargo")
        st.dataframe(
            cargo_stats.style.format({
                'Ingreso_Media': '€{:,.0f}',
                'Ingreso_Mediana': '€{:,.0f}',
                'Ingreso_StdDev': '€{:,.0f}',
                'Activos_Media': '€{:,.0f}',
                'Depositos_Media': '€{:,.0f}',
                'IRPF_Media': '€{:,.0f}',
                'Deuda_Media': '€{:,.0f}',
                'Inmuebles_Media': '{:.1f}',
                'Vehiculos_Media': '{:.1f}',
                'Cantidad': '{:.0f}'
            }),
            use_container_width=True
        )
    
    with tab3:
        st.markdown("### Análisis Geográfico")
        
        # Geographic analysis
        geo_stats = filtered_df.groupby('CIRCUNSCRIPCION').agg({
            'TOTAL_INGRESOS_DECLARADOS': ['mean', 'count'],
            'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
            'BIENES_NUM_INMUEBLES_URBANOS': 'mean'
        }).round(2)
        geo_stats.columns = ['Ingreso_Media', 'Cantidad', 'Activos_Media', 'Inmuebles_Media']
        geo_stats = geo_stats.sort_values('Ingreso_Media', ascending=False)
        
        # Top 20 circumscriptions
        top_20 = geo_stats.head(20)
        
        fig_geo = px.bar(
            top_20.reset_index(),
            x='Ingreso_Media',
            y='CIRCUNSCRIPCION',
            orientation='h',
            title='Top 20 Circunscripciones por Ingreso Medio',
            text='Ingreso_Media',
            color='Cantidad',
            color_continuous_scale='Viridis'
        )
        fig_geo.update_traces(texttemplate='€%{text:,.0f}', textposition='outside')
        fig_geo.update_layout(
            height=600,
            xaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        
        # Scatter plot: Income vs Assets
        fig_scatter = px.scatter(
            geo_stats.reset_index(),
            x='Ingreso_Media',
            y='Activos_Media',
            size='Cantidad',
            hover_data=['CIRCUNSCRIPCION'],
            title='Relación Ingresos-Activos por Circunscripción',
            labels={'Ingreso_Media': 'Ingreso Medio (€)', 
                   'Activos_Media': 'Activos Líquidos Medio (€)'},
            color='Inmuebles_Media',
            color_continuous_scale='Plasma'
        )
        fig_scatter.update_layout(
            height=500,
            xaxis_tickformat=',.0f',
            yaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.markdown("### Análisis de Patrimonio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Property distribution
            st.markdown("#### Distribución de Propiedades")
            
            property_data = {
                'Tipo': ['Inmuebles Urbanos', 'Inmuebles Rústicos', 'Vehículos', 
                        'Sociedades No Cotizadas'],
                'Media': [
                    filtered_df['BIENES_NUM_INMUEBLES_URBANOS'].mean(),
                    filtered_df['BIENES_NUM_INMUEBLES_RUSTICOS'].mean(),
                    filtered_df['VEHICULOS_NUM_TOTAL'].mean(),
                    filtered_df['BIENES_NUM_SOCIEDADES_NO_COTIZADAS'].mean()
                ],
                'Total': [
                    filtered_df['BIENES_NUM_INMUEBLES_URBANOS'].sum(),
                    filtered_df['BIENES_NUM_INMUEBLES_RUSTICOS'].sum(),
                    filtered_df['VEHICULOS_NUM_TOTAL'].sum(),
                    filtered_df['BIENES_NUM_SOCIEDADES_NO_COTIZADAS'].sum()
                ]
            }
            
            fig_props = go.Figure()
            fig_props.add_trace(go.Bar(
                name='Promedio por Parlamentario',
                x=property_data['Tipo'],
                y=property_data['Media'],
                marker_color='#667eea',
                yaxis='y',
            ))
            fig_props.add_trace(go.Bar(
                name='Total Acumulado',
                x=property_data['Tipo'],
                y=property_data['Total'],
                marker_color='#764ba2',
                yaxis='y2',
            ))
            fig_props.update_layout(
                title='Distribución de Propiedades',
                yaxis=dict(title='Promedio', side='left'),
                yaxis2=dict(title='Total', overlaying='y', side='right'),
                height=400,
                barmode='group'
            )
            st.plotly_chart(fig_props, use_container_width=True)
            
            # Debt analysis
            st.markdown("#### Análisis de Deudas")
            debt_holders = filtered_df[filtered_df['DEUDAS_NUM_TOTAL'] > 0]
            
            col_debt1, col_debt2 = st.columns(2)
            with col_debt1:
                st.metric("% con Deudas", f"{len(debt_holders)/len(filtered_df)*100:.1f}%")
            with col_debt2:
                st.metric("Deuda Media (con deuda)", f"€{debt_holders['DEUDAS_SALDO_PENDIENTE_TOTAL'].mean():,.0f}")
            
            if len(debt_holders) > 0:
                fig_debt = px.histogram(
                    debt_holders,
                    x='DEUDAS_SALDO_PENDIENTE_TOTAL',
                    nbins=30,
                    title='Distribución de Deudas Pendientes',
                    color_discrete_sequence=['#e74c3c']
                )
                fig_debt.update_layout(
                    xaxis_tickformat=',.0f',
                    height=400
                )
                st.plotly_chart(fig_debt, use_container_width=True)
        
        with col2:
            # Civil status analysis
            st.markdown("#### Análisis por Estado Civil")
            civil_stats = filtered_df.groupby('ESTADO_CIVIL').agg({
                'TOTAL_INGRESOS_DECLARADOS': 'mean',
                'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
                'NOMBRE_Y_APELLIDOS': 'count'
            }).round(2)
            civil_stats.columns = ['Ingreso_Media', 'Activos_Media', 'Cantidad']
            
            fig_civil = px.bar(
                civil_stats.reset_index(),
                x='ESTADO_CIVIL',
                y='Ingreso_Media',
                title='Ingreso Medio por Estado Civil',
                text='Cantidad',
                color='Activos_Media',
                color_continuous_scale='Viridis'
            )
            fig_civil.update_traces(texttemplate='n=%{text}', textposition='outside')
            fig_civil.update_layout(
                height=400,
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_civil, use_container_width=True)
            
            # Economic regime analysis
            if 'REGIMEN_ECONOMICO_MATRIMONIAL' in filtered_df.columns:
                st.markdown("#### Régimen Económico Matrimonial")
                regime_stats = filtered_df[filtered_df['REGIMEN_ECONOMICO_MATRIMONIAL'].notna()].groupby('REGIMEN_ECONOMICO_MATRIMONIAL').agg({
                    'TOTAL_INGRESOS_DECLARADOS': 'mean',
                    'NOMBRE_Y_APELLIDOS': 'count'
                }).round(2)
                regime_stats.columns = ['Ingreso_Media', 'Cantidad']
                
                if not regime_stats.empty:
                    fig_regime = px.pie(
                        regime_stats.reset_index(),
                        values='Cantidad',
                        names='REGIMEN_ECONOMICO_MATRIMONIAL',
                        title='Distribución por Régimen Económico',
                        color_discrete_sequence=px.colors.sequential.Plasma
                    )
                    st.plotly_chart(fig_regime, use_container_width=True)
    
    with tab5:
        st.markdown("### Análisis de Activos Financieros")
        
        # Financial assets overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_deposits = filtered_df['DEPOSITOS_SALDO_TOTAL'].mean()
            st.metric("Saldo Medio en Depósitos", f"€{avg_deposits:,.0f}")
        
        with col2:
            avg_liquid = filtered_df['TOTAL_ACTIVOS_LIQUIDOS'].mean()
            st.metric("Activos Líquidos Medios", f"€{avg_liquid:,.0f}")
        
        with col3:
            avg_net = filtered_df['POSICION_NETA_LIQUIDA'].mean()
            st.metric("Posición Neta Media", f"€{avg_net:,.0f}")
        
        with col4:
            num_accounts = filtered_df['DEPOSITOS_NUM_CUENTAS'].mean()
            st.metric("Promedio Cuentas Bancarias", f"{num_accounts:.1f}")
        
        # Distribution of bank accounts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_accounts = px.histogram(
                filtered_df,
                x='DEPOSITOS_NUM_CUENTAS',
                title='Distribución del Número de Cuentas Bancarias',
                nbins=20,
                color_discrete_sequence=['#3498db']
            )
            fig_accounts.update_layout(
                xaxis_title='Número de Cuentas',
                yaxis_title='Parlamentarios',
                height=400
            )
            st.plotly_chart(fig_accounts, use_container_width=True)
        
        with col2:
            fig_deposits = px.box(
                filtered_df,
                y='DEPOSITOS_SALDO_TOTAL',
                x='LEGISLATURA',
                title='Distribución de Saldos en Depósitos por Legislatura',
                color='LEGISLATURA',
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_deposits.update_layout(
                yaxis_tickformat=',.0f',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_deposits, use_container_width=True)
        
        # Other financial assets
        st.markdown("#### Otros Activos Financieros")
        
        financial_summary = {
            'Tipo de Activo': ['Deuda Pública', 'Acciones', 'Sociedades (>5%)', 'Otros No Declarados'],
            'Parlamentarios con Activo': [
                (filtered_df['OTROS_BIENES_NUM_DEUDA_PUBLICA'] > 0).sum(),
                (filtered_df['OTROS_BIENES_NUM_ACCIONES'] > 0).sum(),
                (filtered_df['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT'] > 0).sum(),
                (filtered_df['OTROS_NO_DECLARADOS_NUM'] > 0).sum()
            ],
            'Cantidad Media (si tiene)': [
                filtered_df[filtered_df['OTROS_BIENES_NUM_DEUDA_PUBLICA'] > 0]['OTROS_BIENES_NUM_DEUDA_PUBLICA'].mean() if (filtered_df['OTROS_BIENES_NUM_DEUDA_PUBLICA'] > 0).any() else 0,
                filtered_df[filtered_df['OTROS_BIENES_NUM_ACCIONES'] > 0]['OTROS_BIENES_NUM_ACCIONES'].mean() if (filtered_df['OTROS_BIENES_NUM_ACCIONES'] > 0).any() else 0,
                filtered_df[filtered_df['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT'] > 0]['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT'].mean() if (filtered_df['OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT'] > 0).any() else 0,
                filtered_df[filtered_df['OTROS_NO_DECLARADOS_NUM'] > 0]['OTROS_NO_DECLARADOS_NUM'].mean() if (filtered_df['OTROS_NO_DECLARADOS_NUM'] > 0).any() else 0
            ]
        }
        
        fin_df = pd.DataFrame(financial_summary)
        
        fig_fin = px.bar(
            fin_df,
            x='Tipo de Activo',
            y='Parlamentarios con Activo',
            title='Parlamentarios con Otros Activos Financieros',
            text='Parlamentarios con Activo',
            color='Cantidad Media (si tiene)',
            color_continuous_scale='Plasma'
        )
        fig_fin.update_traces(texttemplate='%{text}', textposition='outside')
        fig_fin.update_layout(height=400)
        st.plotly_chart(fig_fin, use_container_width=True)
    
    with tab6:
        st.markdown("### Análisis Temporal")
        
        # Temporal analysis based on election dates
        if 'FECHA_ELECCION_PARLAMENTARIO' in filtered_df.columns:
            temporal_df = filtered_df[filtered_df['FECHA_ELECCION_PARLAMENTARIO'].notna()].copy()
            temporal_df['Año_Eleccion'] = temporal_df['FECHA_ELECCION_PARLAMENTARIO'].dt.year
            
            if not temporal_df.empty:
                yearly_stats = temporal_df.groupby('Año_Eleccion').agg({
                    'TOTAL_INGRESOS_DECLARADOS': 'mean',
                    'TOTAL_ACTIVOS_LIQUIDOS': 'mean',
                    'NOMBRE_Y_APELLIDOS': 'count'
                }).round(2)
                yearly_stats.columns = ['Ingreso_Media', 'Activos_Media', 'Cantidad']
                
                fig_temporal = go.Figure()
                fig_temporal.add_trace(go.Scatter(
                    x=yearly_stats.index,
                    y=yearly_stats['Ingreso_Media'],
                    mode='lines+markers',
                    name='Ingreso Medio',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=10)
                ))
                fig_temporal.add_trace(go.Scatter(
                    x=yearly_stats.index,
                    y=yearly_stats['Activos_Media'],
                    mode='lines+markers',
                    name='Activos Medios',
                    line=dict(color='#764ba2', width=3),
                    marker=dict(size=10),
                    yaxis='y2'
                ))
                fig_temporal.update_layout(
                    title='Evolución Temporal de Ingresos y Activos',
                    xaxis_title='Año de Elección',
                    yaxis=dict(title='Ingreso Medio (€)', side='left'),
                    yaxis2=dict(title='Activos Medios (€)', overlaying='y', side='right'),
                    height=500,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Legislature evolution
        st.markdown("#### Evolución por Legislatura")
        
        leg_evolution = filtered_df.groupby('LEGISLATURA').agg({
            'TOTAL_INGRESOS_DECLARADOS': ['mean', 'median'],
            'CANTIDAD_PAGADA_POR_IRPF': 'mean',
            'DEPOSITOS_SALDO_TOTAL': 'mean',
            'DEUDAS_SALDO_PENDIENTE_TOTAL': 'mean',
            'BIENES_NUM_INMUEBLES_URBANOS': 'mean',
            'VEHICULOS_NUM_TOTAL': 'mean'
        }).round(2)
        
        leg_evolution.columns = ['Ingreso_Media', 'Ingreso_Mediana', 'IRPF_Media', 
                                'Depositos_Media', 'Deuda_Media', 'Inmuebles_Media', 'Vehiculos_Media']
        
        # Create subplots
        fig_evolution = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Evolución Ingresos', 'Evolución IRPF', 'Evolución Depósitos',
                          'Evolución Deudas', 'Evolución Inmuebles', 'Evolución Vehículos')
        )
        
        # Add traces
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['Ingreso_Media'], 
                  name='Ingreso', marker_color='#667eea'),
            row=1, col=1
        )
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['IRPF_Media'], 
                  name='IRPF', marker_color='#764ba2'),
            row=1, col=2
        )
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['Depositos_Media'], 
                  name='Depósitos', marker_color='#3498db'),
            row=1, col=3
        )
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['Deuda_Media'], 
                  name='Deudas', marker_color='#e74c3c'),
            row=2, col=1
        )
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['Inmuebles_Media'], 
                  name='Inmuebles', marker_color='#2ecc71'),
            row=2, col=2
        )
        fig_evolution.add_trace(
            go.Bar(x=leg_evolution.index, y=leg_evolution['Vehiculos_Media'], 
                  name='Vehículos', marker_color='#f39c12'),
            row=2, col=3
        )
        
        fig_evolution.update_layout(height=600, showlegend=False, title_text="Evolución de Indicadores por Legislatura")
        st.plotly_chart(fig_evolution, use_container_width=True)
    
    with tab7:
        st.markdown("### Explorador de Datos Completos")
        
        # Search functionality
        search_term = st.text_input("🔎 Buscar por nombre:", "")
        
        if search_term:
            display_df = filtered_df[filtered_df['NOMBRE_Y_APELLIDOS'].str.contains(search_term, case=False, na=False)]
        else:
            display_df = filtered_df
        
        # Column categories
        column_categories = {
            'Información Básica': ['NOMBRE_Y_APELLIDOS', 'CARGO', 'CIRCUNSCRIPCION', 'LEGISLATURA', 
                                  'ESTADO_CIVIL', 'REGIMEN_ECONOMICO_MATRIMONIAL'],
            'Fechas': ['FECHA_ELECCION_PARLAMENTARIO', 'FECHA_PRESENTACION_CREDENCIAL_CAMARA'],
            'Ingresos': ['TOTAL_INGRESOS_DECLARADOS', 'CANTIDAD_PAGADA_POR_IRPF', 'RENTAS_TOTAL_SALARIALES',
                        'RENTAS_TOTAL_DIVIDENDOS', 'RENTAS_TOTAL_INTERESES', 'RENTAS_TOTAL_OTRAS'],
            'Activos': ['TOTAL_ACTIVOS_LIQUIDOS', 'POSICION_NETA_LIQUIDA', 'DEPOSITOS_SALDO_TOTAL'],
            'Propiedades': ['BIENES_NUM_INMUEBLES_URBANOS', 'BIENES_NUM_INMUEBLES_RUSTICOS', 
                          'VEHICULOS_NUM_TOTAL', 'BIENES_NUM_SOCIEDADES_NO_COTIZADAS'],
            'Deudas': ['DEUDAS_NUM_TOTAL', 'DEUDAS_IMPORTE_CONCEDIDO_TOTAL', 'DEUDAS_SALDO_PENDIENTE_TOTAL'],
            'Otros': ['OTROS_BIENES_NUM_DEUDA_PUBLICA', 'OTROS_BIENES_NUM_ACCIONES', 
                     'OTROS_BIENES_NUM_SOCIEDADES_MAS_5PCT', 'OTROS_NO_DECLARADOS_NUM']
        }
        
        # Column selector
        selected_category = st.selectbox(
            "Seleccionar categoría de columnas:",
            options=['Personalizado'] + list(column_categories.keys())
        )
        
        if selected_category == 'Personalizado':
            selected_columns = st.multiselect(
                "Seleccionar columnas a mostrar:",
                options=df.columns.tolist(),
                default=['NOMBRE_Y_APELLIDOS', 'CARGO', 'CIRCUNSCRIPCION', 'LEGISLATURA',
                        'TOTAL_INGRESOS_DECLARADOS', 'TOTAL_ACTIVOS_LIQUIDOS']
            )
        else:
            selected_columns = column_categories[selected_category]
        
        # Display filtered data
        st.markdown(f"**Mostrando {len(display_df)} registros**")
        
        # Format currency columns
        currency_cols = ['TOTAL_INGRESOS_DECLARADOS', 'TOTAL_ACTIVOS_LIQUIDOS', 
                        'DEPOSITOS_SALDO_TOTAL', 'POSICION_NETA_LIQUIDA',
                        'DEUDAS_SALDO_PENDIENTE_TOTAL', 'DEUDAS_IMPORTE_CONCEDIDO_TOTAL',
                        'CANTIDAD_PAGADA_POR_IRPF', 'RENTAS_TOTAL_SALARIALES',
                        'RENTAS_TOTAL_DIVIDENDOS', 'RENTAS_TOTAL_INTERESES', 'RENTAS_TOTAL_OTRAS']
        
        format_dict = {col: '€{:,.2f}' for col in currency_cols if col in selected_columns}
        
        # Add date formatting
        date_cols = ['FECHA_ELECCION_PARLAMENTARIO', 'FECHA_PRESENTACION_CREDENCIAL_CAMARA']
        for col in date_cols:
            if col in selected_columns:
                display_df[col] = display_df[col].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df[selected_columns].style.format(format_dict, na_rep='-'),
            use_container_width=True,
            height=600
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = display_df[selected_columns].to_csv(index=False)
            st.download_button(
                label="📥 Descargar datos filtrados (CSV)",
                data=csv,
                file_name='datos_congreso_filtrados.csv',
                mime='text/csv'
            )
        
        with col2:
            # Summary statistics for selected data
            if st.button("📊 Generar resumen estadístico"):
                summary = display_df[selected_columns].describe()
                st.markdown("##### Resumen Estadístico")
                st.dataframe(summary.style.format("{:.2f}"), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🏛️ Datos procesados desde fuentes públicas del Congreso de los Diputados</p>
    <p>📊 Aplicación desarrollada por <a href="https://twitter.com/Gsnchez" target="_blank">@Gsnchez</a></p>
    <p>⚠️ Esta aplicación es independiente y no tiene afiliación oficial con el Congreso</p>
    <p>📅 Los datos pueden no estar completamente actualizados - consulte fuentes oficiales para información definitiva</p>
</div>
""", unsafe_allow_html=True)
