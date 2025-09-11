import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64 # Moved import to the top

# Page configuration
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Enhanced CSS with glassmorphism
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main App Styling */
        .stApp {
            background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            position: relative;
        }
        
        /* Animated background gradient */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 1;
        }
        
        .main .block-container {
            padding-top: 1rem;
            max-width: 1600px;
            position: relative;
            z-index: 2;
        }
        
        /* Disclaimer Container */
        .disclaimer-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 3rem;
            margin: 2rem auto;
            max-width: 800px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.3),
                inset 0 0 30px rgba(255, 255, 255, 0.05);
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .disclaimer-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
        }
        
        .disclaimer-text {
            color: #e2e8f0;
            font-size: 1.1rem;
            line-height: 1.8;
            text-align: justify;
            margin-bottom: 2rem;
        }
        
        .disclaimer-text strong {
            color: #fbbf24;
            font-weight: 600;
        }
        
        /* Typography with glow effects */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
            filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.3));
            transition: all 0.3s ease;
        }
        
        h1:hover {
            filter: drop-shadow(0 0 30px rgba(102, 126, 234, 0.5));
            transform: scale(1.02);
        }
        
        h2 {
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        h3 {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
            transition: color 0.3s ease;
        }
        
        h3:hover {
            color: #667eea !important;
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }
        
        h4, h5 {
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }
        
        /* Glassmorphism cards */
        div[data-testid="stHorizontalBlock"],
        div[data-testid="column"] {
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
        }
        
        /* Info Grid with glassmorphism */
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
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .info-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.1), 
                transparent);
            transition: left 0.5s ease;
        }
        
        .info-item:hover::before {
            left: 100%;
        }
        
        .info-item:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: rgba(102, 126, 234, 0.4);
            box-shadow: 
                0 12px 40px rgba(102, 126, 234, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.05);
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.15) 0%, 
                rgba(118, 75, 162, 0.08) 100%);
        }
        
        .info-label {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            font-weight: 600;
            opacity: 0.8;
            transition: opacity 0.3s ease;
        }
        
        .info-item:hover .info-label {
            opacity: 1;
            color: #b4bdc8;
        }
        
        .info-value {
            font-size: 1.1rem;
            color: #ffffff;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .info-item:hover .info-value {
            transform: translateX(5px);
        }
        
        /* Enhanced Metrics with glassmorphism */
        div[data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 1.2rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            position: relative;
            overflow: hidden;
        }
        
        div[data-testid="metric-container"]::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(
                circle,
                rgba(102, 126, 234, 0.1) 0%,
                transparent 70%
            );
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        
        div[data-testid="metric-container"]:hover::after {
            opacity: 1;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-8px) scale(1.05);
            box-shadow: 
                0 20px 50px rgba(102, 126, 234, 0.4),
                inset 0 0 30px rgba(255, 255, 255, 0.1);
            border-color: rgba(102, 126, 234, 0.5);
            background: rgba(255, 255, 255, 0.08);
        }
        
        div[data-testid="metric-container"] label {
            color: #94a3b8 !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover label {
            opacity: 1;
        }
        
        div[data-testid="metric-container"] div[data-testid="metric-value"] {
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            transition: all 0.3s ease;
        }
        
        div[data-testid="metric-container"]:hover div[data-testid="metric-value"] {
            transform: scale(1.1);
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.7);
        }
        
        /* Glassmorphic Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stTabs [data-baseweb="tab"]::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.3s ease, height 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover::before {
            width: 100%;
            height: 100%;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff;
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.2) 0%, 
                rgba(118, 75, 162, 0.2) 100%);
            color: #ffffff !important;
            font-weight: 600;
            box-shadow: 
                inset 0 2px 4px rgba(255, 255, 255, 0.1),
                0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Enhanced Social Media Pills */
        .social-pills {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .social-pill {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.1);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            font-size: 1.5rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .social-pill::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.4s ease, height 0.4s ease;
        }
        
        .social-pill:hover::before {
            width: 120%;
            height: 120%;
        }
        
        .social-pill:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: scale(1.2) rotate(10deg);
            box-shadow: 
                0 8px 25px rgba(102, 126, 234, 0.4),
                inset 0 0 15px rgba(255, 255, 255, 0.2);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        /* Enhanced Input Fields with glassmorphism */
        .stSelectbox > div > div, 
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stSelectbox > div > div:hover, 
        .stTextInput > div > div > input:hover {
            border-color: rgba(102, 126, 234, 0.5) !important;
            box-shadow: 
                0 0 0 3px rgba(102, 126, 234, 0.1),
                0 8px 25px rgba(102, 126, 234, 0.2) !important;
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.08) !important;
        }
        
        .stSelectbox > div > div:focus, 
        .stTextInput > div > div > input:focus {
            border-color: rgba(102, 126, 234, 0.7) !important;
            box-shadow: 
                0 0 0 4px rgba(102, 126, 234, 0.2),
                0 10px 30px rgba(102, 126, 234, 0.3) !important;
            background: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Enhanced Alert Messages */
        .stSuccess, .stWarning, .stError, .stInfo {
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }
        
        .stSuccess:hover, .stWarning:hover, .stError:hover, .stInfo:hover {
            transform: translateX(10px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
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
        
        /* Interactive buttons */
        .stButton > button {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.1) 0%, 
                rgba(118, 75, 162, 0.1) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, 
                rgba(255, 255, 255, 0.2) 0%, 
                transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.5s ease, height 0.5s ease;
        }
        
        .stButton > button:hover::before {
            width: 300%;
            height: 300%;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 
                0 10px 30px rgba(102, 126, 234, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.1);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        /* Accept button special styling */
        .stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            font-size: 1.2rem;
            padding: 1rem 3rem;
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        .stButton > button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
        }
        
        /* Enhanced text highlighting */
        strong {
            color: #ffffff !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            position: relative;
            display: inline-block;
        }
        
        strong:hover {
            text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
            transform: scale(1.05);
        }
        
        /* Smooth scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.4) 0%, 
                rgba(118, 75, 162, 0.4) 100%);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.6) 0%, 
                rgba(118, 75, 162, 0.6) 100%);
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .social-pill:hover {
                transform: scale(1.1) rotate(0deg);
            }
            
            .disclaimer-container {
                padding: 2rem;
                margin: 1rem;
            }
        }
        
        /* Performance optimizations */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        div[data-testid="stVerticalBlock"] > div {
            animation: fadeIn 0.5s ease-out;
            animation-fill-mode: both;
        }
        
        div[data-testid="stVerticalBlock"] > div:nth-child(1) { animation-delay: 0.1s; }
        div[data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 0.2s; }
        div[data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 0.3s; }
        div[data-testid="stVerticalBlock"] > div:nth-child(4) { animation-delay: 0.4s; }
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
    except (json.JSONDecodeError, TypeError):
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
    """Create image gallery HTML"""
    gallery_html = '<div style="display: flex; gap: 1.5rem; align-items: center; justify-content: center; margin-bottom: 2rem;">'
    
    # Main photo
    gallery_html += '<div style="flex: 0 0 auto;">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" style="width: 200px; height: 250px; object-fit: cover; border-radius: 12px; border: 2px solid rgba(102, 126, 234, 0.3);">'
    else:
        gallery_html += '<div style="width: 200px; height: 250px; background: rgba(102, 126, 234, 0.1); display: flex; align-items: center; justify-content: center; color: #94a3b8; border-radius: 12px; border: 2px solid rgba(102, 126, 234, 0.3);">👤<br>Sin Foto</div>'
    gallery_html += '</div>'
    
    # Badges
    gallery_html += '<div style="display: flex; flex-direction: column; gap: 1rem; align-items: center;">'
    
    # Party logo
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" style="width: 120px; height: 120px; object-fit: contain; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px;">'
    
    # Seat indicator
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" style="width: 120px; height: 120px; object-fit: contain; background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 10px;">'
    
    gallery_html += '</div></div>'
    return gallery_html

def show_disclaimer():
    """Show the legal disclaimer page"""
    apply_css()
    
    # Center the disclaimer
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="disclaimer-container">
            <h1 class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD</h1>
            <div class="disclaimer-text">
                <p>Esta aplicación recopila y organiza información pública disponible en la página web del Congreso de los Diputados, incluyendo documentos en formato PDF. La aplicación no pertenece ni está vinculada de ninguna manera al Congreso de los Diputados, ni cuenta con su aval, autorización o patrocinio.</p>
                
                <p>El contenido mostrado se ofrece únicamente con fines informativos y de acceso público. Aunque se procura garantizar la precisión y actualización de los datos, <strong>la aplicación puede contener errores, inexactitudes u omisiones, así como información incompleta o desactualizada</strong>. Para la consulta oficial, íntegra y auténtica de los documentos, se recomienda acudir directamente a la página web del Congreso de los Diputados.</p>
                
                <p>El uso de esta aplicación es responsabilidad exclusiva del usuario.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Accept button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()

def main_app():
    """Main application"""
    apply_css()
    
    st.markdown('<h1 style="text-align: center;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Get unique deputies by name (they might have multiple declarations)
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Search bar
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado por nombre...")
    
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
                
                # Create a clean label without showing the actual filename
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
            # Image gallery
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
            
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Ingresos Anuales", format_currency(total_salary), f"{tax_rate:.1f}% IRPF")
            with m_col2:
                st.metric("Patrimonio Declarado", f"{total_properties + vehicles_count} Activos", f"{total_properties} Inmuebles")
            with m_col3:
                st.metric("Deuda Pendiente", format_currency(total_debt), f"{len(debts)} Préstamos")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tabs with all information
            tabs = st.tabs([
                "💵 Ingresos", 
                "🏠 Inmuebles", 
                "💼 Sociedades",
                "💰 Activos",
                "🚗 Vehículos",
                "💳 Deudas",
                "📊 Análisis",
                "📄 Otros"
            ])
            
            # TAB 1: INGRESOS
            with tabs[0]:
                st.markdown("#### 💵 Todas las Fuentes de Ingresos")
                
                if total_salary > 0:
                    st.success(f"💰 **Total Anual: {format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"📋 **IRPF Pagado: {format_currency_full(irpf)}** (Tipo efectivo: {tax_rate:.2f}%)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 💼 Salarios")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                concepto = salary.get('concepto', f'Ingreso #{i+1}')
                                if pd.isna(concepto): concepto = f'Ingreso #{i+1}'
                                amount = extract_currency_value(salary.get('euros'))
                                st.markdown(f"**{concepto}**: {format_currency_full(amount)}")
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
                                if pd.isna(concepto): concepto = 'Inversión'
                                rendimientos = extract_currency_value(div.get('euros'))
                                st.markdown(f"**{concepto}**: {format_currency_full(rendimientos)}")
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
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                            st.success(f"💰 **Total en Cuentas: {format_currency_full(total_accounts)}**")
                        
                        for account in accounts:
                            if isinstance(account, dict):
                                desc = account.get('descripcion', 'Cuenta')
                                if pd.isna(desc): desc = 'Cuenta'
                                saldo = extract_currency_value(account.get('saldo'))
                                if saldo > 0:
                                    st.markdown(f"**{desc}**: {format_currency_full(saldo)}")
                    else:
                        st.info("Sin cuentas declaradas")
                    
                    st.markdown("##### 📈 Acciones y Participaciones")
                    acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                    if acciones:
                        for i, accion in enumerate(acciones):
                            if isinstance(accion, dict):
                                st.markdown(f"**📊 Acción/Participación #{i+1}**")
                                for key, value in accion.items():
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
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
                                if pd.isna(desc): desc = f'Vehículo #{i+1}'
                                st.markdown(f"**🚗 {desc}**")
                                
                                fecha = vehicle.get('fecha_adquisicion', '')
                                if pd.notna(fecha):
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;• Adquirido: {fecha}")
                                st.markdown("<br>", unsafe_allow_html=True)
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
                            if pd.isna(desc): desc = f'Deuda #{i+1}'
                            st.markdown(f"**📄 {desc}**")
                            
                            original = extract_currency_value(debt.get('importe_concedido'))
                            pending = extract_currency_value(debt.get('saldo_pendiente'))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if original > 0:
                                    st.markdown(f"**Importe Original:** {format_currency_full(original)}")
                                if pending > 0:
                                    st.markdown(f"**Saldo Pendiente:** {format_currency_full(pending)}")
                            
                            with col2:
                                fecha = debt.get('fecha_concesion', '')
                                if pd.notna(fecha):
                                    st.markdown(f"**Fecha:** {fecha}")
                                if original > 0 and pending > 0:
                                    paid_pct = max(0, ((original - pending) / original) * 100)
                                    st.progress(int(paid_pct), text=f"Amortizado al {paid_pct:.1f}%")
                            st.markdown("---")
                else:
                    st.success("✅ No se han declarado deudas")
            
            # TAB 7: ANÁLISIS
            with tabs[6]:
                st.markdown("#### 📊 Análisis Financiero")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    accounts_total = sum(extract_currency_value(a.get('saldo', 0)) 
                                       for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']) 
                                       if isinstance(a, dict))
                    
                    # Estimate property value if not specified
                    estimated_prop_value = total_properties * 150000
                    estimated_vehicle_value = vehicles_count * 15000

                    patrimony_data = {
                        'Activo': ['Depósitos', 'Inmuebles (est.)', 'Vehículos (est.)'],
                        'Valor': [accounts_total, estimated_prop_value, estimated_vehicle_value]
                    }
                    df_patrimony = pd.DataFrame(patrimony_data).query('Valor > 0')

                    if not df_patrimony.empty:
                        fig = px.pie(df_patrimony, values='Valor', names='Activo', 
                                     title='Distribución de Patrimonio Declarado (Estimado)', hole=.4,
                                     color_discrete_sequence=px.colors.sequential.Purples_r)
                        fig.update_layout(
                            showlegend=True,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No hay suficientes datos para generar el gráfico de patrimonio.")
                
                with col2:
                    fig2 = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=tax_rate,
                        number={'suffix': "%", 'valueformat': ".2f"},
                        title={'text': "Tipo Impositivo Efectivo (IRPF)"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 20], 'color': "rgba(102, 126, 234, 0.2)"},
                                {'range': [20, 35], 'color': "rgba(102, 126, 234, 0.4)"},
                            ]
                        }
                    ))
                    fig2.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=350,
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            # TAB 8: OTROS
            with tabs[7]:
                st.markdown("#### 📄 Otros Bienes y Derechos")
                
                otros_bienes = deputy_data.get('otros_bienes_no_declarados_anteriormente', '')
                if otros_bienes and pd.notna(otros_bienes):
                    st.markdown("##### 📦 Otros Bienes No Declarados Anteriormente")
                    
                    otros_parsed = parse_json_field(otros_bienes)
                    if otros_parsed:
                        for i, item in enumerate(otros_parsed):
                            if isinstance(item, dict):
                                st.markdown(f"**Item #{i+1}**")
                                for key, value in item.items():
                                    if pd.notna(value):
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"&nbsp;&nbsp;&nbsp;• **{key_formatted}:** {value}")
                                st.markdown("---")
                    else:
                        st.write(otros_bienes)
                else:
                    st.info("No hay otros bienes declarados en esta sección")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
