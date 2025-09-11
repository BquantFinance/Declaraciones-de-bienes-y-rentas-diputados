import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Congreso de los Diputados - Portal de Transparencia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM DARK MODE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    /* === CORE THEME === */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #0f0f23 50%, #0a0a0a 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e0e0e0;
        position: relative;
        overflow-x: hidden;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(120, 80, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 80, 160, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(80, 200, 255, 0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
    }

    .main > div {
        position: relative;
        z-index: 2;
    }

    /* === ANIMATED GRADIENT ORBS === */
    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        33% { transform: translateY(-20px) translateX(10px); }
        66% { transform: translateY(20px) translateX(-10px); }
    }

    /* === MAIN HEADER === */
    .hero-header {
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.1) 0%, rgba(255, 80, 160, 0.1) 100%);
        backdrop-filter: blur(40px) saturate(150%);
        -webkit-backdrop-filter: blur(40px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        padding: 48px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: glow 3s ease-in-out infinite alternate;
    }

    @keyframes glow {
        0% { box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1); }
        100% { box-shadow: 0 25px 70px rgba(120, 80, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.15); }
    }

    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(120, 80, 255, 0.1),
            transparent,
            rgba(255, 80, 160, 0.1),
            transparent
        );
        animation: rotate 10s linear infinite;
    }

    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .deputy-name {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #a0a0ff 50%, #ff80d0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.1;
        position: relative;
        z-index: 2;
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .deputy-subtitle {
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.6);
        margin-top: 12px;
        font-weight: 400;
        letter-spacing: 0.02em;
        position: relative;
        z-index: 2;
    }

    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 100px;
        background: linear-gradient(135deg, rgba(80, 255, 160, 0.2), rgba(80, 200, 255, 0.2));
        border: 1px solid rgba(80, 255, 160, 0.3);
        font-size: 0.85rem;
        font-weight: 600;
        color: #80ffa0;
        margin-top: 16px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }

    /* === METRICS CARDS === */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.07) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.1) 100%);
        border-color: rgba(120, 80, 255, 0.3);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            0 0 60px rgba(120, 80, 255, 0.1);
    }

    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.6s;
    }

    [data-testid="metric-container"]:hover::before {
        left: 100%;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #7850ff 0%, #ff50a0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* === SECTION HEADERS === */
    .section-divider {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 48px 0 24px 0;
        padding-bottom: 16px;
        position: relative;
        letter-spacing: -0.01em;
    }

    .section-divider::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, #7850ff, #ff50a0);
        border-radius: 2px;
        animation: expand 1s ease-out forwards;
    }

    @keyframes expand {
        from { width: 0; }
        to { width: 100px; }
    }

    /* === GLASS CARDS === */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px) saturate(150%);
        -webkit-backdrop-filter: blur(10px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 32px;
        margin: 20px 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .glass-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            0 0 30px rgba(120, 80, 255, 0.1);
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: slide 3s ease-in-out infinite;
    }

    @keyframes slide {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    /* === INFO ITEMS === */
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        margin: 8px 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.05) 100%);
        border-radius: 12px;
        border-left: 3px solid transparent;
        border-image: linear-gradient(135deg, #7850ff, #ff50a0) 1;
        transition: all 0.3s ease;
    }

    .info-row:hover {
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.1) 0%, rgba(255, 80, 160, 0.1) 100%);
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .info-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .info-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: right;
    }

    /* === SOCIAL MEDIA BUTTONS === */
    .social-container {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin: 32px 0;
        flex-wrap: wrap;
    }

    .social-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 100px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 0.95rem;
        color: white !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .social-btn::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .social-btn:hover::before {
        width: 300px;
        height: 300px;
    }

    .social-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .social-facebook {
        background: linear-gradient(135deg, #1877f2, #0c5ed7);
    }

    .social-twitter {
        background: linear-gradient(135deg, #1da1f2, #0c8cdb);
    }

    .social-instagram {
        background: linear-gradient(135deg, #e1306c, #f77737, #fcaf45);
    }

    .social-website {
        background: linear-gradient(135deg, #6c63ff, #4a43e0);
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 8px;
        gap: 8px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        position: relative;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.9);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.2), rgba(255, 80, 160, 0.2));
        color: white;
        border: 1px solid rgba(120, 80, 255, 0.3);
    }

    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.08) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px !important;
        padding: 16px 20px !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.9) !important;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.1) 0%, rgba(255, 80, 160, 0.1) 100%);
        border-color: rgba(120, 80, 255, 0.3);
        transform: translateX(4px);
    }

    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0 0 16px 16px;
        padding: 20px !important;
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 10, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.2), rgba(255, 80, 160, 0.2));
        border: 1px solid rgba(120, 80, 255, 0.3);
        color: white;
        font-weight: 600;
        padding: 12px;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(120, 80, 255, 0.3), rgba(255, 80, 160, 0.3));
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(120, 80, 255, 0.2);
    }

    /* === SEARCH INPUT === */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px 16px !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(120, 80, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(120, 80, 255, 0.2) !important;
    }

    /* === SELECT BOX === */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(120, 80, 255, 0.3) !important;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #7850ff, #ff50a0);
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.3);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #9070ff, #ff70b0);
    }

    /* === EMPTY STATE === */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: rgba(255, 255, 255, 0.4);
        font-size: 1.1rem;
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 20px;
        opacity: 0.5;
    }

    /* === DATA VALUE HIGHLIGHT === */
    .highlight-value {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, rgba(80, 255, 160, 0.2), rgba(80, 200, 255, 0.2));
        border-radius: 8px;
        font-weight: 600;
        color: #80ffa0;
        font-family: 'JetBrains Mono', monospace;
    }

    /* === LOADING ANIMATION === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .glass-card {
        animation: fadeIn 0.6s ease-out;
    }

    /* === PREMIUM EFFECTS === */
    .premium-border {
        position: relative;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.08) 100%);
        border-radius: 24px;
        padding: 2px;
        margin: 20px 0;
    }

    .premium-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #7850ff, #ff50a0, #50ffff, #7850ff);
        border-radius: 24px;
        opacity: 0.5;
        z-index: -1;
        animation: gradientRotate 3s linear infinite;
    }

    @keyframes gradientRotate {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }

    .premium-content {
        background: #0a0a0a;
        border-radius: 22px;
        padding: 32px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def parse_json_field(field_value):
    """Safely parse JSON string fields."""
    if pd.isna(field_value) or field_value in ["", "[]"]:
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
    """Format number as currency with style."""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return '<span style="color: rgba(255,255,255,0.3);">No declarado</span>'
    formatted = f"{value:,.2f} €"
    if value > 1000000:
        return f'<span class="highlight-value">💎 {formatted}</span>'
    elif value > 100000:
        return f'<span style="color: #80ffa0; font-weight: 600;">{formatted}</span>'
    return formatted

def display_social_media(row):
    """Display social media links with modern styling."""
    links = [
        ("facebook", "📘", "Facebook"),
        ("twitter", "🐦", "Twitter"),
        ("instagram", "📸", "Instagram"),
        ("website", "🌐", "Sitio Web")
    ]
    
    social_html = ""
    for key, icon, label in links:
        url = row.get(key)
        if pd.notna(url) and url:
            social_html += f'<a href="{url}" target="_blank" class="social-btn social-{key}"><span>{icon}</span> {label}</a>'
    
    if social_html:
        st.markdown(f'<div class="social-container">{social_html}</div>', unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    df = pd.read_csv('deputies_full_dataset.csv')
    # Fix: Extract returns a DataFrame, select first column
    df['declaration_date'] = pd.to_datetime(df['source_file'].str.extract(r'(\d{8})\.json$')[0], errors='coerce')
    df = df.sort_values('declaration_date', ascending=False).drop_duplicates('deputy_id', keep='first')
    df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].fillna("Nombre no disponible")
    return df.sort_values('informacion_personal_nombre_y_apellidos')

# --- MAIN APP ---
def main():
    # Load data
    df = load_data()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 2rem; font-weight: 800; 
                    background: linear-gradient(135deg, #7850ff 0%, #ff50a0 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;">
                    ⚡ Portal de Transparencia
                </h1>
                <p style="color: rgba(255,255,255,0.5); margin-top: 10px;">
                    Congreso de los Diputados
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Search
        search = st.text_input("🔍 **Buscar diputado**", placeholder="Nombre...")
        
        # Filter by constituency
        constituencies = ["Todas las circunscripciones"] + sorted(df['informacion_personal_circunscripcion'].dropna().unique().tolist())
        selected_constituency = st.selectbox("📍 **Circunscripción**", constituencies)
        
        # Apply filters
        filtered_df = df.copy()
        if search:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search, case=False, na=False)]
        if selected_constituency != "Todas las circunscripciones":
            filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
        
        if filtered_df.empty:
            st.error("⚠️ No se encontraron resultados")
            return
        
        # Deputy selector
        st.markdown("---")
        selected_deputy = st.selectbox(
            "👤 **Seleccionar Diputado/a**",
            filtered_df['informacion_personal_nombre_y_apellidos'].tolist(),
            help="Seleccione un diputado para ver su información"
        )
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 **Estadísticas**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", f"{len(df):,}", delta=None)
        with col2:
            st.metric("Filtrados", f"{len(filtered_df):,}", delta=None)
        
        # Info
        st.markdown("---")
        st.markdown("""
            <div style="padding: 20px; background: rgba(120,80,255,0.1); border-radius: 12px; border: 1px solid rgba(120,80,255,0.2);">
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0;">
                    💡 <strong>Última actualización:</strong><br/>
                    Declaraciones 2022
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
    
    # Hero Header
    st.markdown(f"""
        <div class="hero-header">
            <h1 class="deputy-name">{deputy_data['informacion_personal_nombre_y_apellidos']}</h1>
            <p class="deputy-subtitle">
                {deputy_data.get('informacion_personal_cargo', 'Diputado/a')} • 
                {deputy_data.get('informacion_personal_circunscripcion', 'España')}
            </p>
            <span class="status-badge">✓ Declaración Activa</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Social Media
    display_social_media(deputy_data)
    
    # Calculate financial summary
    total_rentas = sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales', [])))
    otras_rentas = sum([
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones', []))),
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', []))),
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', [])))
    ])
    total_deudas = sum(parse_currency_value(d.get('saldo_pendiente')) for d in parse_json_field(deputy_data.get('deudas_y_obligaciones', [])))
    irpf_pagado = parse_currency_value(deputy_data.get('irpf_cantidad_pagada'))
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Ingresos Salariales", f"{total_rentas:,.0f} €")
    with col2:
        st.metric("📈 Otras Rentas", f"{otras_rentas:,.0f} €")
    with col3:
        st.metric("💳 Deuda Pendiente", f"{total_deudas:,.0f} €")
    with col4:
        st.metric("🏛️ IRPF Pagado", f"{irpf_pagado:,.0f} €")
    
    # Tabs with content
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 **Información Personal**",
        "💰 **Rentas e Ingresos**", 
        "🏠 **Patrimonio Inmobiliario**",
        "📊 **Activos Financieros**",
        "📋 **Deudas y Otros**"
    ])
    
    with tab1:
        st.markdown('<h2 class="section-divider">Datos Personales</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="info-row">
                        <span class="info-label">Estado Civil</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Fecha de Elección</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="info-row">
                        <span class="info-label">Régimen Económico</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial') or 'No aplica'}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Fecha Credencial</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<h2 class="section-divider">Declaración de Rentas 2022</h2>', unsafe_allow_html=True)
        
        rentas_sections = [
            ("💼 Percepciones Salariales", 'rentas_percibidas_percepciones_salariales'),
            ("📈 Dividendos y Participaciones", 'rentas_percibidas_dividendos_y_participaciones'),
            ("🏦 Intereses Financieros", 'rentas_percibidas_intereses_financieros'),
            ("📑 Otras Rentas", 'rentas_percibidas_otras_rentas')
        ]
        
        for title, field in rentas_sections:
            data = parse_json_field(deputy_data.get(field))
            if data:
                with st.expander(f"{title} ({len(data)} registros)", expanded=True):
                    for item in data:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = parse_currency_value(item.get('euros'))
                        st.markdown(f"""
                            <div class="info-row">
                                <span style="color: rgba(255,255,255,0.8);">{concepto}</span>
                                <span class="highlight-value">{euros:,.2f} €</span>
                            </div>
                        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="section-divider">Bienes Inmuebles</h2>', unsafe_allow_html=True)
        
        # Inmuebles urbanos
        urbanos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos'))
        if urbanos:
            st.markdown("### 🏢 Inmuebles Urbanos")
            for item in urbanos:
                st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="color: #7850ff; margin-bottom: 16px;">📍 {item.get('situacion', 'Ubicación no especificada')}</h4>
                        <div class="info-row">
                            <span class="info-label">Tipo</span>
                            <span class="info-value">{item.get('clase_y_caracteristicas', 'No especificado')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Título</span>
                            <span class="info-value">{item.get('titulo_adquisicion', 'No especificado')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Porcentaje</span>
                            <span class="info-value">{item.get('porcentaje_sobre_el_bien', 'No especificado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Vehículos
        vehiculos = parse_json_field(deputy_data.get('vehiculos'))
        if vehiculos:
            st.markdown("### 🚗 Vehículos")
            for v in vehiculos:
                st.markdown(f"""
                    <div class="glass-card">
                        <div class="info-row">
                            <span class="info-label">Vehículo</span>
                            <span class="info-value">{v.get('marca_y_modelo', 'No especificado')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Fecha Adquisición</span>
                            <span class="info-value">{v.get('fecha_adquisicion', 'No especificado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<h2 class="section-divider">Activos Financieros</h2>', unsafe_allow_html=True)
        
        # Cuentas
        cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
        if cuentas:
            st.markdown("### 🏦 Cuentas Bancarias")
            total_cuentas = sum(parse_currency_value(c.get('saldo')) for c in cuentas)
            st.markdown(f"""
                <div class="premium-border">
                    <div class="premium-content">
                        <h3 style="color: #80ffa0; margin-bottom: 20px;">
                            Total en cuentas: <span class="highlight-value">{total_cuentas:,.2f} €</span>
                        </h3>
            """, unsafe_allow_html=True)
            
            for cuenta in cuentas:
                tipo = cuenta.get('descripcion', cuenta.get('tipo', 'Cuenta'))
                saldo = parse_currency_value(cuenta.get('saldo'))
                st.markdown(f"""
                    <div class="info-row">
                        <span>{tipo}</span>
                        <span class="info-value">{saldo:,.2f} €</span>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<h2 class="section-divider">Deudas y Obligaciones</h2>', unsafe_allow_html=True)
        
        deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
        if deudas:
            for deuda in deudas:
                desc = deuda.get('descripcion', deuda.get('prestamo', 'Deuda'))
                importe = parse_currency_value(deuda.get('importe_concedido'))
                pendiente = parse_currency_value(deuda.get('saldo_pendiente'))
                
                st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="color: #ff50a0; margin-bottom: 20px;">💳 {desc}</h4>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                            <div>
                                <div class="info-label">Fecha Concesión</div>
                                <div class="info-value">{deuda.get('fecha_concesion', 'N/A')}</div>
                            </div>
                            <div>
                                <div class="info-label">Importe Original</div>
                                <div class="info-value" style="color: #ffa0a0;">{importe:,.2f} €</div>
                            </div>
                            <div>
                                <div class="info-label">Saldo Pendiente</div>
                                <div class="info-value" style="color: #ff50a0; font-weight: 700;">{pendiente:,.2f} €</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">✨</div>
                    <p>No hay deudas declaradas</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
