import streamlit as st
import pandas as pd
import json
import re
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Congreso de los Diputados - Portal de Transparencia",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---
def parse_json_field(field_value):
    """Safely parse JSON string fields."""
    if pd.isna(field_value) or field_value in ["", "[]", None]:
        return []
    try:
        data = json.loads(field_value)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, TypeError):
        return []

def parse_currency_value(value):
    """Convert currency strings to float."""
    if value is None or pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s_value = str(value).strip().replace('€', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(s_value)
    except (ValueError, TypeError):
        return 0.0

def format_currency(value):
    """Format number as currency."""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "No declarado"
    return f"{value:,.2f} €"

def get_currency_color(value):
    """Get color based on currency value."""
    if value > 100000:
        return "#00ff88"
    elif value > 50000:
        return "#66b3ff"
    elif value > 10000:
        return "#ffd700"
    else:
        return "#ff6b6b"

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    try:
        df = pd.read_csv('deputies_full_dataset.csv')
        
        if df.empty:
            st.error("❌ El archivo de datos está vacío")
            return pd.DataFrame()
        
        if 'source_file' in df.columns:
            df['declaration_date'] = pd.to_datetime(
                df['source_file'].str.extract(r'(\d{8})\.json$')[0], 
                errors='coerce'
            )
            df = df.sort_values('declaration_date', ascending=False).drop_duplicates('deputy_id', keep='first')
        
        if 'informacion_personal_nombre_y_apellidos' in df.columns:
            df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].fillna("Nombre no disponible")
            df = df.sort_values('informacion_personal_nombre_y_apellidos')
        
        return df
        
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'deputies_full_dataset.csv'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

# --- STUNNING CSS DESIGN ---
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Animated Background */
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            position: relative;
            overflow-x: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Floating particles effect */
        .stApp::before {
            content: '';
            position: fixed;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
            pointer-events: none;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
        }
        
        /* Main Header - Ultra Premium */
        .hero-container {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 30px;
            padding: 50px;
            margin: 0 0 40px 0;
            position: relative;
            overflow: hidden;
            box-shadow: 
                0 25px 50px rgba(0, 0, 0, 0.3),
                inset 0 1px 1px rgba(255, 255, 255, 0.2),
                0 0 100px rgba(139, 92, 246, 0.1);
        }
        
        .hero-container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #8b5cf6, #ec4899, #3b82f6, #8b5cf6);
            border-radius: 30px;
            opacity: 0.3;
            z-index: -1;
            animation: borderRotate 4s linear infinite;
        }
        
        @keyframes borderRotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #8b5cf6 25%, #ec4899 50%, #3b82f6 75%, #ffffff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: textShine 3s linear infinite;
            text-align: center;
            margin: 0;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }
        
        @keyframes textShine {
            to { background-position: 200% center; }
        }
        
        .hero-subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.2rem;
            margin-top: 15px;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        /* Deputy Name Card */
        .deputy-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(236, 72, 153, 0.15));
            backdrop-filter: blur(30px) saturate(200%);
            -webkit-backdrop-filter: blur(30px) saturate(200%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            padding: 40px;
            margin: 30px 0;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .deputy-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 30px 60px rgba(139, 92, 246, 0.3),
                0 0 100px rgba(236, 72, 153, 0.2);
        }
        
        .deputy-name {
            font-size: 2.8rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            text-shadow: 
                0 0 30px rgba(139, 92, 246, 0.5),
                0 0 60px rgba(236, 72, 153, 0.3);
            letter-spacing: -0.01em;
        }
        
        .deputy-role {
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 10px;
            font-weight: 500;
            letter-spacing: 1px;
        }
        
        /* Premium Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .glass-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #8b5cf6, transparent);
            animation: scanline 3s linear infinite;
        }
        
        @keyframes scanline {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .glass-card:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-3px);
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.2),
                0 0 30px rgba(139, 92, 246, 0.2);
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        /* Info Cards with Gradient Borders */
        .info-card-premium {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.08));
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            position: relative;
            border: 1px solid transparent;
            background-clip: padding-box;
            transition: all 0.3s ease;
        }
        
        .info-card-premium::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 20px;
            padding: 1px;
            background: linear-gradient(135deg, #8b5cf6, #ec4899, #3b82f6);
            -webkit-mask: 
                linear-gradient(#fff 0 0) content-box, 
                linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            opacity: 0.5;
        }
        
        .info-card-premium:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
        }
        
        /* Data Rows */
        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 20px;
            margin: 12px 0;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(236, 72, 153, 0.05));
            border-radius: 15px;
            border-left: 4px solid transparent;
            border-image: linear-gradient(135deg, #8b5cf6, #ec4899) 1;
            transition: all 0.3s ease;
        }
        
        .data-row:hover {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        .data-label {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.95rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .data-value {
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 700;
            font-family: 'Space Grotesk', monospace;
        }
        
        .data-value-highlight {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }
        
        /* Social Media Buttons - Premium */
        .social-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .social-pill {
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 14px 28px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.95rem;
            color: white !important;
            text-decoration: none !important;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .social-pill::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            transition: left 0.5s ease;
        }
        
        .social-pill:hover::before {
            left: 100%;
        }
        
        .social-pill:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .social-facebook {
            background: linear-gradient(135deg, #1877f2, #0c63d4);
        }
        
        .social-twitter {
            background: linear-gradient(135deg, #1da1f2, #0c85d0);
        }
        
        .social-instagram {
            background: linear-gradient(135deg, #f58529, #dd2a7b, #8134af);
        }
        
        .social-website {
            background: linear-gradient(135deg, #8b5cf6, #6d28d9);
        }
        
        /* Metrics - Ultra Premium */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
            backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 20px;
            position: relative;
            overflow: hidden;
            transition: all 0.4s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 20px 40px rgba(139, 92, 246, 0.2),
                0 0 50px rgba(236, 72, 153, 0.1);
            border-color: rgba(139, 92, 246, 0.4);
        }
        
        [data-testid="metric-container"]::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.1), transparent);
            animation: pulse 3s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.5); opacity: 0; }
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-family: 'Space Grotesk', monospace !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        
        /* Tabs - Premium Style */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 8px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: rgba(255, 255, 255, 0.6);
            border-radius: 15px;
            padding: 14px 28px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            border: 1px solid transparent;
            position: relative;
            overflow: hidden;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(139, 92, 246, 0.1);
            color: white;
            border-color: rgba(139, 92, 246, 0.3);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2));
            color: white;
            border: 1px solid rgba(139, 92, 246, 0.4);
            box-shadow: 0 5px 20px rgba(139, 92, 246, 0.2);
        }
        
        /* Sidebar - Premium */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 12, 41, 0.98), rgba(48, 43, 99, 0.98));
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        section[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            color: white;
            border: none;
            font-weight: 600;
            border-radius: 15px;
            padding: 12px 24px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(139, 92, 246, 0.3);
        }
        
        section[data-testid="stSidebar"] .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.4);
        }
        
        /* Expanders - Premium */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1)) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 18px 24px !important;
            font-weight: 600 !important;
            color: white !important;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2)) !important;
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(139, 92, 246, 0.2);
        }
        
        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px;
            color: rgba(255, 255, 255, 0.5);
        }
        
        .empty-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            filter: grayscale(50%);
            opacity: 0.5;
        }
        
        /* Section Headers */
        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 30px 0 20px 0;
            position: relative;
            padding-bottom: 15px;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 3px;
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
            border-radius: 2px;
        }
        
        /* Premium Badge */
        .premium-badge {
            display: inline-block;
            padding: 8px 20px;
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            color: #1a1a2e;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.85rem;
            margin-left: 15px;
            animation: shine 2s ease-in-out infinite;
        }
        
        @keyframes shine {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.05); }
        }
        
        /* Loading Animation */
        .loading-bar {
            height: 3px;
            background: linear-gradient(90deg, #8b5cf6, #ec4899, #8b5cf6);
            background-size: 200% 100%;
            animation: loading 2s linear infinite;
            border-radius: 3px;
        }
        
        @keyframes loading {
            0% { background-position: 0% 0%; }
            100% { background-position: 200% 0%; }
        }
    </style>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # Inject CSS
    inject_css()
    
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">🏛️ Portal de Transparencia</h1>
            <p class="hero-subtitle">Congreso de los Diputados de España</p>
            <div class="loading-bar" style="margin-top: 30px;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <h2>No hay datos disponibles</h2>
                <p>Por favor, verifica que el archivo de datos esté disponible.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 30px 0;">
                <h2 style="color: #8b5cf6; font-weight: 800;">🎯 Panel de Control</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Search with icon
        search = st.text_input("🔍 **Buscar diputado**", placeholder="Escribe un nombre...")
        
        # Filter
        if 'informacion_personal_circunscripcion' in df.columns:
            constituencies = ["Todas las circunscripciones"] + sorted(df['informacion_personal_circunscripcion'].dropna().unique().tolist())
            selected_constituency = st.selectbox("📍 **Filtrar por circunscripción**", constituencies)
        else:
            selected_constituency = "Todas las circunscripciones"
        
        # Apply filters
        filtered_df = df.copy()
        
        if search and 'informacion_personal_nombre_y_apellidos' in df.columns:
            filtered_df = filtered_df[
                filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(
                    search, case=False, na=False
                )
            ]
        
        if selected_constituency != "Todas las circunscripciones" and 'informacion_personal_circunscripcion' in df.columns:
            filtered_df = filtered_df[
                filtered_df['informacion_personal_circunscripcion'] == selected_constituency
            ]
        
        if filtered_df.empty:
            st.error("❌ No se encontraron resultados")
            return
        
        # Deputy selector
        st.markdown("---")
        
        if 'informacion_personal_nombre_y_apellidos' in filtered_df.columns:
            deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
            selected_deputy = st.selectbox("👤 **Seleccionar Diputado/a**", deputy_names)
        else:
            st.error("Error en los datos")
            return
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 **Estadísticas**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", f"{len(df):,}")
        with col2:
            st.metric("Filtrados", f"{len(filtered_df):,}")
        
        # Premium badge
        st.markdown("""
            <div style="text-align: center; margin-top: 30px;">
                <span class="premium-badge">✨ VERSIÓN PREMIUM</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if selected_deputy:
        deputy_data = filtered_df[
            filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy
        ].iloc[0]
        
        # Deputy Card
        st.markdown(f"""
            <div class="deputy-card">
                <h1 class="deputy-name">{deputy_data.get('informacion_personal_nombre_y_apellidos', 'Nombre no disponible')}</h1>
                <p class="deputy-role">
                    {deputy_data.get('informacion_personal_cargo', 'Diputado/a')} • 
                    {deputy_data.get('informacion_personal_circunscripcion', 'España')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Social Media
        social_html = ""
        if pd.notna(deputy_data.get('facebook')):
            social_html += f'<a href="{deputy_data.get("facebook")}" target="_blank" class="social-pill social-facebook">📘 Facebook</a>'
        if pd.notna(deputy_data.get('twitter')):
            social_html += f'<a href="{deputy_data.get("twitter")}" target="_blank" class="social-pill social-twitter">🐦 Twitter</a>'
        if pd.notna(deputy_data.get('instagram')):
            social_html += f'<a href="{deputy_data.get("instagram")}" target="_blank" class="social-pill social-instagram">📸 Instagram</a>'
        if pd.notna(deputy_data.get('website')):
            social_html += f'<a href="{deputy_data.get("website")}" target="_blank" class="social-pill social-website">🌐 Sitio Web</a>'
        
        if social_html:
            st.markdown(f'<div class="social-container">{social_html}</div>', unsafe_allow_html=True)
        
        # Calculate financial metrics
        total_rentas = sum(
            parse_currency_value(r.get('euros')) 
            for r in parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales', []))
        )
        
        otras_rentas = sum([
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones', []))),
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', []))),
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', [])))
        ])
        
        total_deudas = sum(
            parse_currency_value(d.get('saldo_pendiente')) 
            for d in parse_json_field(deputy_data.get('deudas_y_obligaciones', []))
        )
        
        irpf_pagado = parse_currency_value(deputy_data.get('irpf_cantidad_pagada'))
        
        # Financial Overview with Icons
        st.markdown('<h2 class="section-title">💎 Resumen Financiero</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Ingresos Salariales", format_currency(total_rentas))
        with col2:
            st.metric("📈 Otras Rentas", format_currency(otras_rentas))
        with col3:
            st.metric("💳 Deuda Pendiente", format_currency(total_deudas))
        with col4:
            st.metric("🏛️ IRPF Pagado", format_currency(irpf_pagado))
        
        # Premium Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 **Personal**",
            "💰 **Rentas**",
            "🏠 **Patrimonio**",
            "📊 **Financiero**",
            "📋 **Deudas**"
        ])
        
        with tab1:
            st.markdown('<h2 class="section-title">Información Personal</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                    <div class="info-card-premium">
                        <div class="data-row">
                            <span class="data-label">👤 Estado Civil</span>
                            <span class="data-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">📅 Fecha de Elección</span>
                            <span class="data-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="info-card-premium">
                        <div class="data-row">
                            <span class="data-label">💍 Régimen Económico</span>
                            <span class="data-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial', 'No aplica')}</span>
                        </div>
                        <div class="data-row">
                            <span class="data-label">📋 Fecha Credencial</span>
                            <span class="data-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Visual representation
            if pd.notna(deputy_data.get('informacion_personal_fecha_eleccion')):
                st.markdown('<h3 class="section-title">📊 Línea de Tiempo</h3>', unsafe_allow_html=True)
                st.info(f"🗓️ En el cargo desde: {deputy_data.get('informacion_personal_fecha_eleccion')}")
        
        with tab2:
            st.markdown('<h2 class="section-title">Declaración de Rentas 2022</h2>', unsafe_allow_html=True)
            
            # Create visual cards for each income type
            rentas_types = [
                ("💼 Percepciones Salariales", 'rentas_percibidas_percepciones_salariales', "#8b5cf6"),
                ("📈 Dividendos", 'rentas_percibidas_dividendos_y_participaciones', "#ec4899"),
                ("🏦 Intereses", 'rentas_percibidas_intereses_financieros', "#3b82f6"),
                ("📑 Otras Rentas", 'rentas_percibidas_otras_rentas', "#10b981")
            ]
            
            for title, field, color in rentas_types:
                data = parse_json_field(deputy_data.get(field))
                if data:
                    with st.expander(f"{title} ({len(data)} registros)", expanded=True):
                        for item in data:
                            concepto = item.get('concepto', 'Sin descripción')
                            euros = parse_currency_value(item.get('euros'))
                            st.markdown(f"""
                                <div class="data-row">
                                    <span style="color: rgba(255,255,255,0.8);">{concepto}</span>
                                    <span class="data-value-highlight">{euros:,.2f} €</span>
                                </div>
                            """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<h2 class="section-title">Bienes Patrimoniales</h2>', unsafe_allow_html=True)
            
            # Properties with cards
            urbanos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos'))
            if urbanos:
                st.markdown("### 🏢 Inmuebles Urbanos")
                for idx, item in enumerate(urbanos, 1):
                    st.markdown(f"""
                        <div class="glass-card">
                            <h4 style="color: #8b5cf6; margin-bottom: 20px;">
                                📍 Propiedad #{idx}
                            </h4>
                            <div class="data-row">
                                <span class="data-label">Ubicación</span>
                                <span class="data-value">{item.get('situacion', 'No especificado')}</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">Tipo</span>
                                <span class="data-value">{item.get('clase_y_caracteristicas', 'No especificado')}</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">Título</span>
                                <span class="data-value">{item.get('titulo_adquisicion', 'No especificado')}</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">Porcentaje</span>
                                <span class="data-value-highlight">{item.get('porcentaje_sobre_el_bien', '100')}%</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Vehicles
            vehiculos = parse_json_field(deputy_data.get('vehiculos'))
            if vehiculos:
                st.markdown("### 🚗 Vehículos")
                for v in vehiculos:
                    st.markdown(f"""
                        <div class="glass-card">
                            <div class="data-row">
                                <span class="data-label">🚙 Modelo</span>
                                <span class="data-value">{v.get('marca_y_modelo', 'No especificado')}</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">📅 Adquisición</span>
                                <span class="data-value">{v.get('fecha_adquisicion', 'No especificado')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<h2 class="section-title">Activos Financieros</h2>', unsafe_allow_html=True)
            
            # Bank accounts with total
            cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
            if cuentas:
                total_cuentas = sum(parse_currency_value(c.get('saldo')) for c in cuentas)
                
                st.markdown(f"""
                    <div class="info-card-premium" style="text-align: center; margin-bottom: 30px;">
                        <h3 style="color: #8b5cf6; margin: 0;">💰 Total en Cuentas</h3>
                        <p style="font-size: 2.5rem; font-weight: 800; margin: 10px 0;">
                            <span class="data-value-highlight">{total_cuentas:,.2f} €</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🏦 Detalle de Cuentas", expanded=True):
                    for cuenta in cuentas:
                        tipo = cuenta.get('descripcion', cuenta.get('tipo', 'Cuenta'))
                        saldo = parse_currency_value(cuenta.get('saldo'))
                        st.markdown(f"""
                            <div class="data-row">
                                <span>{tipo}</span>
                                <span class="data-value">{saldo:,.2f} €</span>
                            </div>
                        """, unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<h2 class="section-title">Deudas y Obligaciones</h2>', unsafe_allow_html=True)
            
            deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
            if deudas:
                for deuda in deudas:
                    desc = deuda.get('descripcion', deuda.get('prestamo', 'Deuda'))
                    importe = parse_currency_value(deuda.get('importe_concedido'))
                    pendiente = parse_currency_value(deuda.get('saldo_pendiente'))
                    
                    # Calculate percentage paid
                    if importe > 0:
                        percentage_paid = ((importe - pendiente) / importe) * 100
                    else:
                        percentage_paid = 0
                    
                    st.markdown(f"""
                        <div class="glass-card">
                            <h4 style="color: #ec4899; margin-bottom: 20px;">💳 {desc}</h4>
                            <div class="data-row">
                                <span class="data-label">📅 Fecha</span>
                                <span class="data-value">{deuda.get('fecha_concesion', 'N/A')}</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">💰 Importe Original</span>
                                <span class="data-value">{importe:,.2f} €</span>
                            </div>
                            <div class="data-row">
                                <span class="data-label">💳 Saldo Pendiente</span>
                                <span class="data-value-highlight">{pendiente:,.2f} €</span>
                            </div>
                            <div style="margin-top: 20px;">
                                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 10px; overflow: hidden;">
                                    <div style="background: linear-gradient(135deg, #8b5cf6, #ec4899); height: 100%; width: {percentage_paid}%; transition: width 1s ease;"></div>
                                </div>
                                <p style="text-align: center; margin-top: 10px; color: rgba(255,255,255,0.6);">
                                    {percentage_paid:.1f}% pagado
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="empty-state">
                        <div class="empty-icon">✨</div>
                        <h3>Sin deudas declaradas</h3>
                        <p>Este diputado no tiene deudas registradas.</p>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
