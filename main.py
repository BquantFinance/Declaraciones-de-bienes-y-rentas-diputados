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

# Spectacular dark mode CSS with glassmorphism and gradients
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Dark mode base */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 40px;
        border-radius: 30px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }
    
    /* Deputy card styles */
    .deputy-main-card {
        background: linear-gradient(135deg, rgba(30, 30, 45, 0.9), rgba(20, 20, 35, 0.95));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    
    .deputy-header {
        display: flex;
        gap: 30px;
        align-items: start;
        margin-bottom: 25px;
    }
    
    .photo-section {
        flex-shrink: 0;
        position: relative;
    }
    
    .info-section {
        flex-grow: 1;
    }
    
    .deputy-name {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #E0E7FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 15px 0;
        line-height: 1.1;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .info-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(102, 126, 234, 0.08);
        border-radius: 8px;
        border-left: 2px solid rgba(102, 126, 234, 0.4);
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
    }
    
    .seat-section {
        flex-shrink: 0;
        text-align: center;
    }
    
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 15px 0;
    }
    
    .metric-card {
        background: rgba(102, 126, 234, 0.08);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    
    .metric-value {
        color: #667eea;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .patrimony-card {
        background: rgba(255, 193, 7, 0.08);
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .patrimony-value {
        color: #ffa500;
    }
    
    /* Comparison card */
    .comparison-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .comparison-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Data tables with glassmorphism */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Tabs with animations */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        color: white;
    }
    
    /* Buttons with gradient */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Comparison header */
    .vs-header {
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 20px 0;
    }
    
    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for disclaimer
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
    """Get the actual deputy photo from deputy_photos folder"""
    # Changed path to deputy_photos folder
    photo_path = f"deputy_photos/deputy_{deputy_index:03d}.jpg"
    if os.path.exists(photo_path):
        return photo_path
    return None

def get_party_logo(deputy_index):
    """Get the party logo from deputy_photos folder - same naming as photos"""
    # Party logos have the same naming convention as photos
    # They appear to be in the same folder
    logo_path = f"deputy_photos/logo_{deputy_index:03d}.png"
    # Also check for jpg version
    if not os.path.exists(logo_path):
        logo_path = f"deputy_photos/logo_{deputy_index:03d}.jpg"
    if os.path.exists(logo_path):
        return logo_path
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
                
                # Calculate totals
                total_income = 0
                rentas = data.get('rentas_percibidas', {})
                
                for salary in rentas.get('percepciones_salariales', []):
                    total_income += parse_money_value(salary.get('euros', 0))
                for dividend in rentas.get('dividendos_y_participaciones', []):
                    total_income += parse_money_value(dividend.get('euros', 0))
                for interest in rentas.get('intereses_financieros', []):
                    total_income += parse_money_value(interest.get('euros', 0))
                for other in rentas.get('otras_rentas', []):
                    total_income += parse_money_value(other.get('euros', 0))
                
                # Liquid assets
                liquid_assets = 0
                accounts = data.get('depositos_y_cuentas', {}).get('cuentas', [])
                for account in accounts:
                    liquid_assets += parse_money_value(account.get('saldo', 0))
                
                # Debt
                total_debt = 0
                debts = data.get('deudas_y_obligaciones', [])
                for debt in debts:
                    total_debt += parse_money_value(debt.get('saldo_pendiente', 0))
                
                # Properties
                urban_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', []))
                rustic_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                vehicles_count = len(data.get('vehiculos', []))
                
                processed_data.append({
                    'deputy_index': idx,
                    'Nombre': personal_info.get('nombre_y_apellidos', '').upper(),
                    'Cargo': personal_info.get('cargo', 'Diputado'),
                    'Circunscripción': personal_info.get('circunscripcion', ''),
                    'Estado Civil': personal_info.get('estado_civil', ''),
                    'Régimen Económico': personal_info.get('regimen_economico_matrimonial', ''),
                    'Ingresos Declarados': total_income,
                    'Activos Líquidos': liquid_assets,
                    'Deudas': total_debt,
                    'Posición Neta': liquid_assets - total_debt,
                    'IRPF Pagado': parse_money_value(data.get('irpf', {}).get('cantidad_pagada', 0)),
                    'Propiedades Urbanas': urban_properties,
                    'Propiedades Rústicas': rustic_properties,
                    'Total Propiedades': urban_properties + rustic_properties,
                    'Vehículos': vehicles_count,
                })
        
        return pd.DataFrame(processed_data)
        
    except FileNotFoundError:
        st.error("No se encuentra el archivo 'all_deputies_merged.json'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        return pd.DataFrame()

# Show disclaimer if not accepted
if not st.session_state.disclaimer_accepted:
    # Hero Section HTML
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
        <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main disclaimer container
    with st.container():
        st.markdown("## ⚠️ **Descargo de Responsabilidad Legal**")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([0.5, 10, 0.5])
        
        with col2:
            with st.container():
                st.markdown("### 📋 Naturaleza de la Aplicación")
                st.info("""
                **Esta aplicación constituye una herramienta independiente de análisis y visualización de información pública** 
                disponible en el portal oficial del Congreso de los Diputados. No mantiene vinculación institucional alguna con el 
                Congreso de los Diputados, sus órganos de gobierno, ni cuenta con aval, autorización o respaldo oficial de dicha institución.
                """)
            
            with st.container():
                st.markdown("### 📊 Origen y Precisión de los Datos")
                st.warning("""
                Los datos presentados provienen de fuentes públicas oficiales y, si bien se ha procurado garantizar su exactitud mediante 
                procesos automatizados de extracción y estructuración, **la aplicación podría contener errores, inexactitudes, 
                omisiones o información desactualizada** derivados del procesamiento de los documentos originales. 
                Para consultas oficiales y verificación de la información, se recomienda acudir directamente a los documentos 
                originales publicados en el portal web del Congreso de los Diputados.
                """)
            
            with st.container():
                st.markdown("### ⚖️ Responsabilidad del Usuario")
                st.write("""
                El uso de esta herramienta es responsabilidad exclusiva del usuario, quien deberá ejercer su propio criterio 
                en la interpretación y utilización de los datos aquí presentados.
                """)
            
            st.markdown("---")
            
            with st.container():
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                            border-radius: 20px; padding: 25px; margin: 20px 0; 
                            border: 2px solid rgba(102, 126, 234, 0.3);">
                    <p style="text-align: center; color: white; font-size: 1.1rem; margin: 0;">
                        ✅ Al hacer clic en <strong>"Aceptar y Continuar"</strong>, usted reconoce haber leído y comprendido este descargo de responsabilidad, 
                        y acepta que el uso de esta aplicación es bajo su propio riesgo y responsabilidad.
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ **Aceptar y Continuar**", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;'>
            Desarrollado con 💜 por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none; font-weight: 600;'>@Gsnchez</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# Main App - Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
    <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    <a href="https://twitter.com/Gsnchez" target="_blank" style="display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; color: white; font-weight: 600; text-decoration: none; transition: all 0.3s ease; position: relative; z-index: 1;">
        Desarrollado por @Gsnchez ✨
    </a>
</div>
""", unsafe_allow_html=True)

# Project motivation
st.markdown("""
<div style="background: rgba(102, 126, 234, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 20px; padding: 30px; margin: 20px 0; color: white;">
    <h3 style="color: #667eea; margin-top: 0; text-align: center;">📚 Motivación del Proyecto</h3>
    <p style="line-height: 1.8; text-align: justify;">
        Este proyecto surge con el propósito fundamental de <strong>democratizar el acceso a la información pública</strong> 
        relativa a las declaraciones de bienes y rentas de los parlamentarios españoles.
    </p>
    <ul style="line-height: 1.8;">
        <li><strong>Transparencia:</strong> Facilitar el escrutinio público de la información patrimonial de los representantes electos.</li>
        <li><strong>Accesibilidad:</strong> Eliminar las barreras técnicas que dificultan el acceso a estos datos.</li>
        <li><strong>Estructuración:</strong> Organizar sistemáticamente la información dispersa en múltiples documentos PDF.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Load data
df = load_json_data()

if not df.empty:
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos Completa"])
    
    with tab1:
        st.markdown("### 🔍 Análisis Individual de Parlamentarios")
        
        # Comparison mode toggle
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            comparison_mode = st.checkbox("📊 Modo Comparación", value=st.session_state.comparison_mode)
            st.session_state.comparison_mode = comparison_mode
        
        if not comparison_mode:
            # Single deputy analysis
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
                    person_data = df[df['Nombre'] == selected_name].iloc[0]
                    
                    # Create a beautiful, compact card layout
                    col_main = st.container()
                    with col_main:
                        # Get paths for photo and logo
                        photo_path = get_deputy_photo(person_data['deputy_index'])
                        logo_path = get_party_logo(person_data['deputy_index'])
                        
                        # Prepare photo HTML with party logo overlay
                        if photo_path and os.path.exists(photo_path):
                            with open(photo_path, "rb") as image_file:
                                encoded_photo = base64.b64encode(image_file.read()).decode()
                            
                            # Check for party logo
                            logo_html = ""
                            if logo_path and os.path.exists(logo_path):
                                with open(logo_path, "rb") as logo_file:
                                    encoded_logo = base64.b64encode(logo_file.read()).decode()
                                logo_html = f"""
                                <div style="
                                    position: absolute;
                                    bottom: -8px;
                                    right: -8px;
                                    background: white;
                                    border-radius: 50%;
                                    padding: 4px;
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                                    width: 40px;
                                    height: 40px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                                    <img src="data:image/png;base64,{encoded_logo}" 
                                         style="width: 32px; height: 32px; object-fit: contain;">
                                </div>
                                """
                            
                            photo_html = f"""
                            <div style="position: relative; display: inline-block;">
                                <div style="
                                    width: 120px;
                                    height: 160px;
                                    border-radius: 12px;
                                    overflow: hidden;
                                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
                                    border: 2px solid rgba(102, 126, 234, 0.3);
                                ">
                                    <img src="data:image/jpeg;base64,{encoded_photo}" 
                                         style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                {logo_html}
                            </div>
                            """
                        else:
                            photo_html = """
                            <div style="
                                width: 120px;
                                height: 160px;
                                border-radius: 12px;
                                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                border: 2px solid rgba(102, 126, 234, 0.2);
                            ">
                                <div style="text-align: center;">
                                    <div style="font-size: 3rem; opacity: 0.3;">👤</div>
                                    <div style="font-size: 0.7rem; opacity: 0.5;">Sin foto</div>
                                </div>
                            </div>
                            """
                        
                        # Get hemiciclo seat
                        seat_html = ""
                        seat_path = get_hemiciclo_seat(person_data['deputy_index'])
                        if seat_path and os.path.exists(seat_path):
                            with open(seat_path, "rb") as image_file:
                                encoded_seat = base64.b64encode(image_file.read()).decode()
                            seat_html = f"""
                            <div class="seat-section">
                                <div style="
                                    background: rgba(102, 126, 234, 0.1);
                                    padding: 10px;
                                    border-radius: 12px;
                                    border: 1px solid rgba(102, 126, 234, 0.2);
                                ">
                                    <img src="data:image/gif;base64,{encoded_seat}" 
                                         style="width: 140px; border-radius: 8px;">
                                    <div style="font-size: 0.65rem; color: rgba(255,255,255,0.5); margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;">
                                        Escaño Hemiciclo
                                    </div>
                                </div>
                            </div>
                            """
                        
                        # Build the complete card HTML
                        st.markdown(f"""
                        <div class="deputy-main-card">
                            <div class="deputy-header">
                                <div class="photo-section">
                                    {photo_html}
                                </div>
                                
                                <div class="info-section">
                                    <h2 class="deputy-name">{person_data['Nombre']}</h2>
                                    
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <span>📍</span>
                                            <span>{person_data['Circunscripción']}</span>
                                        </div>
                                        <div class="info-item">
                                            <span>🏛️</span>
                                            <span>{person_data['Cargo']}</span>
                                        </div>
                                        <div class="info-item">
                                            <span>💑</span>
                                            <span>{person_data['Estado Civil']}</span>
                                        </div>
                                        <div class="info-item">
                                            <span>📜</span>
                                            <span>{person_data.get('Régimen Económico', 'No especificado')}</span>
                                        </div>
                                    </div>
                                </div>
                                
                                {seat_html}
                            </div>
                            
                            <!-- Financial Section -->
                            <div style="border-top: 1px solid rgba(102, 126, 234, 0.2); padding-top: 15px; margin-top: 20px;">
                                <h4 style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0 0 12px 0;">💰 Información Financiera</h4>
                                <div class="metrics-row">
                                    <div class="metric-card">
                                        <div class="metric-label">Ingresos</div>
                                        <div class="metric-value">€{person_data['Ingresos Declarados']:,.0f}</div>
                                    </div>
                                    <div class="metric-card">
                                        <div class="metric-label">Activos</div>
                                        <div class="metric-value">€{person_data['Activos Líquidos']:,.0f}</div>
                                    </div>
                                    <div class="metric-card">
                                        <div class="metric-label">Deudas</div>
                                        <div class="metric-value">€{person_data['Deudas']:,.0f}</div>
                                    </div>
                                    <div class="metric-card">
                                        <div class="metric-label">Posición Neta</div>
                                        <div class="metric-value" style="color: {'#4CAF50' if person_data['Posición Neta'] >= 0 else '#f44336'}">
                                            €{person_data['Posición Neta']:,.0f}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Patrimony Section -->
                            <div style="border-top: 1px solid rgba(255, 193, 7, 0.2); padding-top: 15px; margin-top: 15px;">
                                <h4 style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0 0 12px 0;">🏠 Patrimonio</h4>
                                <div class="metrics-row">
                                    <div class="metric-card patrimony-card">
                                        <div class="metric-label">IRPF Pagado</div>
                                        <div class="metric-value patrimony-value">€{person_data['IRPF Pagado']:,.0f}</div>
                                    </div>
                                    <div class="metric-card patrimony-card">
                                        <div class="metric-label">Prop. Urbanas</div>
                                        <div class="metric-value patrimony-value">{int(person_data['Propiedades Urbanas'])}</div>
                                    </div>
                                    <div class="metric-card patrimony-card">
                                        <div class="metric-label">Prop. Rústicas</div>
                                        <div class="metric-value patrimony-value">{int(person_data['Propiedades Rústicas'])}</div>
                                    </div>
                                    <div class="metric-card patrimony-card">
                                        <div class="metric-label">Vehículos</div>
                                        <div class="metric-value patrimony-value">{int(person_data['Vehículos'])}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
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
                person1 = df[df['Nombre'] == selected_name1].iloc[0]
                person2 = df[df['Nombre'] == selected_name2].iloc[0]
                
                st.markdown('<h2 class="vs-header">VS</h2>', unsafe_allow_html=True)
                
                # Comparison metrics
                metrics = [
                    ('Ingresos Declarados', '€'),
                    ('Activos Líquidos', '€'),
                    ('Deudas', '€'),
                    ('Posición Neta', '€'),
                    ('IRPF Pagado', '€'),
                    ('Total Propiedades', ''),
                    ('Vehículos', '')
                ]
                
                for metric, prefix in metrics:
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        value1 = person1[metric]
                        if prefix == '€':
                            st.metric(selected_name1[:20], f"{prefix}{value1:,.0f}")
                        else:
                            st.metric(selected_name1[:20], f"{int(value1)}")
                    
                    with col2:
                        st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.5); margin-top: 20px;'>{metric}</p>", unsafe_allow_html=True)
                    
                    with col3:
                        value2 = person2[metric]
                        if prefix == '€':
                            st.metric(selected_name2[:20], f"{prefix}{value2:,.0f}")
                        else:
                            st.metric(selected_name2[:20], f"{int(value2)}")
    
    with tab2:
        st.markdown("### 📊 Tabla de Datos Completa con Filtros")
        
        # Advanced filters in expandable section
        with st.expander("🔧 Filtros Avanzados", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                min_income = st.number_input("Ingresos mínimos (€):", min_value=0, value=0, step=10000)
                max_income = st.number_input("Ingresos máximos (€):", min_value=0, value=10000000, step=10000)
            
            with col2:
                min_assets = st.number_input("Activos mínimos (€):", min_value=0, value=0, step=10000)
                max_debt = st.number_input("Deuda máxima (€):", min_value=0, value=10000000, step=10000)
            
            with col3:
                unique_constituencies = df['Circunscripción'].dropna().unique().tolist()
                constituencies = ['Todas'] + sorted([c for c in unique_constituencies if c])
                selected_constituency = st.selectbox("Circunscripción:", constituencies)
                
                min_properties = st.number_input("Mínimo propiedades:", min_value=0, value=0, step=1)
            
            with col4:
                sort_by = st.selectbox("Ordenar por:", 
                    ['Ingresos Declarados', 'Activos Líquidos', 'Posición Neta', 'Deudas', 'IRPF Pagado'])
                sort_order = st.radio("Orden:", ['Descendente', 'Ascendente'])
        
        # Apply filters
        filtered_df = df.copy()
        
        if min_income > 0:
            filtered_df = filtered_df[filtered_df['Ingresos Declarados'] >= min_income]
        if max_income < 10000000:
            filtered_df = filtered_df[filtered_df['Ingresos Declarados'] <= max_income]
        if min_assets > 0:
            filtered_df = filtered_df[filtered_df['Activos Líquidos'] >= min_assets]
        if max_debt < 10000000:
            filtered_df = filtered_df[filtered_df['Deudas'] <= max_debt]
        if selected_constituency != 'Todas':
            filtered_df = filtered_df[filtered_df['Circunscripción'] == selected_constituency]
        if min_properties > 0:
            filtered_df = filtered_df[filtered_df['Total Propiedades'] >= min_properties]
        
        # Sort
        filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_order == 'Ascendente'))
        
        # Show results
        st.markdown(f"""
        <div class="info-card">
            📊 Mostrando <strong>{len(filtered_df)}</strong> de <strong>{len(df)}</strong> parlamentarios
        </div>
        """, unsafe_allow_html=True)
        
        # Format for display
        display_df = filtered_df.copy()
        money_cols = ['Ingresos Declarados', 'Activos Líquidos', 'Deudas', 'Posición Neta', 'IRPF Pagado']
        for col in money_cols:
            display_df[col] = display_df[col].apply(lambda x: f'€{x:,.0f}')
        
        # Remove deputy_index column for display
        columns_to_display = [col for col in display_df.columns if col != 'deputy_index']
        display_df = display_df[columns_to_display]
        
        # Display with style
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar datos filtrados (CSV)",
                data=csv,
                file_name='declaraciones_filtradas.csv',
                mime='text/csv'
            )
        
        with col2:
            # Summary statistics
            if len(filtered_df) > 0:
                avg_income = filtered_df['Ingresos Declarados'].mean()
                total_assets = filtered_df['Activos Líquidos'].sum()
                st.markdown(f"""
                <div class="info-card">
                    📈 <strong>Resumen:</strong> Ingreso medio: €{avg_income:,.0f} | Total activos: €{total_assets:,.0f}
                </div>
                """, unsafe_allow_html=True)

else:
    st.error("Error al cargar los datos. Verifique que existe el archivo 'all_deputies_merged.json'")

# Footer with style
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'>
    <p>🏛️ Datos públicos del Congreso de los Diputados</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
