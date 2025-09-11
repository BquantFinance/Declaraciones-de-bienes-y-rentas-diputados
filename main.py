import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64
import time

# Page configuration
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if 'animation_played' not in st.session_state:
    st.session_state.animation_played = False

# Enhanced CSS with animations and effects
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Variables */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --dark-bg: linear-gradient(135deg, #1e1e3f 0%, #2d2d5f 50%, #1a1a2e 100%);
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(102, 126, 234, 0.2);
            --text-primary: #ffffff;
            --text-secondary: #b8bcc8;
            --accent: #667eea;
        }
        
        /* Main App Background */
        .stApp {
            background: var(--dark-bg);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated background particles */
        .stApp::before {
            content: '';
            position: fixed;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(240, 147, 251, 0.1) 0%, transparent 50%);
            animation: floatBackground 20s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        @keyframes floatBackground {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(-20px, -20px) rotate(1deg); }
            66% { transform: translate(20px, -10px) rotate(-1deg); }
        }
        
        /* Container settings */
        .main .block-container {
            padding-top: 2rem;
            max-width: 1600px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        /* Animated Header */
        .main-header {
            text-align: center;
            margin-bottom: 3rem;
            animation: slideDown 0.8s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .main-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 3s ease infinite;
            filter: drop-shadow(0 0 30px rgba(102, 126, 234, 0.5));
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.8;
        }
        
        /* Disclaimer Container Enhanced */
        .disclaimer-container {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
            backdrop-filter: blur(20px);
            border: 2px solid var(--card-border);
            border-radius: 30px;
            padding: 4rem 3rem;
            margin: 3rem auto;
            max-width: 900px;
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            animation: fadeInScale 0.8s ease-out;
            position: relative;
            overflow: hidden;
        }
        
        .disclaimer-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes fadeInScale {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .disclaimer-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b 0%, #ff8e53 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            z-index: 1;
        }
        
        .disclaimer-text {
            color: #e0e0e0;
            font-size: 1.1rem;
            line-height: 1.8;
            text-align: justify;
            position: relative;
            z-index: 1;
        }
        
        .disclaimer-text p {
            margin-bottom: 1.2rem;
            animation: fadeInUp 0.6s ease-out backwards;
        }
        
        .disclaimer-text p:nth-child(1) { animation-delay: 0.2s; }
        .disclaimer-text p:nth-child(2) { animation-delay: 0.4s; }
        .disclaimer-text p:nth-child(3) { animation-delay: 0.6s; }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Deputy Photo Enhanced */
        .deputy-photo-container {
            position: relative;
            display: inline-block;
            margin: 0 auto;
        }
        
        .deputy-photo {
            border-radius: 20px;
            border: 3px solid transparent;
            background: linear-gradient(white, white) padding-box,
                        var(--primary-gradient) border-box;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.4),
                0 0 60px rgba(102, 126, 234, 0.3);
            width: 250px;
            height: 300px;
            object-fit: cover;
            transition: all 0.4s ease;
            animation: photoFloat 3s ease-in-out infinite;
        }
        
        @keyframes photoFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .deputy-photo:hover {
            transform: scale(1.05);
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.5),
                0 0 80px rgba(102, 126, 234, 0.5);
        }
        
        .no-photo {
            background: var(--primary-gradient);
            border-radius: 20px;
            width: 250px;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 5rem;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.4),
                0 0 60px rgba(102, 126, 234, 0.3);
            animation: photoFloat 3s ease-in-out infinite;
        }
        
        /* Party Logo Badge */
        .party-logo {
            position: absolute;
            bottom: -20px;
            right: -20px;
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
            padding: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: bounceIn 0.6s ease-out 0.5s backwards;
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        /* Info Cards Enhanced */
        .info-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: fadeInLeft 0.6s ease-out backwards;
        }
        
        .info-card:nth-child(1) { animation-delay: 0.1s; }
        .info-card:nth-child(2) { animation-delay: 0.2s; }
        .info-card:nth-child(3) { animation-delay: 0.3s; }
        .info-card:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .info-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .info-card:hover::before {
            left: 100%;
        }
        
        .info-card:hover {
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
            border-color: var(--accent);
        }
        
        .info-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 0.5rem;
            opacity: 0.7;
        }
        
        .info-value {
            color: var(--text-primary);
            font-size: 1.3rem;
            font-weight: 500;
        }
        
        /* Social Links Enhanced */
        .social-container {
            display: flex;
            gap: 1.2rem;
            margin: 2rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .social-link {
            background: var(--primary-gradient);
            border-radius: 50%;
            width: 70px;
            height: 70px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 1.8rem;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            animation: socialPop 0.6s ease-out backwards;
        }
        
        .social-link:nth-child(1) { animation-delay: 0.1s; }
        .social-link:nth-child(2) { animation-delay: 0.2s; }
        .social-link:nth-child(3) { animation-delay: 0.3s; }
        .social-link:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes socialPop {
            0% {
                opacity: 0;
                transform: scale(0);
            }
            80% {
                transform: scale(1.1);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .social-link::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.4s, height 0.4s;
        }
        
        .social-link:hover::before {
            width: 100px;
            height: 100px;
        }
        
        .social-link:hover {
            transform: translateY(-10px) rotate(360deg) scale(1.2);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.5);
        }
        
        /* Metrics Cards Enhanced */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.08) 100%);
            border: 2px solid var(--card-border);
            border-radius: 20px;
            padding: 1.8rem;
            box-shadow: 
                0 10px 40px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            animation: metricSlide 0.6s ease-out backwards;
        }
        
        [data-testid="metric-container"]:nth-child(1) { animation-delay: 0.1s; }
        [data-testid="metric-container"]:nth-child(2) { animation-delay: 0.2s; }
        [data-testid="metric-container"]:nth-child(3) { animation-delay: 0.3s; }
        [data-testid="metric-container"]:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes metricSlide {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        [data-testid="metric-container"]::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
            animation: rotate 10s linear infinite;
        }
        
        [data-testid="metric-container"]:hover::after {
            opacity: 1;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 
                0 20px 60px rgba(102, 126, 234, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: var(--accent);
        }
        
        [data-testid="metric-container"] label {
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            opacity: 0.8;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            font-size: 2.2rem !important;
            text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            animation: pulseValue 2s ease-in-out infinite;
        }
        
        @keyframes pulseValue {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Search Input Enhanced */
        .stTextInput > div > div > input {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
            border: 2px solid var(--card-border) !important;
            border-radius: 50px !important;
            color: var(--text-primary) !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent) !important;
            box-shadow: 
                0 0 0 4px rgba(102, 126, 234, 0.2),
                0 10px 30px rgba(102, 126, 234, 0.3) !important;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
            transform: translateY(-2px) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: var(--text-secondary) !important;
            opacity: 0.6 !important;
        }
        
        /* Selectbox Enhanced */
        .stSelectbox > div > div {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
            border: 2px solid var(--card-border) !important;
            border-radius: 15px !important;
            color: var(--text-primary) !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: var(--accent) !important;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3) !important;
        }
        
        /* Button Enhanced */
        .stButton > button {
            background: var(--primary-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 1rem 3rem !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
            box-shadow: 
                0 10px 30px rgba(102, 126, 234, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 100% !important;
            height: 100% !important;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent) !important;
            transition: left 0.5s !important;
        }
        
        .stButton > button:hover::before {
            left: 100% !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 
                0 20px 40px rgba(102, 126, 234, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        }
        
        /* Accept button pulse animation */
        .stButton > button[type="submit"] {
            background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
            animation: pulse 2s infinite !important;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { box-shadow: 0 0 0 20px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        
        /* Tabs Enhanced */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border-radius: 15px;
            padding: 0.5rem;
            gap: 0.5rem;
            border: 1px solid var(--card-border);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-secondary) !important;
            background: transparent !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stTabs [data-baseweb="tab"]::before {
            content: '' !important;
            position: absolute !important;
            bottom: 0 !important;
            left: 50% !important;
            width: 0 !important;
            height: 3px !important;
            background: var(--primary-gradient) !important;
            transform: translateX(-50%) !important;
            transition: width 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-primary) !important;
            background: rgba(102, 126, 234, 0.1) !important;
            transform: translateY(-2px) !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover::before {
            width: 100% !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary-gradient) !important;
            color: white !important;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
            transform: scale(1.05) !important;
        }
        
        /* Success/Warning/Error/Info Enhanced */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 15px !important;
            padding: 1.2rem !important;
            font-weight: 500 !important;
            border-left: 4px solid !important;
            animation: slideInRight 0.5s ease-out !important;
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .stSuccess {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
            border-left-color: #10b981 !important;
        }
        
        .stWarning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%) !important;
            border-left-color: #f59e0b !important;
        }
        
        .stError {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
            border-left-color: #ef4444 !important;
        }
        
        .stInfo {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%) !important;
            border-left-color: #3b82f6 !important;
        }
        
        /* Divider Enhanced */
        hr {
            border: none !important;
            height: 2px !important;
            background: var(--primary-gradient) !important;
            margin: 3rem 0 !important;
            position: relative !important;
            opacity: 0.5 !important;
        }
        
        hr::before {
            content: '◆' !important;
            position: absolute !important;
            left: 50% !important;
            top: 50% !important;
            transform: translate(-50%, -50%) !important;
            background: #1e1e3f !important;
            color: var(--accent) !important;
            padding: 0 1rem !important;
            font-size: 1.5rem !important;
        }
        
        /* Scrollbar Enhanced */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary-gradient);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-gradient);
        }
        
        /* Loading animation */
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-title { font-size: 2.5rem; }
            .social-link { width: 60px; height: 60px; }
            .deputy-photo { width: 200px; height: 250px; }
            .info-card { padding: 1rem; }
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    try:
        if not os.path.exists('deputies_full_dataset.csv'):
            st.error("⚠️ No se encontró el archivo 'deputies_full_dataset.csv'")
            return pd.DataFrame()
        
        df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
        
        # Clean path columns
        path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
        for col in path_columns:
            if col in df.columns:
                df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value in ('[]', ''):
        return []
    try:
        if isinstance(field_value, str):
            cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', field_value)
            return json.loads(cleaned_value)
        return []
    except:
        return []

def format_currency(value):
    """Format currency values for display"""
    if not isinstance(value, (int, float)):
        return "0€"
    
    if value >= 1000000:
        return f"{value/1000000:.1f}M€"
    elif value >= 1000:
        return f"{value/1000:.0f}K€"
    else:
        return f"{int(value)}€"

def format_currency_full(value):
    """Format currency values for detailed display"""
    if not isinstance(value, (int, float)):
        return "0 €"
    
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
        except:
            return 0
    return 0

def create_deputy_photo_section(deputy_data):
    """Create enhanced deputy photo section with party logo"""
    photo_html = '<div class="deputy-photo-container">'
    
    # Main photo
    photo_path = deputy_data.get('photo_path', '')
    try:
        if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
            with open(photo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                photo_html += f'<img src="data:image/jpeg;base64,{img_data}" class="deputy-photo">'
        else:
            photo_html += '<div class="no-photo">👤</div>'
    except:
        photo_html += '<div class="no-photo">👤</div>'
    
    # Party logo badge
    logo_path = deputy_data.get('logo_path', '')
    try:
        if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
            with open(logo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                photo_html += f'<img src="data:image/png;base64,{img_data}" class="party-logo">'
    except:
        pass
    
    photo_html += '</div>'
    return photo_html

def create_social_links(deputy_data):
    """Create enhanced social media links"""
    social_html = '<div class="social-container">'
    
    social_map = {
        'twitter': ('𝕏', 'X (Twitter)'),
        'facebook': ('📘', 'Facebook'),
        'instagram': ('📸', 'Instagram'),
        'website': ('🌐', 'Sitio Web')
    }
    
    for field, (emoji, title) in social_map.items():
        url = deputy_data.get(field, '')
        if pd.notna(url) and str(url).lower() != 'nan':
            social_html += f'<a href="{url}" target="_blank" class="social-link" title="{title}">{emoji}</a>'
    
    social_html += '</div>'
    return social_html

def show_disclaimer():
    """Show enhanced disclaimer page"""
    apply_css()
    
    # Loading animation
    if not st.session_state.animation_played:
        placeholder = st.empty()
        placeholder.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
        time.sleep(1)
        placeholder.empty()
        st.session_state.animation_played = True
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <div class="disclaimer-container">
            <h1 class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD</h1>
            <div class="disclaimer-text">
                <p>Esta aplicación recopila y organiza información pública disponible en la página web del Congreso de los Diputados, incluyendo documentos en formato PDF. La aplicación no pertenece ni está vinculada de ninguna manera al Congreso de los Diputados, ni cuenta con su aval, autorización o patrocinio.</p>
                
                <p>El contenido mostrado se ofrece únicamente con fines informativos y de acceso público. Aunque se procura garantizar la precisión y actualización de los datos, <strong>la aplicación puede contener errores, inexactitudes u omisiones</strong>, así como información incompleta o desactualizada.</p>
                
                <p>El uso de esta aplicación es responsabilidad exclusiva del usuario.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("✅ **ACEPTO Y ENTIENDO**", type="primary", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()

def main_app():
    """Main application with enhanced UI"""
    apply_css()
    
    # Animated header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">⚖️ Registro de Diputados</h1>
            <p class="subtitle">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>
        </div>
    """, unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Verify required columns
    if 'informacion_personal_nombre_y_apellidos' not in df.columns:
        st.error("El archivo CSV no tiene el formato esperado")
        st.stop()
    
    # Get unique deputies
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Enhanced search section
    col1, col2 = st.columns([5, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            placeholder="🔍 Buscar diputado por nombre...",
            key="search",
            label_visibility="collapsed"
        )
    
    # Filter deputies
    filtered_deputies = unique_deputies.copy()
    if search_term:
        filtered_deputies = filtered_deputies[
            filtered_deputies['informacion_personal_nombre_y_apellidos'].str.contains(
                search_term, case=False, na=False
            )
        ]
    
    with col2:
        st.metric("**DIPUTADOS**", f"{len(filtered_deputies)}", delta=f"de {len(unique_deputies)} total")
    
    st.markdown("---")
    
    if len(filtered_deputies) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
        return
    
    # Deputy selector
    selected_deputy_name = st.selectbox(
        "**👤 Seleccionar Diputado:**",
        filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist(),
        format_func=lambda x: f"📌 {x}"
    )
    
    # Get all declarations for selected deputy
    deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
    
    # If multiple declarations, let user choose
    if len(deputy_declarations) > 1:
        st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
        
        declaration_options = []
        for idx, row in deputy_declarations.iterrows():
            fecha = row.get('informacion_personal_fecha_eleccion', '')
            label = f"📄 Declaración {idx - deputy_declarations.index[0] + 1}"
            if fecha and str(fecha).lower() != 'nan':
                label += f" - {fecha}"
            declaration_options.append((idx, label))
        
        selected_idx = st.selectbox(
            "**Seleccionar Declaración:**",
            [opt[0] for opt in declaration_options],
            format_func=lambda x: next(opt[1] for opt in declaration_options if opt[0] == x)
        )
        
        deputy_data = deputy_declarations.loc[selected_idx]
    else:
        deputy_data = deputy_declarations.iloc[0]
    
    st.markdown("---")
    
    # Main layout with enhanced styling
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        # Enhanced deputy photo section
        st.markdown(create_deputy_photo_section(deputy_data), unsafe_allow_html=True)
        
        # Personal information with animation
        st.markdown("### 📋 Información Personal")
        
        info_fields = [
            ('📍 CARGO', deputy_data.get('informacion_personal_cargo', 'Diputado')),
            ('🏛️ CIRCUNSCRIPCIÓN', deputy_data.get('informacion_personal_circunscripcion', '')),
            ('💑 ESTADO CIVIL', deputy_data.get('informacion_personal_estado_civil', '')),
            ('📅 FECHA ELECCIÓN', deputy_data.get('informacion_personal_fecha_eleccion', '')),
            ('📜 PRESENTACIÓN CREDENCIAL', deputy_data.get('informacion_personal_fecha_presentacion_credencial', '')),
        ]
        
        for label, value in info_fields:
            if value and str(value).lower() != 'nan':
                st.markdown(f"""
                <div class="info-card">
                    <div class="info-label">{label}</div>
                    <div class="info-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Social media with enhanced effects
        st.markdown("### 🌐 Redes Sociales")
        st.markdown(create_social_links(deputy_data), unsafe_allow_html=True)
    
    with col_right:
        # Deputy name with gradient
        st.markdown(f"""
            <h2 style="background: var(--primary-gradient); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-size: 2.5rem;
                       font-weight: 700;">
                👤 {deputy_data['informacion_personal_nombre_y_apellidos']}
            </h2>
        """, unsafe_allow_html=True)
        
        # Calculate financial metrics
        salaries = parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales', '[]'))
        total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in salaries if isinstance(s, dict))
        
        irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
        tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
        
        vehicles = parse_json_field(deputy_data.get('vehiculos', '[]'))
        vehicles_count = len(vehicles)
        
        urban_properties = len(parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos', '[]')))
        rustic_properties = len(parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]')))
        total_properties = urban_properties + rustic_properties
        
        debts = parse_json_field(deputy_data.get('deudas_y_obligaciones', '[]'))
        total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
        
        # Enhanced financial summary with animations
        st.markdown("### 💰 Resumen Financiero")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💵 **INGRESOS**", 
                format_currency(total_salary),
                delta=f"IRPF: {format_currency(irpf)}" if irpf > 0 else None
            )
        
        with col2:
            st.metric(
                "🏠 **PATRIMONIO**", 
                f"{total_properties}",
                delta=f"Inmuebles: {total_properties}" if total_properties > 0 else None
            )
        
        with col3:
            st.metric(
                "🚗 **VEHÍCULOS**", 
                f"{vehicles_count}",
                delta="Declarados" if vehicles_count > 0 else None
            )
        
        with col4:
            st.metric(
                "💳 **DEUDAS**", 
                format_currency(total_debt),
                delta="Sin deudas" if total_debt == 0 else f"{len(debts)} activas",
                delta_color="inverse"
            )
        
        st.markdown("---")
        
        # Enhanced tabs with icons
        tabs = st.tabs([
            "💵 Ingresos",
            "🏠 Inmuebles", 
            "🚗 Vehículos",
            "💼 Sociedades",
            "🔥 Activos",
            "💳 Deudas",
            "📊 Análisis",
            "📝 Otros"
        ])
        
        # TAB 1: INGRESOS
        with tabs[0]:
            st.markdown("#### 💰 Todas las Fuentes de Ingresos")
            
            if total_salary > 0:
                st.success(f"💵 **Total Anual:** {format_currency_full(total_salary)}")
                if irpf > 0:
                    st.info(f"📋 **IRPF Pagado:** {format_currency_full(irpf)} • **Tipo:** {tax_rate:.2f}%")
            
            if salaries:
                for i, salary in enumerate(salaries[:10]):
                    if isinstance(salary, dict):
                        concepto = salary.get('concepto', f'Ingreso {i+1}')
                        amount = extract_currency_value(salary.get('euros'))
                        if amount > 100000:
                            st.error(f"💰 **{concepto}**: {format_currency_full(amount)}")
                        elif amount > 50000:
                            st.warning(f"💰 **{concepto}**: {format_currency_full(amount)}")
                        else:
                            st.info(f"💰 **{concepto}**: {format_currency_full(amount)}")
            else:
                st.info("Sin salarios declarados")
        
        # TAB 2: INMUEBLES
        with tabs[1]:
            st.markdown("#### 🏠 Bienes Inmuebles")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**🏢 Inmuebles Urbanos:** {urban_properties}")
                urban = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos', '[]'))
                for i, prop in enumerate(urban[:5]):
                    if isinstance(prop, dict):
                        st.write(f"📍 Inmueble urbano #{i+1}")
            
            with col2:
                st.markdown(f"**🌾 Inmuebles Rústicos:** {rustic_properties}")
                rustic = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))
                for i, prop in enumerate(rustic[:5]):
                    if isinstance(prop, dict):
                        st.write(f"🚜 Inmueble rústico #{i+1}")
        
        # TAB 3: VEHÍCULOS
        with tabs[2]:
            st.markdown("#### 🚗 Vehículos")
            
            if vehicles:
                st.success(f"🚙 **Total vehículos:** {vehicles_count}")
                for i, vehicle in enumerate(vehicles[:10]):
                    if isinstance(vehicle, dict):
                        desc = vehicle.get('descripcion', f'Vehículo {i+1}')
                        fecha = vehicle.get('fecha_adquisicion', '')
                        if fecha and str(fecha).lower() != 'nan':
                            st.write(f"🚗 **{desc}** • Adquirido: {fecha}")
                        else:
                            st.write(f"🚗 **{desc}**")
            else:
                st.info("No hay vehículos declarados")
        
        # TAB 4: SOCIEDADES
        with tabs[3]:
            st.markdown("#### 💼 Sociedades y Participaciones")
            
            sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', '[]'))
            participaciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', '[]'))
            
            col1, col2 = st.columns(2)
            
            with col1:
                if sociedades:
                    st.warning(f"🏢 **Sociedades no cotizadas:** {len(sociedades)}")
                    for i, soc in enumerate(sociedades[:5]):
                        if isinstance(soc, dict):
                            st.write(f"• Sociedad #{i+1}")
                else:
                    st.info("Sin sociedades no cotizadas")
            
            with col2:
                if participaciones:
                    st.warning(f"📊 **Participaciones >5%:** {len(participaciones)}")
                    for i, part in enumerate(participaciones[:5]):
                        if isinstance(part, dict):
                            st.write(f"• Participación #{i+1}")
                else:
                    st.info("Sin participaciones superiores al 5%")
        
        # TAB 5: ACTIVOS
        with tabs[4]:
            st.markdown("#### 💰 Activos Financieros")
            
            accounts = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas', '[]'))
            if accounts:
                total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                st.success(f"🏦 **Total en cuentas:** {format_currency_full(total_accounts)}")
                
                for account in accounts[:5]:
                    if isinstance(account, dict):
                        desc = account.get('descripcion', 'Cuenta')
                        saldo = extract_currency_value(account.get('saldo'))
                        if saldo > 0:
                            st.write(f"💳 **{desc}**: {format_currency_full(saldo)}")
            else:
                st.info("Sin cuentas declaradas")
        
        # TAB 6: DEUDAS
        with tabs[5]:
            st.markdown("#### 💳 Deudas y Obligaciones")
            
            if debts:
                st.error(f"💸 **Total pendiente:** {format_currency_full(total_debt)}")
                for i, debt in enumerate(debts[:5]):
                    if isinstance(debt, dict):
                        desc = debt.get('descripcion', f'Deuda {i+1}')
                        pending = extract_currency_value(debt.get('saldo_pendiente'))
                        original = extract_currency_value(debt.get('importe_concedido'))
                        
                        if original > 0 and pending > 0:
                            paid_pct = ((original - pending) / original) * 100
                            st.write(f"📄 **{desc}**")
                            st.progress(paid_pct / 100)
                            st.write(f"Pendiente: **{format_currency_full(pending)}** • Pagado: {paid_pct:.1f}%")
            else:
                st.success("✅ No hay deudas declaradas")
        
        # TAB 7: ANÁLISIS
        with tabs[6]:
            st.markdown("#### 📊 Análisis Visual")
            
            # Enhanced pie chart
            if total_salary > 0 or total_properties > 0 or vehicles_count > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Ingresos', 'Propiedades (est.)', 'Vehículos (est.)', 'Cuentas'],
                    values=[
                        total_salary,
                        total_properties * 150000,
                        vehicles_count * 20000,
                        sum(extract_currency_value(a.get('saldo', 0)) 
                            for a in parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas', '[]'))
                            if isinstance(a, dict))
                    ],
                    hole=.5,
                    marker=dict(
                        colors=['#667eea', '#764ba2', '#f093fb', '#f5576c'],
                        line=dict(color='#1e1e3f', width=2)
                    )
                )])
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value:,.0f}€<br>%{percent}<extra></extra>'
                )
                
                fig.update_layout(
                    title=dict(
                        text="Distribución Patrimonial Estimada",
                        font=dict(size=20, color='white')
                    ),
                    showlegend=True,
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=14),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(size=12)
                    ),
                    margin=dict(t=50, b=0, l=0, r=150),
                    annotations=[
                        dict(
                            text=f"Total<br>{format_currency(total_salary + total_properties*150000 + vehicles_count*20000)}",
                            x=0.5, y=0.5,
                            font_size=16,
                            showarrow=False
                        )
                    ]
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tax gauge chart
                if tax_rate > 0:
                    fig2 = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=tax_rate,
                        number={'suffix': "%", 'valueformat': ".2f"},
                        delta={'reference': 25, 'relative': False},
                        title={'text': "Tipo Impositivo IRPF"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 50]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 15], 'color': "rgba(102, 126, 234, 0.1)"},
                                {'range': [15, 30], 'color': "rgba(102, 126, 234, 0.2)"},
                                {'range': [30, 50], 'color': "rgba(102, 126, 234, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 45
                            }
                        }
                    ))
                    
                    fig2.update_layout(
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white', size=14)
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No hay suficientes datos para generar el análisis visual")
        
        # TAB 8: OTROS
        with tabs[7]:
            st.markdown("#### 📝 Otros Bienes y Derechos")
            
            otros_bienes = deputy_data.get('otros_bienes_no_declarados_anteriormente', '')
            observaciones = deputy_data.get('observaciones', '')
            
            if otros_bienes and str(otros_bienes).lower() != 'nan':
                st.markdown("**📦 Otros Bienes:**")
                st.write(otros_bienes)
            
            if observaciones and str(observaciones).lower() != 'nan':
                st.markdown("**📝 Observaciones:**")
                st.info(observaciones)
            
            if not (otros_bienes and str(otros_bienes).lower() != 'nan') and not (observaciones and str(observaciones).lower() != 'nan'):
                st.info("No hay información adicional declarada")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
