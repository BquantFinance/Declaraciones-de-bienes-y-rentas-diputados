import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Deputies Information Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme aesthetics
st.markdown("""
<style>
    /* Main theme adjustments */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(145deg, #1e2435, #161b28);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header styling */
    .deputy-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .deputy-name {
        font-size: 2.5em;
        font-weight: bold;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .deputy-title {
        font-size: 1.2em;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 10px;
    }
    
    /* Section headers */
    .section-header {
        color: #667eea;
        font-size: 1.4em;
        font-weight: bold;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Info items */
    .info-item {
        margin: 12px 0;
        padding: 10px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        border-left: 3px solid #667eea;
    }
    
    .info-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .info-value {
        color: white;
        font-size: 1.1em;
        font-weight: 500;
    }
    
    /* Social media buttons */
    .social-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 25px;
        text-decoration: none;
        color: white;
        transition: all 0.3s;
    }
    
    .social-facebook {
        background: linear-gradient(45deg, #3b5998, #4267B2);
    }
    
    .social-twitter {
        background: linear-gradient(45deg, #1DA1F2, #4BC0FF);
    }
    
    .social-instagram {
        background: linear-gradient(45deg, #F58529, #DD2A7B, #8134AF);
    }
    
    .social-website {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    .social-button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    
    /* Empty state */
    .no-data {
        color: rgba(255, 255, 255, 0.4);
        font-style: italic;
        padding: 10px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1f2e 0%, #0e1117 100%);
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e2435, #161b28);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def parse_json_field(field_value):
    """Parse JSON string fields safely"""
    if pd.isna(field_value) or field_value == "[]" or field_value == "":
        return []
    try:
        return json.loads(field_value)
    except:
        return []

def format_currency(value):
    """Format currency values"""
    if pd.isna(value):
        return "No declarado"
    try:
        if isinstance(value, str):
            return value
        return f"{value:,.2f} €"
    except:
        return str(value)

def display_social_media(row):
    """Display social media links as buttons"""
    social_html = ""
    
    if pd.notna(row.get('facebook')) and row['facebook']:
        social_html += f'<a href="{row["facebook"]}" target="_blank" class="social-button social-facebook">📘 Facebook</a>'
    
    if pd.notna(row.get('twitter')) and row['twitter']:
        social_html += f'<a href="{row["twitter"]}" target="_blank" class="social-button social-twitter">🐦 Twitter</a>'
    
    if pd.notna(row.get('instagram')) and row['instagram']:
        social_html += f'<a href="{row["instagram"]}" target="_blank" class="social-button social-instagram">📷 Instagram</a>'
    
    if pd.notna(row.get('website')) and row['website']:
        social_html += f'<a href="{row["website"]}" target="_blank" class="social-button social-website">🌐 Website</a>'
    
    if social_html:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">{social_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-data">No hay redes sociales disponibles</div>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('deputies_complete_data.csv')
    return df

# Main app
def main():
    # Load data
    df = load_data()
    
    # Sidebar
    st.sidebar.markdown("# 🏛️ **Panel de Navegación**")
    st.sidebar.markdown("---")
    
    # Search and filter options
    search = st.sidebar.text_input("🔍 Buscar por nombre", "")
    
    # Filter by constituency
    constituencies = df['informacion_personal_circunscripcion'].dropna().unique()
    selected_constituency = st.sidebar.selectbox(
        "📍 Filtrar por circunscripción",
        ["Todas"] + sorted(constituencies.tolist())
    )
    
    # Filter dataframe
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search, case=False, na=False)]
    if selected_constituency != "Todas":
        filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
    
    # Deputy selector
    deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
    
    if not deputy_names:
        st.error("No se encontraron diputados con los criterios seleccionados")
        return
    
    selected_deputy = st.sidebar.selectbox(
        "👤 Seleccionar Diputado",
        deputy_names,
        format_func=lambda x: x if x else "Sin nombre"
    )
    
    # Statistics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 **Estadísticas**")
    st.sidebar.metric("Total Diputados", len(df))
    st.sidebar.metric("Resultados Filtrados", len(filtered_df))
    
    # Get selected deputy data
    deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
    
    # Main content area
    # Header with deputy name
    st.markdown(f"""
        <div class="deputy-header">
            <h1 class="deputy-name">{deputy_data['informacion_personal_nombre_y_apellidos']}</h1>
            <div class="deputy-title">{deputy_data['informacion_personal_cargo']} - {deputy_data['informacion_personal_circunscripcion']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Social Media
    display_social_media(deputy_data)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Información Personal", "💰 Rentas e IRPF", "🏠 Bienes Patrimoniales", "💳 Cuentas y Valores", "📝 Deudas y Otros"])
    
    with tab1:
        st.markdown('<div class="section-header">Información Personal</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-item">
                        <div class="info-label">Estado Civil</div>
                        <div class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Régimen Económico</div>
                        <div class="info-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial') or 'No aplica'}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-item">
                        <div class="info-label">Fecha de Elección</div>
                        <div class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Presentación de Credencial</div>
                        <div class="info-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-header">Rentas Percibidas</div>', unsafe_allow_html=True)
        
        # Salarios
        salarios = parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales'))
        if salarios:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**💼 Percepciones Salariales:**")
            for salario in salarios:
                concepto = salario.get('concepto', 'Sin especificar')
                euros = salario.get('euros', 'No declarado')
                st.markdown(f"- {concepto}: **{euros}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # IRPF
        st.markdown('<div class="section-header">Impuestos</div>', unsafe_allow_html=True)
        irpf = deputy_data.get('irpf_cantidad_pagada')
        st.markdown(f"""
            <div class="info-card">
                <div class="info-item">
                    <div class="info-label">IRPF - Cantidad Pagada</div>
                    <div class="info-value" style="font-size: 1.5em; color: #667eea;">{format_currency(irpf)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-header">Bienes Inmuebles</div>', unsafe_allow_html=True)
        
        # Inmuebles urbanos
        inmuebles_urbanos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos'))
        if inmuebles_urbanos:
            st.markdown("**🏢 Inmuebles Urbanos:**")
            for inmueble in inmuebles_urbanos:
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"**Tipo:** {inmueble.get('clase_y_caracteristicas', 'N/A')}")
                    st.markdown(f"**Ubicación:** {inmueble.get('situacion', 'N/A')}")
                with cols[1]:
                    st.markdown(f"**Adquisición:** {inmueble.get('fecha_adquisicion', 'N/A')}")
                    st.markdown(f"**Título:** {inmueble.get('titulo_adquisicion', 'N/A')}")
                with cols[2]:
                    st.markdown(f"**Derecho:** {inmueble.get('derecho_sobre_el_bien', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay inmuebles urbanos declarados</div>', unsafe_allow_html=True)
        
        # Vehículos
        st.markdown('<div class="section-header">Vehículos</div>', unsafe_allow_html=True)
        vehiculos = parse_json_field(deputy_data.get('vehiculos'))
        if vehiculos:
            for vehiculo in vehiculos:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-item">
                            <div class="info-label">🚗 Vehículo</div>
                            <div class="info-value">{vehiculo.get('descripcion', 'Sin descripción')}</div>
                            <div class="info-label" style="margin-top: 10px;">Año de Adquisición</div>
                            <div class="info-value">{vehiculo.get('fecha_adquisicion', 'No especificado')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay vehículos declarados</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="section-header">Cuentas y Depósitos</div>', unsafe_allow_html=True)
        
        cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
        if cuentas:
            for cuenta in cuentas:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-item">
                            <div class="info-label">💳 Descripción</div>
                            <div class="info-value">{cuenta.get('descripcion', 'Sin descripción')}</div>
                            <div class="info-label" style="margin-top: 10px;">Saldo</div>
                            <div class="info-value" style="font-size: 1.3em; color: #667eea;">{cuenta.get('saldo', 'No declarado')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay cuentas declaradas</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Valores y Acciones</div>', unsafe_allow_html=True)
        
        valores = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores'))
        if valores:
            for valor in valores:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-item">
                            <div class="info-label">📈 Descripción</div>
                            <div class="info-value">{valor.get('descripcion', 'Sin descripción')}</div>
                            <div class="info-label" style="margin-top: 10px;">Valor</div>
                            <div class="info-value">{valor.get('valor', 'No declarado')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay valores declarados</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<div class="section-header">Deudas y Obligaciones</div>', unsafe_allow_html=True)
        
        deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
        if deudas:
            for deuda in deudas:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-item">
                            <div class="info-label">📝 Tipo de Deuda</div>
                            <div class="info-value">{deuda.get('descripcion', 'Sin descripción')}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                            <div>
                                <div class="info-label">Fecha Concesión</div>
                                <div class="info-value">{deuda.get('fecha_concesion', 'N/A')}</div>
                            </div>
                            <div>
                                <div class="info-label">Importe Concedido</div>
                                <div class="info-value">{deuda.get('importe_concedido', 'N/A')}</div>
                            </div>
                            <div>
                                <div class="info-label">Saldo Pendiente</div>
                                <div class="info-value" style="color: #ff6b6b;">{deuda.get('saldo_pendiente', 'N/A')}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay deudas declaradas</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Otros Bienes</div>', unsafe_allow_html=True)
        
        otros = parse_json_field(deputy_data.get('otros_bienes_no_declarados_anteriormente'))
        if otros:
            for otro in otros:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-item">
                            <div class="info-label">📦 Descripción</div>
                            <div class="info-value">{otro.get('descripcion', 'Sin descripción')}</div>
                            <div class="info-label" style="margin-top: 10px;">Valor</div>
                            <div class="info-value">{otro.get('valor', 'No declarado')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay otros bienes declarados</div>', unsafe_allow_html=True)
        
        # Observaciones
        if pd.notna(deputy_data.get('observaciones')) and deputy_data.get('observaciones'):
            st.markdown('<div class="section-header">Observaciones</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-value">{deputy_data['observaciones']}</div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
