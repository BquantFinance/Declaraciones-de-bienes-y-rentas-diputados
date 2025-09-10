import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import glob
import base64

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced dark mode CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Dark mode base with better gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Enhanced hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 30px;
        border-radius: 20px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Compact individual card */
    .individual-card {
        background: rgba(30, 30, 45, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .individual-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Metric containers */
    .metric-container {
        background: rgba(40, 40, 55, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        padding: 15px;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        background: rgba(50, 50, 65, 0.6);
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Info cards with better contrast */
    .info-card {
        background: rgba(40, 40, 55, 0.4);
        border-left: 3px solid #667eea;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        color: #e0e0e0;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .info-card:hover {
        background: rgba(50, 50, 65, 0.5);
        transform: translateX(3px);
    }
    
    .info-card strong {
        color: #a0b0ff;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 30, 45, 0.4);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(224, 224, 224, 0.7);
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: white;
    }
    
    /* Better buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Input fields */
    .stSelectbox > div > div,
    .stTextInput > div > div {
        background: rgba(30, 30, 45, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        color: #e0e0e0;
    }
    
    .stSelectbox > div > div:hover,
    .stTextInput > div > div:hover {
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Data tables */
    .dataframe {
        background: rgba(30, 30, 45, 0.4) !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
        color: #e0e0e0 !important;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .dataframe thead th {
        background: rgba(102, 126, 234, 0.15) !important;
        color: white !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(102, 126, 234, 0.08) !important;
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #e0e0e0 !important;
        font-weight: 700 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 45, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        color: #e0e0e0;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(40, 40, 55, 0.5);
    }
    
    /* Comparison card */
    .comparison-card {
        background: rgba(30, 30, 45, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* VS header */
    .vs-header {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 20px 0;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 30, 45, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: #e0e0e0 !important;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: rgba(30, 30, 45, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="metric-container"]:hover {
        background: rgba(40, 40, 55, 0.5);
        border-color: rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False

# Helper functions
def parse_money_value(value):
    """Convert string money values to float"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    value_str = str(value).replace('€', '').replace('.', '').replace(',', '.')
    value_str = value_str.strip()
    try:
        return float(value_str)
    except:
        return 0

def get_deputy_photo(deputy_index):
    """Get the actual deputy photo from fotos_diputados folder"""
    photo_path = f"fotos_diputados/deputy_{deputy_index:03d}.jpg"
    if os.path.exists(photo_path):
        return photo_path
    return None

def get_hemiciclo_seat(deputy_index):
    """Get hemiciclo seat visualization"""
    pattern = f"hemiciclo/hemi_{deputy_index:04d}_*.gif"
    files = glob.glob(pattern)
    if files:
        return files[0]
    return None

# Load JSON data
def load_json_data():
    try:
        with open('all_deputies_merged.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        processed_data = []
        
        for idx, entry in enumerate(json_data, 1):
            if 'data' in entry and entry['data']:
                data = entry['data']
                personal_info = data.get('informacion_personal', {})
                
                processed_data.append({
                    'deputy_index': idx,
                    'Nombre': personal_info.get('nombre_y_apellidos', '').upper(),
                    'Cargo': personal_info.get('cargo', 'Diputado'),
                    'Circunscripción': personal_info.get('circunscripcion', ''),
                    'Estado Civil': personal_info.get('estado_civil', ''),
                    'Régimen Económico': personal_info.get('regimen_economico_matrimonial', ''),
                })
        
        return pd.DataFrame(processed_data), json_data
        
    except FileNotFoundError:
        st.error("No se encuentra el archivo 'all_deputies_merged.json'")
        return pd.DataFrame(), []
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        return pd.DataFrame(), []

# Show disclaimer if not accepted
if not st.session_state.disclaimer_accepted:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
        <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("## ⚠️ **Descargo de Responsabilidad Legal**")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([0.5, 10, 0.5])
        
        with col2:
            st.info("""
            **Esta aplicación constituye una herramienta independiente de análisis y visualización de información pública** 
            disponible en el portal oficial del Congreso de los Diputados. No mantiene vinculación institucional alguna con el 
            Congreso de los Diputados, sus órganos de gobierno, ni cuenta con aval, autorización o respaldo oficial de dicha institución.
            """)
            
            st.warning("""
            Los datos presentados provienen de fuentes públicas oficiales y, si bien se ha procurado garantizar su exactitud mediante 
            procesos automatizados de extracción y estructuración, **la aplicación podría contener errores, inexactitudes, 
            omisiones o información desactualizada** derivados del procesamiento de los documentos originales.
            """)
            
            st.markdown("""
            <div style="background: rgba(102, 126, 234, 0.1); border-radius: 12px; padding: 20px; margin: 20px 0; 
                        border: 1px solid rgba(102, 126, 234, 0.3);">
                <p style="text-align: center; color: #e0e0e0; font-size: 1rem; margin: 0;">
                    ✅ Al hacer clic en <strong>"Aceptar y Continuar"</strong>, usted reconoce haber leído y comprendido este descargo de responsabilidad.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ **Aceptar y Continuar**", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    
    st.stop()

# Main App - Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
    <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
</div>
""", unsafe_allow_html=True)

# Load data
df, json_data = load_json_data()

if not df.empty:
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos"])
    
    with tab1:
        # Comparison mode toggle
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            comparison_mode = st.checkbox("📊 Modo Comparación", value=st.session_state.comparison_mode)
            st.session_state.comparison_mode = comparison_mode
        
        if not comparison_mode:
            # Single deputy analysis - COMPACT VERSION
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("🔎 Buscar por nombre:", placeholder="Introduzca el nombre del parlamentario...")
            
            # Filter names
            if search_term:
                filtered_df = df[df['Nombre'].str.contains(search_term, case=False, na=False)]
                names = sorted(filtered_df['Nombre'].unique())
            else:
                names = sorted(df['Nombre'].unique())
            
            if names:
                selected_name = st.selectbox("Seleccione parlamentario:", names, key="single_select")
                
                if selected_name:
                    person_idx = df[df['Nombre'] == selected_name]['deputy_index'].iloc[0]
                    deputy_data = json_data[person_idx - 1]['data'] if person_idx <= len(json_data) else {}
                    personal_info = deputy_data.get('informacion_personal', {})
                    
                    # Compact card with photo and basic info
                    st.markdown('<div class="individual-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2.5, 1.5])
                    
                    with col1:
                        # Photo section (compact)
                        photo_path = get_deputy_photo(person_idx)
                        if photo_path:
                            with open(photo_path, "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read()).decode()
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <img src="data:image/jpeg;base64,{encoded_string}" 
                                     style="width: 120px; height: 160px; object-fit: cover; 
                                            border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background: rgba(102, 126, 234, 0.2); width: 120px; height: 160px; 
                                        border-radius: 10px; display: flex; align-items: center; 
                                        justify-content: center; margin: 0 auto;">
                                <div style="text-align: center;">
                                    <div style="font-size: 3rem;">👤</div>
                                    <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Sin foto</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Name and basic info (compact)
                        st.markdown(f"""
                        <div style="padding-left: 15px;">
                            <h3 style="color: #e0e0e0; margin: 0 0 10px 0; font-size: 1.6rem;">
                                {personal_info.get('nombre_y_apellidos', '').upper()}
                            </h3>
                            <p style="color: rgba(224,224,224,0.8); margin: 5px 0; font-size: 0.9rem;">
                                📍 <strong>{personal_info.get('circunscripcion', '')}</strong>
                            </p>
                            <p style="color: rgba(224,224,224,0.8); margin: 5px 0; font-size: 0.9rem;">
                                🏛️ {personal_info.get('cargo', 'Diputado')}
                            </p>
                            <p style="color: rgba(224,224,224,0.8); margin: 5px 0; font-size: 0.9rem;">
                                💑 {personal_info.get('estado_civil', '')}
                            </p>
                            {f'<p style="color: rgba(224,224,224,0.8); margin: 5px 0; font-size: 0.9rem;">📜 {personal_info.get("regimen_economico_matrimonial", "")}</p>' 
                             if personal_info.get('regimen_economico_matrimonial') else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        # Hemiciclo seat (compact)
                        seat_path = get_hemiciclo_seat(person_idx)
                        if seat_path:
                            with open(seat_path, "rb") as image_file:
                                encoded_seat = base64.b64encode(image_file.read()).decode()
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <img src="data:image/gif;base64,{encoded_seat}" 
                                     style="width: 100px; border-radius: 8px;">
                                <p style="color: rgba(224,224,224,0.5); font-size: 0.65rem; 
                                         margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;">Escaño</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Tabs for different sections of raw data
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "💰 Rentas", 
                        "🏠 Bienes", 
                        "💳 Cuentas",
                        "📊 Deudas",
                        "🚗 Vehículos"
                    ])
                    
                    with tab1:
                        # Show actual income data from JSON
                        rentas = deputy_data.get('rentas_percibidas', {})
                        
                        if rentas.get('percepciones_salariales'):
                            st.markdown("**Percepciones Salariales:**")
                            for salary in rentas['percepciones_salariales']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • {salary.get('concepto', 'Sin concepto')}: <strong>€{salary.get('euros', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if rentas.get('dividendos_y_participaciones'):
                            st.markdown("**Dividendos y Participaciones:**")
                            for div in rentas['dividendos_y_participaciones']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • {div.get('concepto', 'Sin concepto')}: <strong>€{div.get('euros', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if rentas.get('intereses_financieros'):
                            st.markdown("**Intereses Financieros:**")
                            for interest in rentas['intereses_financieros']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • {interest.get('concepto', 'Sin concepto')}: <strong>€{interest.get('euros', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if rentas.get('otras_rentas'):
                            st.markdown("**Otras Rentas:**")
                            for other in rentas['otras_rentas']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • {other.get('concepto', 'Sin concepto')}: <strong>€{other.get('euros', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # IRPF
                        irpf = deputy_data.get('irpf', {})
                        if irpf:
                            st.markdown(f"""
                            <div class="info-card" style="background: rgba(255,193,7,0.1); border-left-color: #ffc107;">
                                <strong>IRPF Pagado:</strong> €{irpf.get('cantidad_pagada', 0)}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with tab2:
                        # Show actual property data
                        bienes = deputy_data.get('bienes_patrimoniales', {})
                        
                        if bienes.get('inmuebles_urbanos'):
                            st.markdown("**Inmuebles Urbanos:**")
                            for prop in bienes['inmuebles_urbanos']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{prop.get('tipo', 'Inmueble')}</strong> - {prop.get('provincia', '')}
                                    <br>&nbsp;&nbsp;&nbsp;Derecho: {prop.get('derecho', '')} | Porcentaje: {prop.get('porcentaje', '')}%
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if bienes.get('inmuebles_rusticos'):
                            st.markdown("**Inmuebles Rústicos:**")
                            for prop in bienes['inmuebles_rusticos']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{prop.get('tipo', 'Inmueble')}</strong> - {prop.get('provincia', '')}
                                    <br>&nbsp;&nbsp;&nbsp;Derecho: {prop.get('derecho', '')} | Porcentaje: {prop.get('porcentaje', '')}%
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if not bienes.get('inmuebles_urbanos') and not bienes.get('inmuebles_rusticos'):
                            st.markdown("*No hay propiedades declaradas*")
                    
                    with tab3:
                        # Show actual account data
                        cuentas_data = deputy_data.get('depositos_y_cuentas', {})
                        
                        if cuentas_data.get('cuentas'):
                            st.markdown("**Cuentas y Depósitos:**")
                            for cuenta in cuentas_data['cuentas']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{cuenta.get('tipo', 'Cuenta')}</strong>
                                    <br>&nbsp;&nbsp;&nbsp;Saldo: <strong>€{cuenta.get('saldo', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        valores = deputy_data.get('valores_y_participaciones', {})
                        if valores.get('valores'):
                            st.markdown("**Valores y Participaciones:**")
                            for valor in valores['valores']:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{valor.get('entidad', 'Entidad')}</strong>
                                    <br>&nbsp;&nbsp;&nbsp;Valor: €{valor.get('valor_euros', 0)}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if not cuentas_data.get('cuentas') and not valores.get('valores'):
                            st.markdown("*No hay cuentas o valores declarados*")
                    
                    with tab4:
                        # Show actual debt data
                        deudas = deputy_data.get('deudas_y_obligaciones', [])
                        
                        if deudas:
                            st.markdown("**Deudas y Obligaciones:**")
                            for deuda in deudas:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{deuda.get('tipo', 'Deuda')}</strong> - {deuda.get('entidad', '')}
                                    <br>&nbsp;&nbsp;&nbsp;Saldo pendiente: <strong>€{deuda.get('saldo_pendiente', 0)}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("*No hay deudas declaradas*")
                    
                    with tab5:
                        # Show actual vehicle data
                        vehiculos = deputy_data.get('vehiculos', [])
                        
                        if vehiculos:
                            st.markdown("**Vehículos:**")
                            for vehiculo in vehiculos:
                                st.markdown(f"""
                                <div class="info-card">
                                    • <strong>{vehiculo.get('marca', '')} {vehiculo.get('modelo', '')}</strong>
                                    <br>&nbsp;&nbsp;&nbsp;Año: {vehiculo.get('fecha_adquisicion', '')}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("*No hay vehículos declarados*")
        
        else:
            # Comparison mode
            st.markdown("### 📊 Comparación entre Parlamentarios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="comparison-card">', unsafe_allow_html=True)
                names1 = sorted(df['Nombre'].unique())
                selected_name1 = st.selectbox("Primer parlamentario:", names1, key="compare1")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="comparison-card">', unsafe_allow_html=True)
                names2 = sorted(df['Nombre'].unique())
                selected_name2 = st.selectbox("Segundo parlamentario:", names2, key="compare2")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if selected_name1 and selected_name2:
                st.markdown('<h2 class="vs-header">VS</h2>', unsafe_allow_html=True)
                
                # Get data for both deputies
                idx1 = df[df['Nombre'] == selected_name1]['deputy_index'].iloc[0]
                idx2 = df[df['Nombre'] == selected_name2]['deputy_index'].iloc[0]
                
                data1 = json_data[idx1 - 1]['data'] if idx1 <= len(json_data) else {}
                data2 = json_data[idx2 - 1]['data'] if idx2 <= len(json_data) else {}
                
                # Compare key metrics
                col1, col2, col3 = st.columns([2, 1, 2])
                
                # Count properties for each
                props1 = len(data1.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', [])) + \
                        len(data1.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                props2 = len(data2.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', [])) + \
                        len(data2.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                
                vehicles1 = len(data1.get('vehiculos', []))
                vehicles2 = len(data2.get('vehiculos', []))
                
                accounts1 = len(data1.get('depositos_y_cuentas', {}).get('cuentas', []))
                accounts2 = len(data2.get('depositos_y_cuentas', {}).get('cuentas', []))
                
                debts1 = len(data1.get('deudas_y_obligaciones', []))
                debts2 = len(data2.get('deudas_y_obligaciones', []))
                
                with col1:
                    st.metric(selected_name1[:25], f"{props1} propiedades")
                    st.metric("", f"{vehicles1} vehículos")
                    st.metric("", f"{accounts1} cuentas")
                    st.metric("", f"{debts1} deudas")
                
                with col2:
                    st.markdown("<div style='text-align: center; padding-top: 50px;'>", unsafe_allow_html=True)
                    st.markdown("<p>🏠</p>", unsafe_allow_html=True)
                    st.markdown("<p>🚗</p>", unsafe_allow_html=True)
                    st.markdown("<p>💳</p>", unsafe_allow_html=True)
                    st.markdown("<p>📊</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col3:
                    st.metric(selected_name2[:25], f"{props2} propiedades")
                    st.metric("", f"{vehicles2} vehículos")
                    st.metric("", f"{accounts2} cuentas")
                    st.metric("", f"{debts2} deudas")
    
    with main_tab2:
        st.markdown("### 📊 Tabla de Datos Completa")
        
        # Simple search
        search = st.text_input("🔍 Buscar en la tabla:", placeholder="Nombre, circunscripción...")
        
        # Filter dataframe
        display_df = df.copy()
        if search:
            display_df = display_df[
                display_df['Nombre'].str.contains(search, case=False, na=False) |
                display_df['Circunscripción'].str.contains(search, case=False, na=False)
            ]
        
        # Remove deputy_index for display
        display_df = display_df.drop('deputy_index', axis=1)
        
        # Display
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Export option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name='declaraciones_bienes.csv',
            mime='text/csv'
        )

else:
    st.error("Error al cargar los datos. Verifique que existe el archivo 'all_deputies_merged.json'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(224, 224, 224, 0.4); padding: 20px 0;'>
    <p>🏛️ Datos públicos del Congreso de los Diputados</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
