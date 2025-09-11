import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os

# Page configuration
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced modern dark theme with advanced CSS effects
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* CSS Variables for easy theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --dark-gradient: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
        --card-gradient: linear-gradient(135deg, rgba(30, 30, 60, 0.7) 0%, rgba(20, 20, 40, 0.9) 100%);
        --hover-scale: 1.02;
        --transition-speed: 0.3s;
        --glow-color: rgba(102, 126, 234, 0.6);
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Main App Styling with animated gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        position: relative;
        overflow-x: hidden;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animated particles background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(245, 87, 108, 0.05) 0%, transparent 50%);
        animation: floatingBubbles 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 1;
    }
    
    @keyframes floatingBubbles {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -30px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
    }
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1600px;
        position: relative;
        z-index: 2;
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
    
    /* Typography with text shadows */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        animation: titleGlow 3s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
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
    }
    
    /* Deputy Card with advanced effects */
    .deputy-card {
        background: linear-gradient(135deg, rgba(30, 30, 60, 0.7) 0%, rgba(20, 20, 40, 0.9) 100%);
        border-radius: 24px;
        padding: 2.5rem;
        border: 2px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(12px);
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-top: 1rem;
        position: relative;
        overflow: hidden;
        animation: cardEntrance 0.6s ease-out;
    }
    
    @keyframes cardEntrance {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .deputy-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(102, 126, 234, 0.1),
            transparent
        );
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Image Gallery with hover effects */
    .image-gallery {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
        align-items: center;
        justify-content: center;
        animation: fadeIn 1s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .main-image-container {
        position: relative;
        flex: 0 0 auto;
        transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .main-image-container:hover {
        transform: scale(1.05) rotate(2deg);
    }
    
    .main-image {
        width: 220px;
        height: 280px;
        object-fit: cover;
        border-radius: 15px;
        box-shadow: 
            0 8px 32px rgba(102, 126, 234, 0.3),
            0 0 80px rgba(102, 126, 234, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.3);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .main-image:hover {
        box-shadow: 
            0 12px 40px rgba(102, 126, 234, 0.5),
            0 0 120px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    .badge-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: center;
        justify-content: center;
    }
    
    .party-logo, .seat-indicator {
        width: 140px;
        height: 140px;
        object-fit: contain;
        padding: 15px;
        border-radius: 12px;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
    }
    
    .party-logo {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .seat-indicator {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .party-logo:hover, .seat-indicator:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 
            0 10px 30px rgba(102, 126, 234, 0.4),
            inset 0 0 20px rgba(102, 126, 234, 0.1);
    }
    
    /* Info Grid with stagger animation */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    
    .info-item {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: slideInLeft 0.6s ease-out backwards;
    }
    
    .info-item:nth-child(1) { animation-delay: 0.1s; }
    .info-item:nth-child(2) { animation-delay: 0.2s; }
    .info-item:nth-child(3) { animation-delay: 0.3s; }
    .info-item:nth-child(4) { animation-delay: 0.4s; }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .info-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .info-item:hover::before {
        left: 100%;
    }
    
    .info-item:hover {
        transform: translateY(-3px) scale(1.02);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 
            0 6px 20px rgba(102, 126, 234, 0.2),
            inset 0 0 15px rgba(102, 126, 234, 0.05);
    }
    
    .info-label {
        font-size: 0.8rem;
        color: #b4bdc8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .info-value {
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Enhanced Metrics with pulse effect */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.2) 0%, transparent 70%);
        transform: translate(-50%, -50%) scale(0);
        transition: transform 0.5s ease;
    }
    
    [data-testid="metric-container"]:hover::after {
        transform: translate(-50%, -50%) scale(2);
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.3),
            inset 0 0 30px rgba(102, 126, 234, 0.05);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: valueGlow 2s ease-in-out infinite;
    }
    
    @keyframes valueGlow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    /* Tabs with sliding indicator */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 30, 60, 0.3);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        position: relative;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        padding: 0 20px;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 2;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        color: #ffffff !important;
        font-weight: 600;
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 10%;
        right: 10%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        animation: tabGlow 1.5s ease-in-out infinite;
    }
    
    @keyframes tabGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    /* Social Media Pills with bounce effect */
    .social-pills {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }
    
    .social-pill {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 2px solid rgba(102, 126, 234, 0.3);
        width: 55px;
        height: 55px;
        border-radius: 50%;
        font-size: 1.6rem;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #ffffff;
        font-weight: bold;
        position: relative;
        overflow: hidden;
        animation: socialBounce 0.6s ease-out backwards;
    }
    
    .social-pill:nth-child(1) { animation-delay: 0.1s; }
    .social-pill:nth-child(2) { animation-delay: 0.2s; }
    .social-pill:nth-child(3) { animation-delay: 0.3s; }
    .social-pill:nth-child(4) { animation-delay: 0.4s; }
    
    @keyframes socialBounce {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .social-pill::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.3s ease, height 0.3s ease;
    }
    
    .social-pill:hover::before {
        width: 100%;
        height: 100%;
    }
    
    .social-pill:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.35) 0%, rgba(118, 75, 162, 0.35) 100%);
        transform: translateY(-5px) scale(1.15) rotate(10deg);
        box-shadow: 
            0 10px 30px rgba(102, 126, 234, 0.5),
            inset 0 0 15px rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields with glow effect */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: rgba(30, 30, 60, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        color: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:hover {
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    .stSelectbox > div > div:focus, .stTextInput > div > div > input:focus {
        border-color: rgba(102, 126, 234, 0.6);
        box-shadow: 
            0 0 0 3px rgba(102, 126, 234, 0.1),
            0 0 30px rgba(102, 126, 234, 0.3);
        transform: scale(1.02);
    }
    
    /* Success, Warning, Error messages with animations */
    .stSuccess, .stWarning, .stError, .stInfo {
        animation: messageSlide 0.4s ease-out;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-left: 4px solid #10b981;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
        border-left: 4px solid #f59e0b;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(185, 28, 28, 0.1) 100%);
        border-left: 4px solid #ef4444;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
        border-left: 4px solid #3b82f6;
    }
    
    /* Property Cards with slide effect */
    .property-item {
        background: rgba(30, 30, 60, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(102, 126, 234, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .property-item::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .property-item:hover::after {
        transform: scaleX(1);
    }
    
    .property-item:hover {
        transform: translateX(10px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 
            0 5px 20px rgba(102, 126, 234, 0.2),
            inset 0 0 20px rgba(102, 126, 234, 0.05);
    }
    
    /* Scroll animations trigger */
    @media (prefers-reduced-motion: no-preference) {
        [data-testid="stVerticalBlock"] > [data-testid="element-container"] {
            animation: fadeInUp 0.6s ease-out backwards;
        }
        
        [data-testid="stVerticalBlock"] > [data-testid="element-container"]:nth-child(odd) {
            animation: fadeInLeft 0.6s ease-out backwards;
        }
        
        [data-testid="stVerticalBlock"] > [data-testid="element-container"]:nth-child(even) {
            animation: fadeInRight 0.6s ease-out backwards;
        }
    }
    
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
    
    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Loading state */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 30, 60, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
    }
    
    /* Responsive design improvements */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        .deputy-card {
            padding: 1.5rem;
            border-radius: 16px;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
        }
        
        .social-pills {
            justify-content: center;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
    }
    
    /* Print styles */
    @media print {
        .stApp {
            background: white !important;
        }
        
        * {
            color: black !important;
            background: transparent !important;
            box-shadow: none !important;
        }
    }
    
    /* Performance optimizations */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header { visibility: hidden; }
    .viewerBadge_container__1QSob { display: none; }
    
    /* Additional hover effects for interactive elements */
    button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Highlight animation for important values */
    @keyframes highlight {
        0% { background-color: transparent; }
        50% { background-color: rgba(102, 126, 234, 0.2); }
        100% { background-color: transparent; }
    }
    
    strong {
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 0 4px;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    strong:hover {
        animation: highlight 1s ease;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
    path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
    for col in path_columns:
        if col in df.columns:
            df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
    return df

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
    """Format currency values for display with Spanish notation - exact values"""
    if not isinstance(value, (int, float)):
        return "0€"
    
    # Check if it's a whole number or has decimals
    if value == int(value):
        # No decimals needed - format with Spanish thousands separator
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted}€"
    else:
        # Show up to 2 decimal places with Spanish formatting
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"

def format_currency_full(value):
    """Format currency values for detailed display with Spanish formatting"""
    if not isinstance(value, (int, float)):
        return "0,00 €"
    
    # Show exact value with Spanish formatting
    if value == int(value):
        # If it's a whole number, show without decimals
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted} €"
    else:
        # Show with 2 decimal places
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
    """Create a compact image gallery for the deputy"""
    gallery_html = '<div class="image-gallery">'
    
    # Main photo
    gallery_html += '<div class="main-image-container">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        import base64
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" class="main-image" alt="Foto del Diputado">'
    else:
        gallery_html += '<div class="main-image" style="width: 220px; height: 280px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; font-size: 1.2rem; border-radius: 15px; border: 2px solid rgba(102, 126, 234, 0.3);">👤<br>Sin Foto</div>'
    gallery_html += '</div>'
    
    # Badges container
    gallery_html += '<div class="badge-container">'
    
    # Party logo
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        import base64
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="party-logo" alt="Logo del Partido" title="Partido Político">'
    
    # Seat indicator
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        import base64
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="seat-indicator" alt="Posición en el Hemiciclo" title="Escaño en el Hemiciclo">'
    
    gallery_html += '</div></div>'
    return gallery_html

def main():
    # Header with gradient
    st.markdown('<h1 style="text-align: center; margin-bottom: 0;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1rem; margin-top: 0;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    # Search in a compact layout
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado por nombre...", label_visibility="visible")
        
        # Filter data
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
        
        with col2:
            st.metric("Resultados", f"{len(filtered_df)}", label_visibility="visible")
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
    else:
        # Deputy selector with better formatting
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "**Seleccionar Diputado:**",
            deputy_names,
            format_func=lambda x: f"👤 {x}",
            label_visibility="visible"
        )
        
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        # Main Deputy Card
        st.markdown('<div class="deputy-card">', unsafe_allow_html=True)
        
        # Create two-column layout with image gallery on left
        col_left, col_right = st.columns([1.6, 2])
        
        with col_left:
            # Compact image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info in compact grid
            st.markdown("### 📋 Información Básica")
            
            # Build info grid dynamically, excluding 'nan' values
            info_html = '<div class="info-grid">'
            
            # Always show cargo, default to "Diputado" if empty
            cargo = deputy_data.get('informacion_personal_cargo', '')
            if not cargo or str(cargo).lower() == 'nan':
                cargo = 'Diputado'
            info_html += f'''
            <div class="info-item">
                <div class="info-label">📋 CARGO</div>
                <div class="info-value">{cargo}</div>
            </div>'''
            
            circunscripcion = deputy_data.get('informacion_personal_circunscripcion', '')
            if circunscripcion and str(circunscripcion).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">📍 CIRCUNSCRIPCIÓN</div>
                    <div class="info-value">{circunscripcion}</div>
                </div>'''
            
            estado_civil = deputy_data.get('informacion_personal_estado_civil', '')
            if estado_civil and str(estado_civil).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">💑 ESTADO CIVIL</div>
                    <div class="info-value">{estado_civil}</div>
                </div>'''
            
            fecha_eleccion = deputy_data.get('informacion_personal_fecha_eleccion', '')
            if fecha_eleccion and str(fecha_eleccion).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">📅 FECHA DE ELECCIÓN</div>
                    <div class="info-value">{fecha_eleccion}</div>
                </div>'''
            
            info_html += '</div>'
            st.markdown(info_html, unsafe_allow_html=True)
            
            # Social Media Links as pills with emojis
            social_links = {
                "𝕏": deputy_data.get('twitter'),  # X/Twitter
                "📘": deputy_data.get('facebook'),  # Facebook
                "📸": deputy_data.get('instagram'),  # Instagram
                "🌐": deputy_data.get('website')  # Website
            }
            
            valid_links = {emoji: url for emoji, url in social_links.items() if pd.notna(url) and str(url).lower() != 'nan'}
            
            if valid_links:
                st.markdown("### 🌐 Redes Sociales")
                social_html = '<div class="social-pills">'
                
                # Map emojis to titles for hover text
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
        
        with col_right:
            # Deputy name with style
            st.markdown(f"## 👤 {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            # Calculate financial metrics
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in salaries if isinstance(s, dict))
            
            if total_salary == 0:
                salary_text = str(deputy_data.get('rentas_percibidas_percepciones_salariales', ''))
                if "mensual" in salary_text.lower():
                    monthly_salary = extract_currency_value(salary_text)
                    total_salary = monthly_salary * 12
            
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            properties_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
            
            # Financial Overview - Compact metrics with exact values
            st.markdown("### 💰 Resumen Financiero")
            
            # Display key metrics in a more accessible way
            col_metrics = st.columns(3)
            
            with col_metrics[0]:
                st.markdown("**💵 Ingresos Totales**")
                st.markdown(f"# {format_currency(total_salary)}")
                st.markdown(f"*IRPF Pagado:* **{format_currency(irpf)}**")
                st.markdown(f"*Tipo Efectivo:* **{tax_rate:.2f}%**")
            
            with col_metrics[1]:
                st.markdown("**🏠 Patrimonio**")
                st.markdown(f"# {properties_count + vehicles_count}")
                st.markdown(f"*Inmuebles:* **{properties_count}**")
                st.markdown(f"*Vehículos:* **{vehicles_count}**")
            
            with col_metrics[2]:
                st.markdown("**💳 Obligaciones**")
                st.markdown(f"# {format_currency(total_debt)}")
                if total_debt > 0:
                    st.markdown(f"*Deudas activas:* **{len(debts)}**")
                else:
                    st.markdown("*Sin deudas*")
            
            st.markdown("---")
            
            # Compact tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💵 Ingresos", "🏠 Patrimonio", "💳 Deudas", "📊 Análisis"])
            
            with tab1:
                st.markdown("#### 💵 **Fuentes de Ingresos Declaradas**")
                
                # Show total income at the top
                if total_salary > 0:
                    st.success(f"💰 **Ingresos Totales Anuales: {format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"📋 **IRPF Pagado: {format_currency_full(irpf)}** ({tax_rate:.2f}% tipo efectivo)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 💼 Salarios e Ingresos")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                concepto = salary.get('concepto', '')
                                if not concepto or str(concepto).lower() == 'nan':
                                    concepto = f'Fuente de Ingresos #{i+1}'
                                
                                amount = extract_currency_value(salary.get('euros'))
                                display_amount = format_currency_full(amount)
                                
                                # Color code based on amount
                                if amount > 100000:
                                    st.error(f"💰 **{concepto}**")
                                elif amount > 50000:
                                    st.warning(f"💰 **{concepto}**")
                                else:
                                    st.info(f"💰 **{concepto}**")
                                
                                if "mensual" in str(salary.get('euros', '')).lower():
                                    st.markdown(f"→ **{display_amount}/mes** ({format_currency_full(amount * 12)}/año)")
                                else:
                                    st.markdown(f"→ **{display_amount}**")
                                st.markdown("")
                    else:
                        st.info("📭 No se han declarado salarios")
                
                with col2:
                    st.markdown("##### 📈 Rentas del Capital")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        total_dividends = sum(extract_currency_value(d.get('euros', 0)) for d in dividends if isinstance(d, dict))
                        if total_dividends > 0:
                            st.warning(f"📊 **Total rentas capital: {format_currency_full(total_dividends)}**")
                        
                        for div in dividends:
                            if isinstance(div, dict):
                                concepto = div.get('concepto', '')
                                if not concepto or str(concepto).lower() == 'nan':
                                    concepto = 'Inversión'
                                
                                st.markdown(f"**📊 {concepto}**")
                                rendimientos = extract_currency_value(div.get('euros'))
                                if rendimientos > 0:
                                    st.markdown(f"→ **{format_currency_full(rendimientos)}**")
                                st.markdown("")
                    else:
                        st.info("📭 No se han declarado rentas del capital")
            
            with tab2:
                st.markdown("#### 🏠 **Patrimonio Declarado**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏢 Bienes Inmuebles")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                # Create a card-like display
                                with st.container():
                                    st.markdown(f"""
                                    <div style='background: rgba(102, 126, 234, 0.05); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 3px solid #667eea;'>
                                    <strong style='color: #667eea; font-size: 1.1rem;'>📍 Inmueble #{i+1}</strong>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    tipo = prop.get('clase_y_caracteristicas', '')
                                    if tipo and str(tipo).lower() != 'nan':
                                        st.markdown(f"**Tipo:** {tipo}")
                                    
                                    ubicacion = prop.get('situacion', '')
                                    if ubicacion and str(ubicacion).lower() != 'nan':
                                        st.markdown(f"**📍 Ubicación:** {ubicacion}")
                                    
                                    fecha = prop.get('fecha_adquisicion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"**📅 Adquirido:** {fecha}")
                                    
                                    derecho = prop.get('derecho_sobre_el_bien', '')
                                    if derecho and str(derecho).lower() != 'nan':
                                        st.markdown(f"**📜 Derecho:** {derecho}")
                    else:
                        st.info("📭 No se han declarado propiedades")
                    
                    st.markdown("##### 💳 Activos Financieros")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                        if total_accounts > 0:
                            st.success(f"💰 **Total en cuentas: {format_currency_full(total_accounts)}**")
                        
                        for i, account in enumerate(accounts):
                            if isinstance(account, dict):
                                desc = account.get('descripcion', '')
                                if not desc or str(desc).lower() == 'nan':
                                    desc = f'Cuenta #{i+1}'
                                
                                saldo = extract_currency_value(account.get('saldo'))
                                if saldo > 0:
                                    st.markdown(f"""
                                    **🏦 {desc}**  
                                    → Saldo: **{format_currency_full(saldo)}**
                                    """)
                    else:
                        st.info("📭 No se han declarado cuentas")
                
                with col2:
                    st.markdown("##### 🚗 Vehículos")
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        st.info(f"🚙 **Total vehículos: {len(vehicles)}**")
                        
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                desc = vehicle.get('descripcion', '')
                                if desc and str(desc).lower() != 'nan':
                                    st.markdown(f"""
                                    **🚗 {desc}**
                                    """)
                                else:
                                    st.markdown(f"**🚗 Vehículo #{i+1}**")
                                
                                fecha = vehicle.get('fecha_adquisicion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"→ Adquirido: {fecha}")
                                st.markdown("")
                    else:
                        st.info("📭 No se han declarado vehículos")
                    
                    # Add a summary box if there are multiple vehicles or properties
                    total_assets = properties_count + vehicles_count
                    if total_assets > 5:
                        st.warning(f"⚠️ **Alto patrimonio declarado:** {total_assets} bienes totales")
            
            with tab3:
                st.markdown("#### 💸 Deudas y Obligaciones")
                if debts:
                    # Summary card
                    st.error(f"💰 **Deuda Total Pendiente: {format_currency_full(total_debt)}**")
                    st.markdown("")
                    
                    # Display debts in a grid layout
                    debt_cols = st.columns(2)
                    
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            col_idx = i % 2
                            with debt_cols[col_idx]:
                                desc = debt.get('descripcion', '')
                                if not desc or str(desc).lower() == 'nan':
                                    desc = f'Deuda #{i+1}'
                                
                                st.markdown(f"**📄 {desc}**")
                                
                                importe_original = extract_currency_value(debt.get('importe_concedido'))
                                if importe_original > 0:
                                    st.markdown(f"• Original: **{format_currency_full(importe_original)}**")
                                
                                importe_pendiente = extract_currency_value(debt.get('saldo_pendiente'))
                                if importe_pendiente > 0:
                                    st.markdown(f"• Pendiente: **{format_currency_full(importe_pendiente)}**")
                                
                                fecha = debt.get('fecha_concesion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"• Fecha: {fecha}")
                                
                                original = extract_currency_value(debt.get('importe_concedido'))
                                pending = extract_currency_value(debt.get('saldo_pendiente'))
                                if original > 0:
                                    paid_pct = ((original - pending) / original) * 100
                                    if paid_pct > 50:
                                        st.success(f"✅ Pagado: **{paid_pct:.1f}%**")
                                    else:
                                        st.warning(f"⏳ Pagado: **{paid_pct:.1f}%**")
                                
                                st.markdown("---")
                else:
                    st.success("✅ No se han declarado deudas")
            
            with tab4:
                st.markdown("#### 📊 Análisis Financiero")
                
                # Create analysis visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Asset Distribution Pie Chart
                    fig_assets = go.Figure(data=[go.Pie(
                        labels=['Propiedades', 'Vehículos', 'Efectivo/Cuentas'],
                        values=[
                            properties_count * 150000,  # Estimated avg property value
                            vehicles_count * 20000,     # Estimated avg vehicle value
                            sum(extract_currency_value(a.get('saldo', 0)) for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']) if isinstance(a, dict))
                        ],
                        hole=.3,
                        marker_colors=['#667eea', '#764ba2', '#f093fb']
                    )])
                    fig_assets.update_layout(
                        title="Distribución de Patrimonio (Estimado)",
                        showlegend=True,
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_assets, use_container_width=True)
                
                with col2:
                    # Tax Efficiency Gauge with exact value
                    fig_tax = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=tax_rate,
                        number={'suffix': "%", 'valueformat': ".2f"},
                        title={'text': "Tipo Impositivo Efectivo"},
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
                                'value': 30
                            }
                        }
                    ))
                    fig_tax.update_layout(
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_tax, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
