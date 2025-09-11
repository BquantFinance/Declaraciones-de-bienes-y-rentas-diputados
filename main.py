import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64

# Page configuration
st.set_page_config(
    page_title="Registro de Diputados - Congreso de España",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Production CSS with all enhancements
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main App Styling */
        .stApp {
            background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main .block-container {
            padding-top: 1rem;
            max-width: 1600px;
        }
        
        /* Image Gallery Container */
        .image-gallery {
            display: flex;
            gap: 2rem;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        @media (max-width: 768px) {
            .image-gallery {
                flex-direction: column;
            }
        }
        
        /* Deputy Photo Effects */
        .deputy-photo-container {
            position: relative;
            overflow: hidden;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            perspective: 1000px;
            cursor: zoom-in;
        }
        
        .deputy-photo-container:hover {
            transform: translateY(-10px) scale(1.05) rotateY(5deg);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5);
        }
        
        .deputy-photo-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, 
                transparent 0%, 
                transparent 50%, 
                rgba(102, 126, 234, 0.3) 100%);
            opacity: 0;
            transition: opacity 0.4s ease;
            pointer-events: none;
            z-index: 1;
        }
        
        .deputy-photo-container:hover::before {
            opacity: 1;
        }
        
        .deputy-photo-container::after {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, 
                #667eea, #764ba2, #f093fb, #c471f5, 
                #667eea, #764ba2, #f093fb, #c471f5);
            background-size: 400% 400%;
            border-radius: 15px;
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s ease;
            animation: gradientShift 3s ease infinite;
        }
        
        .deputy-photo-container:hover::after {
            opacity: 1;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .deputy-photo {
            width: 200px;
            height: 250px;
            object-fit: cover;
            display: block;
            transition: transform 0.4s ease;
            animation: imageLoad 0.6s ease-out;
        }
        
        .deputy-photo-container:hover .deputy-photo {
            transform: scale(1.1);
        }
        
        /* No Photo Placeholder */
        .no-photo-placeholder {
            width: 200px;
            height: 250px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.1));
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            border-radius: 15px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            font-size: 3rem;
            transition: all 0.3s ease;
            cursor: default;
        }
        
        .no-photo-placeholder:hover {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.2));
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        /* Badges Container */
        .badges-container {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            align-items: center;
        }
        
        /* Logo and Hemiciclo Badge Effects */
        .badge-item {
            position: relative;
            overflow: hidden;
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .badge-item:hover {
            transform: rotate(-5deg) scale(1.1);
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .badge-item img {
            width: 100px;
            height: 100px;
            object-fit: contain;
            transition: transform 0.3s ease;
            animation: imageLoad 0.6s ease-out;
        }
        
        .badge-item:hover img {
            transform: scale(1.1);
        }
        
        .badge-item::before {
            content: attr(title);
            position: absolute;
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.75rem;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            z-index: 10;
        }
        
        .badge-item:hover::before {
            opacity: 1;
        }
        
        /* Party Logo Animation */
        .party-logo {
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .badge-item:hover .party-logo {
            animation: none;
            transform: scale(1.15);
        }
        
        /* Hemiciclo Special Effect */
        .hemiciclo-badge {
            position: relative;
        }
        
        .hemiciclo-badge::after {
            content: '🏛️';
            position: absolute;
            top: -10px;
            right: -10px;
            font-size: 1.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.8; }
        }
        
        @keyframes imageLoad {
            from {
                opacity: 0;
                transform: scale(0.8) rotate(-5deg);
            }
            to {
                opacity: 1;
                transform: scale(1) rotate(0deg);
            }
        }
        
        /* Responsive Design */
        @media (max-width: 1024px) {
            .deputy-photo {
                width: 180px;
                height: 230px;
            }
            .no-photo-placeholder {
                width: 180px;
                height: 230px;
            }
        }
        
        @media (max-width: 640px) {
            .deputy-photo {
                width: 160px;
                height: 200px;
            }
            .no-photo-placeholder {
                width: 160px;
                height: 200px;
                font-size: 2.5rem;
            }
            .badge-item img {
                width: 80px;
                height: 80px;
            }
        }
        
        /* Mobile Touch Feedback */
        @media (hover: none) {
            .deputy-photo-container:active {
                transform: scale(0.95);
            }
            .badge-item:active {
                transform: scale(0.9);
            }
        }
        
        /* Disclaimer Container */
        .disclaimer-container {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 3rem;
            margin: 2rem auto;
            max-width: 900px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .disclaimer-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 2rem;
        }

        .disclaimer-section-title {
            color: #f59e0b;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            padding-left: 2.5rem;
            position: relative;
            font-size: 1.2rem;
        }

        .disclaimer-section-title::before {
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5rem;
        }
        
        .disclaimer-section-title.nature::before { content: '📋'; }
        .disclaimer-section-title.disclaimer::before { content: '⚠️'; }
        .disclaimer-section-title.liability::before { content: '📌'; }
        .disclaimer-section-title.source::before { content: '✅'; }
        .disclaimer-section-title.privacy::before { content: '👤'; }
        .disclaimer-section-title.acceptance::before { content: '⚖️'; }
        
        .disclaimer-text {
            color: #e2e8f0;
            font-size: 1.1rem;
            line-height: 1.8;
            text-align: justify;
            margin-bottom: 1.5rem;
        }
        
        .disclaimer-text strong {
            color: #fbbf24;
            font-weight: 600;
        }
        
        .disclaimer-list {
            list-style: none;
            padding-left: 0;
            margin: 1.5rem 0;
        }
        
        .disclaimer-list li {
            color: #e2e8f0;
            margin: 1rem 0;
            padding-left: 2rem;
            position: relative;
        }
        
        .disclaimer-list li::before {
            content: '⚠️';
            position: absolute;
            left: 0;
            top: 0;
        }
        
        /* Typography */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
        }
        
        h3 {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
        }
        
        h4, h5 {
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }
        
        /* Info Grid */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.2rem;
            margin: 1.5rem 0;
        }
        
        .info-item {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.1) 0%, 
                rgba(118, 75, 162, 0.05) 100%);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
            transition: all 0.3s ease;
        }
        
        .info-item:hover {
            transform: translateY(-5px);
            border-color: rgba(102, 126, 234, 0.4);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        }
        
        .info-label {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            font-weight: 600;
            opacity: 0.8;
        }
        
        .info-value {
            font-size: 1.1rem;
            color: #ffffff;
            font-weight: 500;
        }
        
        /* Metrics */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 1.2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        div[data-testid="metric-container"] label {
            color: #94a3b8 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        
        div[data-testid="metric-container"] div[data-testid="metric-value"] {
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            padding: 0 20px;
            background: transparent;
            border: none;
            border-radius: 8px;
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff;
            background: rgba(102, 126, 234, 0.1);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.2) 0%, 
                rgba(118, 75, 162, 0.2) 100%);
            color: #ffffff !important;
            font-weight: 600;
        }
        
        /* Social Pills */
        .social-pills {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .social-pill {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            font-size: 1.5rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .social-pill:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: scale(1.2);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        /* Input Fields */
        .stSelectbox > div > div, 
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
            transition: all 0.3s ease !important;
        }
        
        .stSelectbox > div > div:hover, 
        .stTextInput > div > div > input:hover {
            border-color: rgba(102, 126, 234, 0.5) !important;
            background: rgba(255, 255, 255, 0.08) !important;
        }
        
        .stSelectbox > div > div:focus, 
        .stTextInput > div > div > input:focus {
            border-color: rgba(102, 126, 234, 0.7) !important;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Alert Messages */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .stSuccess {
            background: linear-gradient(135deg, 
                rgba(16, 185, 129, 0.1) 0%, 
                rgba(16, 185, 129, 0.05) 100%);
            border-left: 4px solid #10b981;
        }
        
        .stWarning {
            background: linear-gradient(135deg, 
                rgba(245, 158, 11, 0.1) 0%, 
                rgba(245, 158, 11, 0.05) 100%);
            border-left: 4px solid #f59e0b;
        }
        
        .stError {
            background: linear-gradient(135deg, 
                rgba(239, 68, 68, 0.1) 0%, 
                rgba(239, 68, 68, 0.05) 100%);
            border-left: 4px solid #ef4444;
        }
        
        .stInfo {
            background: linear-gradient(135deg, 
                rgba(59, 130, 246, 0.1) 0%, 
                rgba(59, 130, 246, 0.05) 100%);
            border-left: 4px solid #3b82f6;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.1) 0%, 
                rgba(118, 75, 162, 0.1) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        /* Accept button */
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            font-size: 1.2rem;
            padding: 1rem 3rem;
            font-weight: 600;
        }
        
        /* Text */
        strong {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.4) 0%, 
                rgba(118, 75, 162, 0.4) 100%);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.6) 0%, 
                rgba(118, 75, 162, 0.6) 100%);
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Responsive */
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .disclaimer-container {
                padding: 2rem;
                margin: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    try:
        df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
        path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
        for col in path_columns:
            if col in df.columns:
                df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'deputies_full_dataset.csv'. Por favor, asegúrate de que el archivo esté en el mismo directorio que la aplicación.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value in ('[]', ''):
        return []
    try:
        cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value))
        return json.loads(cleaned_value)
    except:
        return []

def format_currency(value):
    """Format currency values for display with Spanish notation"""
    if not isinstance(value, (int, float)):
        return "0€"
    
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted}€"
    else:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"

def format_currency_full(value):
    """Format currency values for detailed display"""
    if not isinstance(value, (int, float)):
        return "0,00 €"
    
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted} €"
    else:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} €"

def extract_currency_value(value_str):
    """Extract numeric value from currency string"""
    if pd.isna(value_str) or value_str == '':
        return 0
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    numeric_part = re.search(r'[\d.,]+', str(value_str))
    if numeric_part:
        try:
            cleaned_str = numeric_part.group(0).replace('.', '').replace(',', '.')
            return float(cleaned_str)
        except (ValueError, TypeError):
            return 0
    return 0

def create_image_gallery(deputy_data):
    """Create enhanced image gallery with effects"""
    gallery_html = '<div class="image-gallery">'
    
    # Main photo with effects
    gallery_html += '<div class="deputy-photo-container">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" class="deputy-photo" alt="Foto del diputado">'
    else:
        gallery_html = '<div class="image-gallery">'
        gallery_html += '<div class="no-photo-placeholder">👤<span style="font-size: 0.9rem; margin-top: 10px;">Sin Foto</span></div>'
    gallery_html += '</div>'
    
    # Badges container with animation effects
    gallery_html += '<div class="badges-container">'
    
    # Party logo with floating animation
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'''
            <div class="badge-item" title="Logo del Partido">
                <img src="data:image/png;base64,{img_data}" class="party-logo" alt="Logo del partido">
            </div>'''
    
    # Hemiciclo seat indicator with pulse effect
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'''
            <div class="badge-item hemiciclo-badge" title="Ubicación en el Hemiciclo">
                <img src="data:image/png;base64,{img_data}" alt="Posición en hemiciclo">
            </div>'''
    
    gallery_html += '</div></div>'
    return gallery_html

def show_disclaimer():
    """Show the comprehensive legal disclaimer page"""
    apply_css()
    
    # Center the disclaimer
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <div class="disclaimer-container">
            <h1 class="disclaimer-title">DESCARGO DE RESPONSABILIDAD LEGAL</h1>
            <div class="disclaimer-text">
                <p><strong>IMPORTANTE: LEA ATENTAMENTE ANTES DE USAR ESTA APLICACIÓN</strong></p>
                
                <p>Esta aplicación web de consulta de información pública ("la Aplicación") recopila, procesa y presenta datos obtenidos de fuentes públicas disponibles en la página web oficial del Congreso de los Diputados de España, incluyendo documentos en formato PDF y otros registros de acceso público.</p>
                
                <h3 class="disclaimer-section-title nature">NATURALEZA Y ORIGEN DE LA INFORMACIÓN</h3>
                <p>La información mostrada en esta Aplicación proviene exclusivamente de:</p>
                <ul class="disclaimer-list">
                    <li>Declaraciones de bienes y rentas publicadas en el Portal de Transparencia del Congreso de los Diputados</li>
                    <li>Registros públicos de actividades e intereses de los parlamentarios</li>
                    <li>Documentación oficial de acceso público disponible en www.congreso.es</li>
                </ul>
                
                <h3 class="disclaimer-section-title disclaimer">DESCARGO DE RESPONSABILIDAD</h3>
                <p><strong>La Aplicación no pertenece, no está vinculada, afiliada, patrocinada, avalada ni autorizada de ninguna manera por el Congreso de los Diputados</strong>, ni por ninguna institución gubernamental o entidad pública española. Es un proyecto independiente desarrollado con fines informativos y de acceso facilitado a información pública.</p>
                
                <p>El contenido mostrado se ofrece únicamente con fines informativos, educativos y de consulta pública. Aunque se realizan esfuerzos razonables para garantizar la precisión y actualización de los datos:</p>
                
                <ul class="disclaimer-list">
                    <li>La Aplicación puede contener <strong>errores, inexactitudes, omisiones o información desactualizada</strong></li>
                    <li>Los datos pueden no reflejar los cambios más recientes en las declaraciones</li>
                    <li>Pueden existir discrepancias entre la información mostrada y los documentos originales</li>
                    <li>La interpretación o procesamiento automatizado de los datos puede introducir errores involuntarios</li>
                </ul>
                
                <h3 class="disclaimer-section-title liability">LIMITACIÓN DE RESPONSABILIDAD</h3>
                <p>Los desarrolladores y operadores de esta Aplicación:</p>
                <ul class="disclaimer-list">
                    <li>No garantizan la exactitud, integridad, actualidad o idoneidad de la información para ningún propósito particular</li>
                    <li>No asumen responsabilidad por decisiones tomadas basándose en la información aquí presentada</li>
                    <li>No se responsabilizan de daños directos, indirectos, incidentales o consecuentes derivados del uso de la Aplicación</li>
                    <li>Se reservan el derecho de modificar, suspender o discontinuar el servicio sin previo aviso</li>
                </ul>
                
                <h3 class="disclaimer-section-title source">FUENTE OFICIAL</h3>
                <p><strong>Para la consulta oficial, íntegra, auténtica y legalmente válida de las declaraciones de bienes y rentas de los diputados, se debe acudir directamente a:</strong></p>
                <p style="text-align: center; font-size: 1.2rem; margin: 1.5rem 0;">
                    <strong>🔗 Portal de Transparencia del Congreso de los Diputados</strong><br>
                    <span style="color: #3b82f6;">www.congreso.es</span>
                </p>
                
                <h3 class="disclaimer-section-title privacy">PRIVACIDAD Y DATOS PERSONALES</h3>
                <p>Esta Aplicación muestra únicamente información que ya es de dominio público y ha sido publicada oficialmente por el Congreso de los Diputados en cumplimiento de las obligaciones de transparencia establecidas en la legislación española.</p>
                
                <h3 class="disclaimer-section-title acceptance">ACEPTACIÓN DE TÉRMINOS</h3>
                <p>Al hacer clic en "ACEPTO Y ENTIENDO" y utilizar esta Aplicación, usted reconoce que:</p>
                <ul class="disclaimer-list">
                    <li>Ha leído y comprendido este descargo de responsabilidad en su totalidad</li>
                    <li>Acepta usar la Aplicación bajo su propio riesgo</li>
                    <li>Comprende las limitaciones de la información presentada</li>
                    <li>Se compromete a verificar cualquier información crítica en las fuentes oficiales</li>
                </ul>
                
                <p style="margin-top: 2rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 10px; border-left: 4px solid #ef4444;">
                    <strong>⚠️ ADVERTENCIA FINAL:</strong> El uso de esta aplicación es responsabilidad exclusiva del usuario. Si no está de acuerdo con estos términos, por favor no utilice la Aplicación.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Centered Accept button and message
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()

            st.markdown(
                """
                <p style="
                    margin-top: 1rem; 
                    padding: 1rem; 
                    background: rgba(239, 68, 68, 0.1); 
                    border-radius: 10px; 
                    border-left: 4px solid #ef4444;
                    text-align: center;
                    color: #e2e8f0;
                ">
                    Para usar esta aplicación debe aceptar los términos y condiciones.
                </p>
                """,
                unsafe_allow_html=True
            )

def main_app():
    """Main application"""
    apply_css()
    
    st.markdown('<h1 style="text-align: center;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Get unique deputies by name
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Search bar
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input(
            "Buscar diputado",
            placeholder="🔍 Buscar diputado por nombre...",
            key="search",
            label_visibility="collapsed"
        )
    
    # Filter unique deputies
    filtered_deputies = unique_deputies.copy()
    if search_term:
        filtered_deputies = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
    
    with col2:
        st.metric("Diputados", len(filtered_deputies))
    
    st.markdown("---")
    
    if len(filtered_deputies) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
    else:
        # Deputy selector
        deputy_names = filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy_name = st.selectbox(
            "Seleccionar Diputado:",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        # Get all declarations for selected deputy
        deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
        
        # Declaration selector (if multiple)
        if len(deputy_declarations) > 1:
            st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
            
            # Create options for declarations
            declaration_options = []
            for idx, row in deputy_declarations.iterrows():
                fecha_eleccion = row.get('informacion_personal_fecha_eleccion', '')
                fecha_presentacion = row.get('informacion_personal_fecha_presentacion_credencial', '')
                
                declaration_number = idx - deputy_declarations.index[0] + 1
                label = f"📄 Declaración {declaration_number}"
                
                if fecha_eleccion and str(fecha_eleccion).lower() != 'nan':
                    label += f" - Elección: {fecha_eleccion}"
                if fecha_presentacion and str(fecha_presentacion).lower() != 'nan':
                    label += f" - Presentación: {fecha_presentacion}"
                    
                declaration_options.append((idx, label))
            
            selected_idx = st.selectbox(
                "Seleccionar Declaración:",
                [opt[0] for opt in declaration_options],
                format_func=lambda x: next(opt[1] for opt in declaration_options if opt[0] == x)
            )
            
            deputy_data = deputy_declarations.loc[selected_idx]
        else:
            deputy_data = deputy_declarations.iloc[0]
        
        st.markdown("---")
        
        # Layout
        col_left, col_right = st.columns([1.5, 2])
        
        with col_left:
            # Enhanced image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info
            st.markdown("### 📋 Información Personal")
            
            info_html = '<div class="info-grid">'
            
            # Personal information fields
            personal_fields = [
                ('📋 CARGO', 'informacion_personal_cargo', 'Diputado'),
                ('📍 CIRCUNSCRIPCIÓN', 'informacion_personal_circunscripcion', None),
                ('💑 ESTADO CIVIL', 'informacion_personal_estado_civil', None),
                ('💍 RÉGIMEN ECONÓMICO', 'informacion_personal_regimen_economico_matrimonial', None),
                ('📅 FECHA ELECCIÓN', 'informacion_personal_fecha_eleccion', None),
                ('📜 PRESENTACIÓN CREDENCIAL', 'informacion_personal_fecha_presentacion_credencial', None),
            ]
            
            for label, field, default in personal_fields:
                value = deputy_data.get(field, default)
                if value and str(value).lower() != 'nan':
                    if not value and default:
                        value = default
                    info_html += f'''
                    <div class="info-item">
                        <div class="info-label">{label}</div>
                        <div class="info-value">{value}</div>
                    </div>'''
            
            info_html += '</div>'
            st.markdown(info_html, unsafe_allow_html=True)
            
            # Social Media
            social_links = {
                "𝕏": deputy_data.get('twitter'),
                "📘": deputy_data.get('facebook'),
                "📸": deputy_data.get('instagram'),
                "🌐": deputy_data.get('website')
            }
            
            valid_links = {emoji: url for emoji, url in social_links.items() if pd.notna(url) and str(url).lower() != 'nan'}
            
            if valid_links:
                st.markdown("### 🌐 Redes Sociales")
                social_html = '<div class="social-pills">'
                emoji_titles = {
                    "𝕏": "X (Twitter)",
                    "📘": "Facebook",
                    "📸": "Instagram",
                    "🌐": "Sitio Web"
                }
                for emoji, url in valid_links.items():
                    title = emoji_titles.get(emoji, "")
                    social_html += f'<a href="{url}" target="_blank" class="social-pill" title="{title}">{emoji}</a>'
                social_html += '</div>'
                st.markdown(social_html, unsafe_allow_html=True)
            
            # Observaciones if exists
            observaciones = deputy_data.get('observaciones', '')
            if observaciones and str(observaciones).lower() != 'nan':
                st.markdown("### 📝 Observaciones")
                st.info(observaciones)
        
        with col_right:
            st.markdown(f"## 👤 {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            # Calculate metrics
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in salaries if isinstance(s, dict))
            
            if total_salary == 0:
                salary_text = str(deputy_data.get('rentas_percibidas_percepciones_salariales', ''))
                if "mensual" in salary_text.lower():
                    monthly_salary = extract_currency_value(salary_text)
                    total_salary = monthly_salary * 12
            
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            
            # Count all properties
            urban_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            rustic_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_rusticos']))
            total_properties = urban_properties + rustic_properties
            
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
            
            # Financial summary
            st.markdown("### 💰 Resumen Financiero")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**💵 Ingresos**")
                st.markdown(f"# {format_currency(total_salary)}")
                st.markdown(f"IRPF: **{format_currency(irpf)}**")
                st.markdown(f"Tipo: **{tax_rate:.2f}%**")
            
            with col2:
                st.markdown("**🏠 Patrimonio**")
                st.markdown(f"# {total_properties + vehicles_count}")
                st.markdown(f"Inmuebles: **{total_properties}**")
                st.markdown(f"Vehículos: **{vehicles_count}**")
            
            with col3:
                st.markdown("**💳 Deudas**")
                st.markdown(f"# {format_currency(total_debt)}")
                if total_debt > 0:
                    st.markdown(f"Activas: **{len(debts)}**")
                else:
                    st.markdown("*Sin deudas*")
            
            st.markdown("---")
            
            # Tabs with all information (removed Análisis tab)
            tabs = st.tabs([
                "💵 Ingresos", 
                "🏠 Inmuebles", 
                "💼 Sociedades",
                "💰 Activos",
                "🚗 Vehículos",
                "💳 Deudas",
                "📄 Otros"
            ])
            
            # TAB 1: INGRESOS
            with tabs[0]:
                st.markdown("#### 💵 Todas las Fuentes de Ingresos")
                
                if total_salary > 0:
                    st.success(f"💰 **Total Anual: {format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"📋 **IRPF: {format_currency_full(irpf)}** ({tax_rate:.2f}%)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 💼 Salarios")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                concepto = salary.get('concepto', f'Ingreso #{i+1}')
                                if str(concepto).lower() == 'nan':
                                    concepto = f'Ingreso #{i+1}'
                                
                                amount = extract_currency_value(salary.get('euros'))
                                if amount > 100000:
                                    st.error(f"💰 **{concepto}**")
                                elif amount > 50000:
                                    st.warning(f"💰 **{concepto}**")
                                else:
                                    st.info(f"💰 **{concepto}**")
                                
                                st.markdown(f"→ **{format_currency_full(amount)}**")
                    else:
                        st.info("Sin salarios declarados")
                    
                    st.markdown("##### 💸 Otras Rentas")
                    otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', ''))
                    if otras:
                        for item in otras:
                            if isinstance(item, dict):
                                concepto = item.get('concepto', 'Otra renta')
                                importe = extract_currency_value(item.get('euros', 0))
                                if importe > 0:
                                    st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                    else:
                        st.info("Sin otras rentas")
                
                with col2:
                    st.markdown("##### 📈 Dividendos y Participaciones")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        for div in dividends:
                            if isinstance(div, dict):
                                concepto = div.get('concepto', 'Inversión')
                                if str(concepto).lower() == 'nan':
                                    concepto = 'Inversión'
                                st.markdown(f"**📊 {concepto}**")
                                rendimientos = extract_currency_value(div.get('euros'))
                                if rendimientos > 0:
                                    st.markdown(f"→ **{format_currency_full(rendimientos)}**")
                    else:
                        st.info("Sin dividendos")
                    
                    st.markdown("##### 🏦 Intereses Financieros")
                    intereses = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', ''))
                    if intereses:
                        for item in intereses:
                            if isinstance(item, dict):
                                concepto = item.get('concepto', 'Interés')
                                importe = extract_currency_value(item.get('euros', 0))
                                if importe > 0:
                                    st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                    else:
                        st.info("Sin intereses financieros")
            
            # TAB 2: INMUEBLES
            with tabs[1]:
                st.markdown("#### 🏠 Bienes Inmuebles")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏢 Inmuebles Urbanos")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                st.markdown(f"**📍 Inmueble Urbano #{i+1}**")
                                
                                for key, value in prop.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                
                                st.markdown("")
                    else:
                        st.info("Sin inmuebles urbanos")
                
                with col2:
                    st.markdown("##### 🌾 Inmuebles Rústicos")
                    rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                    if rusticos:
                        for i, prop in enumerate(rusticos):
                            if isinstance(prop, dict):
                                st.markdown(f"**🚜 Inmueble Rústico #{i+1}**")
                                
                                for key, value in prop.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                
                                st.markdown("")
                    else:
                        st.info("Sin inmuebles rústicos")
            
            # TAB 3: SOCIEDADES
            with tabs[2]:
                st.markdown("#### 💼 Sociedades y Participaciones")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏢 Sociedades No Cotizadas")
                    sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                    if sociedades:
                        for i, soc in enumerate(sociedades):
                            if isinstance(soc, dict):
                                st.markdown(f"**🏭 Sociedad #{i+1}**")
                                for key, value in soc.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                st.markdown("")
                    else:
                        st.info("Sin sociedades no cotizadas")
                
                with col2:
                    st.markdown("##### 📊 Participaciones >5%")
                    participaciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                    if participaciones:
                        for i, part in enumerate(participaciones):
                            if isinstance(part, dict):
                                st.markdown(f"**📈 Participación #{i+1}**")
                                for key, value in part.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                st.markdown("")
                    else:
                        st.info("Sin participaciones superiores al 5%")
            
            # TAB 4: ACTIVOS FINANCIEROS
            with tabs[3]:
                st.markdown("#### 💰 Activos Financieros")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏦 Cuentas y Depósitos")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                        if total_accounts > 0:
                            st.success(f"💰 **Total: {format_currency_full(total_accounts)}**")
                        
                        for account in accounts:
                            if isinstance(account, dict):
                                desc = account.get('descripcion', 'Cuenta')
                                if str(desc).lower() == 'nan':
                                    desc = 'Cuenta'
                                saldo = extract_currency_value(account.get('saldo'))
                                if saldo > 0:
                                    st.markdown(f"**🏦 {desc}**")
                                    st.markdown(f"Saldo: **{format_currency_full(saldo)}**")
                    else:
                        st.info("Sin cuentas declaradas")
                    
                    st.markdown("##### 📈 Acciones y Participaciones")
                    acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                    if acciones:
                        for i, accion in enumerate(acciones):
                            if isinstance(accion, dict):
                                st.markdown(f"**📊 Acción/Participación #{i+1}**")
                                for key, value in accion.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.info("Sin acciones declaradas")
                
                with col2:
                    st.markdown("##### 📜 Deuda Pública y Valores")
                    deuda_publica = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
                    if deuda_publica:
                        for i, item in enumerate(deuda_publica):
                            if isinstance(item, dict):
                                st.markdown(f"**💼 Valor #{i+1}**")
                                for key, value in item.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.info("Sin deuda pública o valores")
            
            # TAB 5: VEHÍCULOS
            with tabs[4]:
                st.markdown("#### 🚗 Vehículos")
                vehicles = parse_json_field(deputy_data['vehiculos'])
                if vehicles:
                    st.info(f"🚙 **Total vehículos: {len(vehicles)}**")
                    
                    cols = st.columns(2)
                    for i, vehicle in enumerate(vehicles):
                        if isinstance(vehicle, dict):
                            with cols[i % 2]:
                                desc = vehicle.get('descripcion', f'Vehículo #{i+1}')
                                if str(desc).lower() == 'nan':
                                    desc = f'Vehículo #{i+1}'
                                st.markdown(f"**🚗 {desc}**")
                                
                                fecha = vehicle.get('fecha_adquisicion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Adquirido: {fecha}")
                                st.markdown("")
                else:
                    st.info("Sin vehículos declarados")
            
            # TAB 6: DEUDAS
            with tabs[5]:
                st.markdown("#### 💸 Deudas y Obligaciones")
                if debts:
                    st.error(f"💰 **Total Pendiente: {format_currency_full(total_debt)}**")
                    
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            desc = debt.get('descripcion', f'Deuda #{i+1}')
                            if str(desc).lower() == 'nan':
                                desc = f'Deuda #{i+1}'
                            
                            st.markdown(f"**📄 {desc}**")
                            
                            original = extract_currency_value(debt.get('importe_concedido'))
                            pending = extract_currency_value(debt.get('saldo_pendiente'))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if original > 0:
                                    st.markdown(f"Original: **{format_currency_full(original)}**")
                                fecha = debt.get('fecha_concesion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Fecha: {fecha}")
                            
                            with col2:
                                if pending > 0:
                                    st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                                if original > 0 and pending > 0:
                                    paid_pct = ((original - pending) / original) * 100
                                    if paid_pct > 50:
                                        st.success(f"✅ Pagado: {paid_pct:.1f}%")
                                    else:
                                        st.warning(f"⏳ Pagado: {paid_pct:.1f}%")
                            
                            st.markdown("---")
                else:
                    st.success("✅ No se han declarado deudas")
            
            # TAB 7: OTROS
            with tabs[6]:
                st.markdown("#### 📄 Otros Bienes y Derechos")
                
                otros_bienes = deputy_data.get('otros_bienes_no_declarados_anteriormente', '')
                if otros_bienes and str(otros_bienes).lower() != 'nan':
                    st.markdown("##### 📦 Otros Bienes No Declarados Anteriormente")
                    
                    otros_parsed = parse_json_field(otros_bienes)
                    if otros_parsed:
                        for i, item in enumerate(otros_parsed):
                            if isinstance(item, dict):
                                st.markdown(f"**Item #{i+1}**")
                                for key, value in item.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.write(otros_bienes)
                else:
                    st.info("No hay otros bienes declarados")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
