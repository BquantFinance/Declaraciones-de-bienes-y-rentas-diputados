import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import re
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import json

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode CSS with glassmorphism and gradients (keeping your existing styles)
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
    
    /* Disclaimer with glassmorphism */
    .disclaimer-glass {
        background: rgba(255, 193, 7, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        color: #ffc107;
        box-shadow: 0 8px 32px 0 rgba(255, 193, 7, 0.1);
    }
    
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
    
    /* Property card */
    .property-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .property-card:hover {
        background: rgba(255, 255, 255, 0.05);
        transform: translateX(5px);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Metric cards */
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Individual card */
    .individual-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 25px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    /* Deputy photo */
    .deputy-photo {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        max-width: 200px;
        width: 100%;
        height: auto;
    }
    
    /* Data tables */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Tabs */
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
    }
    
    /* Buttons */
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
</style>
""", unsafe_allow_html=True)

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Helper function to parse monetary values from string
def parse_money_value(value):
    """Convert string money values to float"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    # Remove currency symbols and thousands separators
    value_str = str(value).replace('€', '').replace('.', '').replace(',', '.')
    value_str = value_str.strip()
    try:
        return float(value_str)
    except:
        return 0

# Helper function to get deputy photo
def get_deputy_photo(deputy_index):
    """Get the photo path for a deputy based on their index"""
    # Try different possible paths
    photo_paths = [
        f"deputy_photos/deputy_{deputy_index:04d}.jpg",
        f"deputy_photos/deputy_{deputy_index:04d}.gif",
        f"fotos_diputados/deputy_{deputy_index:04d}.jpg",
        f"fotos_diputados/deputy_{deputy_index:04d}.gif",
    ]
    
    for path in photo_paths:
        if os.path.exists(path):
            return path
    return None

# Load data function
@st.cache_data
def load_json_data():
    try:
        # Load the JSON file
        with open('all_deputies_merged.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Process JSON data into a DataFrame
        processed_data = []
        
        for idx, entry in enumerate(json_data, 1):
            if 'data' in entry and entry['data']:
                data = entry['data']
                
                # Extract personal information
                personal_info = data.get('informacion_personal', {})
                
                # Calculate total income
                total_income = 0
                rentas = data.get('rentas_percibidas', {})
                
                # Sum all salary perceptions
                for salary in rentas.get('percepciones_salariales', []):
                    total_income += parse_money_value(salary.get('euros', 0))
                
                # Add dividends
                for dividend in rentas.get('dividendos_y_participaciones', []):
                    total_income += parse_money_value(dividend.get('euros', 0))
                
                # Add interests
                for interest in rentas.get('intereses_financieros', []):
                    total_income += parse_money_value(interest.get('euros', 0))
                
                # Add other income
                for other in rentas.get('otras_rentas', []):
                    total_income += parse_money_value(other.get('euros', 0))
                
                # Calculate liquid assets
                liquid_assets = 0
                accounts = data.get('depositos_y_cuentas', {}).get('cuentas', [])
                for account in accounts:
                    liquid_assets += parse_money_value(account.get('saldo', 0))
                
                # Calculate total debt
                total_debt = 0
                debts = data.get('deudas_y_obligaciones', [])
                for debt in debts:
                    total_debt += parse_money_value(debt.get('saldo_pendiente', 0))
                
                # Net position
                net_position = liquid_assets - total_debt
                
                # Count properties
                urban_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', []))
                rustic_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                total_properties = urban_properties + rustic_properties
                
                # Count vehicles
                vehicles_count = len(data.get('vehiculos', []))
                
                processed_data.append({
                    'deputy_index': idx,
                    'name_surname': personal_info.get('nombre_y_apellidos', '').upper(),
                    'position': personal_info.get('cargo', 'Diputado'),
                    'constituency': personal_info.get('circunscripcion', ''),
                    'civil_status': personal_info.get('estado_civil', ''),
                    'economic_regime': personal_info.get('regimen_economico_matrimonial', ''),
                    'total_income_declared': total_income,
                    'total_liquid_assets': liquid_assets,
                    'total_debt': total_debt,
                    'net_position': net_position,
                    'irpf_paid': parse_money_value(data.get('irpf', {}).get('cantidad_pagada', 0)),
                    'total_properties': total_properties,
                    'urban_properties': urban_properties,
                    'rustic_properties': rustic_properties,
                    'vehicles_count': vehicles_count,
                    'source_file': entry.get('source_file', ''),
                    'legislatura': 'XV'  # Assuming all are from XV legislature
                })
        
        df = pd.DataFrame(processed_data)
        
        # Clean and standardize data
        string_cols = ['name_surname', 'position', 'constituency', 'civil_status', 'economic_regime']
        for col in string_cols:
            df[col] = df[col].fillna('').str.strip()
        
        return df
        
    except FileNotFoundError:
        st.error("No se encuentra el archivo 'all_deputies_merged.json'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al procesar el archivo JSON: {str(e)}")
        return pd.DataFrame()

# Show disclaimer if not accepted
if not st.session_state.disclaimer_accepted:
    # Hero Section for Disclaimer
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
        <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Large disclaimer box
    st.markdown("""
    <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(10px); border: 2px solid rgba(255, 193, 7, 0.4); border-radius: 25px; padding: 40px; margin: 30px 0;">
        <h2 style="color: #ffc107; text-align: center; margin-bottom: 30px;">⚠️ Descargo de Responsabilidad Legal</h2>
        <div style="line-height: 1.8; font-size: 1.05rem; color: white;">
            <p style="text-align: justify; margin-bottom: 20px;">
                <strong>Esta aplicación constituye una herramienta independiente de análisis y visualización de información pública</strong> 
                disponible en el portal oficial del Congreso de los Diputados. No mantiene vinculación institucional alguna con el 
                Congreso de los Diputados, sus órganos de gobierno, ni cuenta con aval, autorización o respaldo oficial de dicha institución.
            </p>
            <p style="text-align: justify; margin-bottom: 20px;">
                Los datos presentados provienen de fuentes públicas oficiales y, si bien se ha procurado garantizar su exactitud mediante 
                procesos automatizados de extracción y estructuración, <strong>la aplicación podría contener errores, inexactitudes, 
                omisiones o información desactualizada</strong> derivados del procesamiento de los documentos originales. 
                Para consultas oficiales y verificación de la información, se recomienda acudir directamente a los documentos 
                originales publicados en el portal web del Congreso de los Diputados.
            </p>
            <p style="text-align: justify; margin-bottom: 30px;">
                El uso de esta herramienta es responsabilidad exclusiva del usuario, quien deberá ejercer su propio criterio 
                en la interpretación y utilización de los datos aquí presentados.
            </p>
            <div style="background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; margin-top: 30px;">
                <p style="text-align: center; margin: 0; font-weight: 600;">
                    Al hacer clic en "Aceptar y Continuar", usted reconoce haber leído y comprendido este descargo de responsabilidad, 
                    y acepta que el uso de esta aplicación es bajo su propio riesgo y responsabilidad.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration requirements
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15)); backdrop-filter: blur(10px); border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 20px; padding: 25px; margin: 20px 0; color: white;">
        <h4 style="color: #667eea; margin-top: 0; text-align: center;">⚙️ Requisitos de Visualización</h4>
        <p style="text-align: center;">
            Esta aplicación requiere: <strong>Resolución de PC (mínimo 1920x1080)</strong> y <strong>Modo Oscuro del Navegador</strong> 
            para una experiencia óptima.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Accept button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Aceptar y Continuar", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0; margin-top: 50px;'>
        <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stop execution here if disclaimer not accepted
    st.stop()

# Main app continues here if disclaimer is accepted

# Hero Section
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
data_loaded = not df.empty

if data_loaded:
    # Main navigation
    st.markdown("---")
    mode = st.radio(
        "**Seleccione el modo de visualización:**",
        ["📊 Resumen Ejecutivo", "🔍 Análisis Individual", "📈 Estadísticas Agregadas", "🏠 Análisis Patrimonial"],
        horizontal=True
    )
    
    if mode == "📊 Resumen Ejecutivo":
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_parliamentarians = len(df['name_surname'].unique())
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Parlamentarios</div>
                <div class="metric-value">{total_parliamentarians}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_income = df['total_income_declared'].mean()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ingreso Medio</div>
                <div class="metric-value">€{avg_income:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            median_assets = df['total_liquid_assets'].median()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Mediana Activos</div>
                <div class="metric-value">€{median_assets:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            max_income = df['total_income_declared'].max()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Máximo Declarado</div>
                <div class="metric-value">€{max_income:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Top earners table
        st.markdown("### 💎 Ranking de Mayores Declaraciones Patrimoniales")
        top_earners = df.nlargest(15, 'total_income_declared')[
            ['name_surname', 'position', 'constituency', 'total_income_declared', 'total_liquid_assets', 'net_position']
        ].copy()
        top_earners['total_income_declared'] = top_earners['total_income_declared'].apply(lambda x: f'€{x:,.0f}')
        top_earners['total_liquid_assets'] = top_earners['total_liquid_assets'].apply(lambda x: f'€{x:,.0f}')
        top_earners['net_position'] = top_earners['net_position'].apply(lambda x: f'€{x:,.0f}')
        top_earners.columns = ['Nombre', 'Cargo', 'Circunscripción', 'Ingresos', 'Activos Líquidos', 'Posición Neta']
        st.dataframe(top_earners, use_container_width=True, hide_index=True)
    
    elif mode == "🔍 Análisis Individual":
        st.markdown("### 🔍 Consulta Individual de Parlamentarios")
        
        # Search box
        search_term = st.text_input("🔎 Búsqueda por nombre:", placeholder="Introduzca el nombre...")
        
        if search_term:
            filtered_names = df[df['name_surname'].str.contains(search_term, case=False, na=False)]['name_surname'].unique()
            if len(filtered_names) > 0:
                selected_name = st.selectbox("Seleccione parlamentario:", filtered_names)
            else:
                st.warning("No se encontraron resultados.")
                selected_name = None
        else:
            names = sorted(df['name_surname'].unique())
            selected_name = st.selectbox("Seleccione parlamentario:", names)
        
        if selected_name:
            person_data = df[df['name_surname'] == selected_name].iloc[0]
            
            # Display individual information with photo
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Try to load and display the photo
                photo_path = get_deputy_photo(person_data['deputy_index'])
                if photo_path:
                    st.image(photo_path, caption=person_data['name_surname'], use_column_width=True)
                else:
                    st.info("📷 Foto no disponible")
            
            with col2:
                st.markdown(f"""
                <div class="individual-card">
                    <h2 style="color: white;">{person_data['name_surname']}</h2>
                    <p style="color: rgba(255,255,255,0.8);">📍 {person_data['constituency']} | 🏛️ {person_data['position']}</p>
                    <p style="color: rgba(255,255,255,0.7);">👤 {person_data['civil_status']} | 📋 {person_data['economic_regime']}</p>
                    <p style="color: #ffc107; font-weight: bold; font-size: 1.2rem;">💰 Ingresos Declarados: €{person_data['total_income_declared']:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display detailed metrics
            st.markdown("#### 📊 Resumen Financiero")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Ingresos", f"€{person_data['total_income_declared']:,.0f}")
            with col2:
                st.metric("Activos Líquidos", f"€{person_data['total_liquid_assets']:,.0f}")
            with col3:
                st.metric("Deudas", f"€{person_data['total_debt']:,.0f}")
            with col4:
                st.metric("Posición Neta", f"€{person_data['net_position']:,.0f}")
            
            # Additional details
            st.markdown("#### 🏘️ Patrimonio")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("IRPF Pagado", f"€{person_data['irpf_paid']:,.0f}")
            with col2:
                st.metric("Propiedades", f"{int(person_data['total_properties'])}")
            with col3:
                st.metric("Vehículos", f"{int(person_data['vehicles_count'])}")
    
    elif mode == "📈 Estadísticas Agregadas":
        st.markdown("### 📈 Análisis Estadístico Agregado")
        
        # Group by constituency
        constituency_summary = df.groupby('constituency').agg({
            'total_income_declared': ['mean', 'median', 'count'],
            'total_liquid_assets': 'mean',
            'net_position': 'mean'
        }).round(0)
        
        constituency_summary.columns = ['Ingreso Medio', 'Ingreso Mediano', 'Cantidad', 'Activos Medios', 'Posición Neta Media']
        constituency_summary = constituency_summary.sort_values('Ingreso Medio', ascending=False)
        
        for col in ['Ingreso Medio', 'Ingreso Mediano', 'Activos Medios', 'Posición Neta Media']:
            constituency_summary[col] = constituency_summary[col].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(constituency_summary, use_container_width=True)
        
        # Distribution charts
        st.markdown("#### 📊 Distribución de Ingresos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x='total_income_declared', nbins=30, 
                              title='Distribución de Ingresos Declarados',
                              labels={'total_income_declared': 'Ingresos (€)', 'count': 'Frecuencia'})
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(df, y='total_income_declared', 
                        title='Box Plot de Ingresos',
                        labels={'total_income_declared': 'Ingresos (€)'})
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    
    elif mode == "🏠 Análisis Patrimonial":
        st.markdown("### 🏠 Análisis del Patrimonio Declarado")
        
        # Properties analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏘️ Distribución de Propiedades")
            properties_data = df[['name_surname', 'urban_properties', 'rustic_properties', 'total_properties']].copy()
            properties_data = properties_data[properties_data['total_properties'] > 0].nlargest(20, 'total_properties')
            
            fig = px.bar(properties_data, x='name_surname', y=['urban_properties', 'rustic_properties'],
                        title='Top 20 - Mayor Número de Propiedades',
                        labels={'value': 'Número de Propiedades', 'name_surname': 'Parlamentario'})
            fig.update_layout(template='plotly_dark', xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🚗 Análisis de Vehículos")
            vehicles_data = df[df['vehicles_count'] > 0].groupby('vehicles_count').size().reset_index(name='count')
            
            fig = px.pie(vehicles_data, values='count', names='vehicles_count',
                        title='Distribución por Número de Vehículos')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        
        # Debt analysis
        st.markdown("#### 💳 Análisis de Endeudamiento")
        debt_data = df[df['total_debt'] > 0].nlargest(15, 'total_debt')[['name_surname', 'total_debt', 'total_liquid_assets', 'net_position']]
        debt_data_display = debt_data.copy()
        debt_data_display['total_debt'] = debt_data_display['total_debt'].apply(lambda x: f'€{x:,.0f}')
        debt_data_display['total_liquid_assets'] = debt_data_display['total_liquid_assets'].apply(lambda x: f'€{x:,.0f}')
        debt_data_display['net_position'] = debt_data_display['net_position'].apply(lambda x: f'€{x:,.0f}')
        debt_data_display.columns = ['Nombre', 'Deuda Total', 'Activos Líquidos', 'Posición Neta']
        
        st.dataframe(debt_data_display, use_container_width=True, hide_index=True)
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar datos completos (CSV)",
            data=csv,
            file_name='declaraciones_bienes_rentas_xv_legislatura.csv',
            mime='text/csv'
        )

else:
    st.error("""
    ⚠️ **Error en la carga de datos**
    
    No se ha podido acceder al archivo de datos necesario para el funcionamiento de la aplicación.
    
    Por favor, verifique que el archivo 'all_deputies_merged.json' se encuentra en el directorio correspondiente.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'>
    <p>🏛️ Declaraciones de Bienes y Rentas - Datos públicos del Congreso de los Diputados</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
