import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64
import random
import unicodedata

# Page configuration
st.set_page_config(
    page_title="Declaración de Bienes - Congreso de España",
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
        
        /* Random Button Special Styling */
        .random-button-container {
            margin-top: 27px;
        }
        
        .random-button-container > div > button {
            background: linear-gradient(135deg, #f59e0b 0%, #dc2626 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
            padding: 0.65rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .random-button-container > div > button:hover {
            transform: translateY(-2px) scale(1.05) !important;
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.5) !important;
            background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%) !important;
        }
        
        .random-button-container > div > button:active {
            transform: scale(0.98) !important;
        }
        
        @keyframes diceRoll {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(90deg); }
            50% { transform: rotate(180deg); }
            75% { transform: rotate(270deg); }
            100% { transform: rotate(360deg); }
        }
        
        .random-button-container > div > button:hover::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transform: rotate(45deg);
            animation: shimmer 0.5s ease-out;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        /* Screener Card Styling */
        .screener-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        .screener-card:hover {
            transform: translateY(-5px);
            border-color: rgba(102, 126, 234, 0.4);
            box-shadow: 0 12px 30px rgba(102, 126, 234, 0.3);
        }
        
        .screener-rank {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            min-width: 60px;
            text-align: center;
        }
        
        .screener-rank.gold {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .screener-rank.silver {
            background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .screener-rank.bronze {
            background: linear-gradient(135deg, #cd7f32 0%, #e89b5c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .screener-photo {
            width: 80px;
            height: 100px;
            object-fit: cover;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        
        .screener-photo-placeholder {
            width: 80px;
            height: 100px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.1));
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            font-size: 2rem;
        }
        
        .screener-info {
            flex: 1;
            min-width: 0;
        }
        
        .screener-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.3rem;
        }
        
        .screener-party {
            font-size: 0.9rem;
            color: #94a3b8;
            margin-bottom: 0.5rem;
        }
        
        .screener-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .screener-value.positive {
            color: #10b981;
        }
        
        .screener-value.negative {
            color: #ef4444;
        }
        
        /* Activity Card Styling */
        .activity-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .activity-card:hover {
            transform: translateY(-3px);
            border-color: rgba(102, 126, 234, 0.4);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }
        
        .activity-type-badge {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-cargo {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
        }
        
        .badge-actividad {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
        }
        
        .badge-partido {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
        }
        
        .badge-otros {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            color: white;
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
            padding: 2rem 3rem 3rem 3rem;
            margin: 2rem auto;
            max-width: 900px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        h1.disclaimer-title {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 2rem !important;
            padding-bottom: 0 !important;
        }

        h3.disclaimer-section-title {
            color: #f59e0b !important;
            margin-top: 2.5rem !important;
            margin-bottom: 1rem !important;
            font-size: 1.2rem !important;
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
            
            .screener-card {
                flex-direction: column;
                text-align: center;
            }
            
            .screener-rank {
                min-width: auto;
            }
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    try:
        df = pd.read_csv('deputies_with_salaries.csv', encoding='utf-8-sig')
        path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
        for col in path_columns:
            if col in df.columns:
                df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'deputies_with_salaries.csv'. Por favor, asegúrate de que el archivo esté en el mismo directorio que la aplicación.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_interests_data():
    """Load the interests and activities CSV data"""
    try:
        df = pd.read_csv('deputies_interests_full.csv', encoding='utf-8-sig')
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def normalize_name(name):
    """Normalize name for matching"""
    if pd.isna(name):
        return ""
    # Remove accents and convert to lowercase
    name = str(name)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Remove extra whitespace and convert to lowercase
    return ' '.join(name.lower().split())

def normalize_deputy_id(deputy_id):
    """Normalize deputy ID for matching (handles both int and zero-padded strings)"""
    if pd.isna(deputy_id):
        return None
    try:
        # Convert to int to remove leading zeros, then back to string
        return str(int(deputy_id))
    except (ValueError, TypeError):
        return str(deputy_id).strip()

def match_deputy_interests(deputy_name, deputy_id, interests_df):
    """Match deputy with their interests data using both ID and name"""
    if interests_df.empty:
        return pd.DataFrame()
    
    matches = pd.DataFrame()
    
    # Method 1: Try matching by deputy_id first (most reliable)
    if pd.notna(deputy_id):
        normalized_id = normalize_deputy_id(deputy_id)
        if normalized_id:
            interests_df['normalized_metadata_deputy_id'] = interests_df['metadata_deputy_id'].apply(normalize_deputy_id)
            id_matches = interests_df[interests_df['normalized_metadata_deputy_id'] == normalized_id]
            if not id_matches.empty:
                return id_matches
    
    # Method 2: Try name matching
    normalized_deputy = normalize_name(deputy_name)
    
    # Create normalized full name combinations from interests data
    interests_df['full_name_normalized'] = (
        interests_df['personal_nombre'].fillna('') + ' ' + 
        interests_df['personal_apellidos'].fillna('')
    ).apply(normalize_name)
    
    # Also try reversed order (Last Name First Name)
    interests_df['full_name_reversed'] = (
        interests_df['personal_apellidos'].fillna('') + ' ' + 
        interests_df['personal_nombre'].fillna('')
    ).apply(normalize_name)
    
    # Find matches
    matches = interests_df[
        (interests_df['full_name_normalized'] == normalized_deputy) |
        (interests_df['full_name_reversed'] == normalized_deputy)
    ]
    
    return matches

def display_interests_section(deputy_interests):
    """Display the interests and activities section"""
    if deputy_interests.empty:
        st.info("📋 No hay información de registro de intereses disponible para este diputado.")
        return
    
    st.markdown(f"### 📋 Registro de Intereses - {len(deputy_interests)} Registros")
    
    # Group by section type
    section_groups = deputy_interests.groupby('seccion')
    
    # Create expandable sections for each type
    for section_name, section_data in section_groups:
        
        section_titles = {
            'actividades_previas': '🏛️ Actividades Previas al Mandato',
            'donaciones': '🎁 Donaciones y Obsequios',
            'fundaciones': '🏢 Fundaciones y Asociaciones',
            'otros_intereses': '📝 Otros Intereses'
        }
        
        section_title = section_titles.get(section_name, f'📌 {section_name.replace("_", " ").title()}')
        
        with st.expander(f"{section_title} ({len(section_data)})", expanded=(section_name == 'actividades_previas')):
            
            if section_name == 'actividades_previas':
                # Display activities
                for idx, row in section_data.iterrows():
                    activity_type = row.get('actividad_tipo', 'Sin especificar')
                    activity_desc = row.get('actividad_descripcion', '')
                    activity_date = row.get('actividad_fecha', '')
                    activity_cargo = row.get('actividad_cargo', '')
                    
                    # Determine badge class based on activity type
                    badge_class = 'badge-otros'
                    if pd.notna(activity_type):
                        activity_type_lower = str(activity_type).lower()
                        if 'cargo' in activity_type_lower and 'público' in activity_type_lower:
                            badge_class = 'badge-cargo'
                        elif 'partido' in activity_type_lower or 'grupo parlamentario' in activity_type_lower:
                            badge_class = 'badge-partido'
                        elif 'privada' in activity_type_lower or 'docente' in activity_type_lower:
                            badge_class = 'badge-actividad'
                    
                    # Create activity card
                    card_html = f'''
                    <div class="activity-card">
                        <div class="activity-type-badge {badge_class}">{activity_type if pd.notna(activity_type) else 'Sin especificar'}</div>
                    '''
                    
                    if pd.notna(activity_cargo) and str(activity_cargo).strip():
                        card_html += f'<p style="color: #ffffff; font-weight: 600; margin: 0.5rem 0;">📌 {activity_cargo}</p>'
                    
                    if pd.notna(activity_desc) and str(activity_desc).strip():
                        card_html += f'<p style="color: #e2e8f0; margin: 0.5rem 0;">{activity_desc}</p>'
                    
                    if pd.notna(activity_date) and str(activity_date).strip():
                        card_html += f'<p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">📅 {activity_date}</p>'
                    
                    card_html += '</div>'
                    st.markdown(card_html, unsafe_allow_html=True)
            
            elif section_name == 'otros_intereses':
                # Display other interests
                for idx, row in section_data.iterrows():
                    otros_texto = row.get('otros_intereses_texto', '')
                    if pd.notna(otros_texto) and str(otros_texto).strip():
                        st.markdown(f"""
                        <div class="activity-card">
                            <p style="color: #e2e8f0; white-space: pre-wrap;">{otros_texto}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            else:
                # Generic display for other sections
                for idx, row in section_data.iterrows():
                    st.markdown(f"""
                    <div class="activity-card">
                        <p style="color: #e2e8f0;">Registro de {section_name.replace('_', ' ')}</p>
                    </div>
                    """, unsafe_allow_html=True)

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

def get_deputy_photo_html(photo_path, size="small"):
    """Get deputy photo HTML for screener cards"""
    if size == "small":
        width, height = 80, 100
    else:
        width, height = 200, 250
        
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        try:
            with open(photo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" class="screener-photo" alt="Foto del diputado">'
        except:
            return '<div class="screener-photo-placeholder">👤</div>'
    else:
        return '<div class="screener-photo-placeholder">👤</div>'

def extract_irpf_value(value):
    """Extract IRPF value with corruption detection and correction"""
    if pd.isna(value) or value == '':
        return 0
    
    if isinstance(value, (int, float)):
        value = float(value)
        value_str = str(value)
        
        # Case 1: Extremely high values (> 200,000) with suspicious decimals
        # Pattern: 3213560.321356 → 31135.60 or 1849074.0 → 18490.74
        if value > 200000:
            if '.' in value_str:
                parts = value_str.split('.')
                full_digits = parts[0] + parts[1].rstrip('0')
                
                # For very long corrupted numbers like 3213560321356
                if len(full_digits) >= 7:
                    # Extract middle portion: "3213560321356" → "31135" + "60"
                    middle_start = 1
                    middle_end = 6
                    if len(full_digits) >= middle_end + 2:
                        corrected = full_digits[middle_start:middle_end] + '.' + full_digits[middle_end:middle_end+2]
                        return float(corrected)
            
            # Simple case: remove decimal point 2 positions from right
            # 1849074 → 18490.74
            value_str_int = str(int(value))
            if len(value_str_int) >= 3:
                corrected = value_str_int[:-2] + '.' + value_str_int[-2:]
                return float(corrected)
        
        # Case 2: Values with dot as thousands separator and extra decimals
        # Pattern: 38.84977 → 38849.77 (dot is thousands, last digits are decimals)
        if 10 < value < 200000 and '.' in value_str:
            parts = value_str.split('.')
            if len(parts) == 2:
                integer_part = parts[0]
                decimal_part = parts[1]
                
                # If we have something like "38.84977"
                # This means 38 thousand + 849.77
                if len(decimal_part) >= 3:
                    # Combine: "38" + "84977" → "3884977" → "38849.77"
                    combined = integer_part + decimal_part
                    # Insert decimal point 2 positions from right
                    corrected = combined[:-2] + '.' + combined[-2:]
                    return float(corrected)
                
                # If it's like "23.117" (format español)
                elif len(decimal_part) == 3:
                    # Remove the dot: 23117
                    return float(integer_part + decimal_part)
        
        # Case 3: Very small values with dot (like 23.117)
        if 20 < value < 100 and '.' in value_str:
            return float(value_str.replace('.', ''))
        
        # Value seems normal
        return value
    
    # If it's a string, parse it
    value_str = str(value).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    numeric_part = re.search(r'[\d.,]+', value_str)
    
    if numeric_part:
        num_str = numeric_part.group(0)
        # European format with comma as decimal
        if ',' in num_str:
            return float(num_str.replace('.', '').replace(',', '.'))
        else:
            return float(num_str.replace(',', ''))
    
    return 0

def extract_debt_account_value(value_str):
    """Extract currency value from debt/account fields - handles all DB formats correctly"""
    if pd.isna(value_str) or value_str == '':
        return 0
    
    # Priority 1: Already a clean number (int or float)
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    # Priority 2: Parse string
    value_str = str(value_str).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    
    numeric_part = re.search(r'[\d.,]+', value_str)
    if not numeric_part:
        return 0
    
    try:
        num_str = numeric_part.group(0)
        dot_count = num_str.count('.')
        comma_count = num_str.count(',')
        
        # CASE 1: Has comma - comma is ALWAYS decimal separator
        if comma_count > 0:
            # European format: dots=thousands, comma=decimal
            # Examples: "67.230,26" → 67230.26 or "1.200.000,50" → 1200000.50
            return float(num_str.replace('.', '').replace(',', '.'))
        
        # CASE 2: No comma, only dots
        if dot_count > 0 and comma_count == 0:
            # Multiple dots = ALL are thousands separators
            # Examples: "1.112.477" → 1112477
            if dot_count > 1:
                return float(num_str.replace('.', ''))
            
            # Single dot - need to determine if it's decimal or thousands or corrupted
            parts = num_str.split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
            
            # Corrupted format like "13.15250" (should be 13152.50)
            if len(decimal_part) >= 3:
                # If 3-5 digits after dot, it's corrupted
                # "13.15250" → "1315250" → "13152.50"
                combined = integer_part + decimal_part
                corrected = combined[:-2] + '.' + combined[-2:]
                return float(corrected)
            
            # Normal decimal: "70847.8" or "123.45"
            elif len(decimal_part) <= 2:
                return float(num_str)
            
            # Fallback: treat as thousands separator
            else:
                return float(num_str.replace('.', ''))
        
        # CASE 3: No separators at all
        return float(num_str)
        
    except (ValueError, TypeError):
        return 0
    
    return 0


# Update the prepare_screener_data function to use the correct function for each field
def prepare_screener_data(df):
    """Prepare data for screener with all metrics calculated - properly deduplicated"""
    df_copy = df.copy()
    df_copy['normalized_name'] = df_copy['informacion_personal_nombre_y_apellidos'].apply(normalize_name)
    
    df_sorted = df_copy.sort_values('source_file', ascending=True)
    unique_deputies = df_sorted.groupby('normalized_name').last().reset_index()
    
    screener_data = []
    
    for idx, row in unique_deputies.iterrows():
        deputy_info = {
            'name': row['informacion_personal_nombre_y_apellidos'],
            'photo_path': row.get('photo_path', ''),
            'party': row.get('informacion_personal_cargo', 'Diputado'),
            'salary': 0,
            'irpf': 0,
            'properties_count': 0,
            'vehicles_count': 0,
            'debt_total': 0,
            'accounts_balance': 0,
            'max_account': 0,
            'max_debt': 0,
            'max_debt_original': 0,
            'total_assets': 0,
        }
        
        # Salary
        salary = row.get('scraped_salary', None)
        if pd.notna(salary) and salary:
            try:
                deputy_info['salary'] = float(salary)
            except:
                deputy_info['salary'] = 0
        
        # IRPF - USE SPECIFIC FUNCTION
        irpf = extract_irpf_value(row.get('irpf_cantidad_pagada', 0))
        deputy_info['irpf'] = irpf
        
        # Properties
        urban_properties = parse_json_field(row['bienes_patrimoniales_inmuebles_urbanos'])
        rustic_properties = parse_json_field(row.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))
        deputy_info['properties_count'] = len(urban_properties) + len(rustic_properties)
        
        # Vehicles
        vehicles = parse_json_field(row['vehiculos'])
        deputy_info['vehicles_count'] = len(vehicles)
        
        # Debts - USE SPECIFIC FUNCTION FOR DEBT/ACCOUNT FIELDS
        debts = parse_json_field(row['deudas_y_obligaciones'])
        debt_pending = []
        debt_original = []
        for debt in debts:
            if isinstance(debt, dict):
                pending = extract_debt_account_value(debt.get('saldo_pendiente', 0))
                original = extract_debt_account_value(debt.get('importe_concedido', 0))
                if pending > 0:
                    debt_pending.append(pending)
                if original > 0:
                    debt_original.append(original)
        
        deputy_info['debt_total'] = sum(debt_pending)
        deputy_info['max_debt'] = max(debt_pending) if debt_pending else 0
        deputy_info['max_debt_original'] = max(debt_original) if debt_original else 0
        
        # Accounts - USE SPECIFIC FUNCTION
        accounts = parse_json_field(row['depositos_y_cuentas_cuentas'])
        account_balances = []
        for account in accounts:
            if isinstance(account, dict):
                saldo = extract_debt_account_value(account.get('saldo', 0))
                if saldo > 0:
                    account_balances.append(saldo)
        
        deputy_info['accounts_balance'] = sum(account_balances)
        deputy_info['max_account'] = max(account_balances) if account_balances else 0
        
        # Calculate total liquid assets
        total_assets = deputy_info['accounts_balance']
        
        # Add other financial assets
        acciones = parse_json_field(row.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
        for accion in acciones:
            if isinstance(accion, dict):
                valor = extract_debt_account_value(accion.get('valor', 0))
                total_assets += valor
        
        deuda_publica = parse_json_field(row.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
        for valor in deuda_publica:
            if isinstance(valor, dict):
                val = extract_debt_account_value(valor.get('valor', 0))
                total_assets += val
        
        deputy_info['total_assets'] = total_assets
        
        screener_data.append(deputy_info)
    
    return pd.DataFrame(screener_data)

def show_screener(df):
    """Display the screener interface"""
    st.markdown('<h1 style="text-align: center;">🔍 Screening de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">Explora y compara las métricas financieras de los diputados</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Prepare screener data
    screener_df = prepare_screener_data(df)
    
    # Controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metric_options = {
            '💰 Salario Anual': ('salary', 'positive', 'currency'),
            '💵 IRPF Pagado': ('irpf', 'positive', 'currency'),
            '🏠 Número de Inmuebles': ('properties_count', 'positive', 'number'),
            '🚗 Número de Vehículos': ('vehicles_count', 'positive', 'number'),
            '💳 Deuda Total Pendiente': ('debt_total', 'negative', 'currency'),
            '⚠️ Préstamo Individual Más Alto (Pendiente)': ('max_debt', 'negative', 'currency'),
            '📊 Préstamo Individual Más Alto (Original)': ('max_debt_original', 'negative', 'currency'),
            '🏦 Saldo Total en Cuentas': ('accounts_balance', 'positive', 'currency'),
            '💎 Cuenta Individual Más Grande': ('max_account', 'positive', 'currency'),
            '💼 Total Activos Líquidos': ('total_assets', 'positive', 'currency'),
        }
        
        selected_metric_name = st.selectbox(
            "Seleccionar Métrica:",
            list(metric_options.keys())
        )
    
    with col2:
        ranking_type = st.radio(
            "Tipo de Ranking:",
            ["🔝 Top 10", "🔻 Bottom 10"],
            horizontal=True
        )
    
    metric_column, value_class, format_type = metric_options[selected_metric_name]
    
    st.markdown("---")
    
    # Sort and filter
    ascending = ranking_type == "🔻 Bottom 10"
    top_deputies = screener_df.nlargest(10, metric_column) if not ascending else screener_df.nsmallest(10, metric_column)
    
    # Display header
    if ranking_type == "🔝 Top 10":
        st.markdown(f"### 🏆 Top 10 Diputados - {selected_metric_name}")
    else:
        st.markdown(f"### 📊 Bottom 10 Diputados - {selected_metric_name}")
    
    # Display summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        avg_value = screener_df[metric_column].mean()
        if format_type == 'currency':
            st.metric("Promedio", format_currency(avg_value))
        else:
            st.metric("Promedio", f"{avg_value:.1f}")
    
    with col2:
        max_value = screener_df[metric_column].max()
        if format_type == 'currency':
            st.metric("Máximo", format_currency(max_value))
        else:
            st.metric("Máximo", f"{int(max_value)}")
    
    st.markdown("---")
    
    # Display cards
    for idx, (_, deputy) in enumerate(top_deputies.iterrows(), 1):
        metric_val = deputy[metric_column]
        
        # Format the metric value
        if format_type == 'currency':
            formatted_value = format_currency_full(metric_val)
        else:
            formatted_value = f"{int(metric_val)}"
        
        display_screener_card(idx, deputy, selected_metric_name, formatted_value, value_class)
    
    st.markdown("---")
    
    # Add visualization
    st.markdown("### 📊 Visualización Comparativa")
    
    fig = go.Figure()
    
    # Format text for chart
    if format_type == 'currency':
        text_values = top_deputies[metric_column].apply(lambda x: format_currency(x))
    else:
        text_values = top_deputies[metric_column].apply(lambda x: f"{int(x)}")
    
    fig.add_trace(go.Bar(
        x=top_deputies['name'],
        y=top_deputies[metric_column],
        marker=dict(
            color=top_deputies[metric_column],
            colorscale='Viridis',
            showscale=True
        ),
        text=text_values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f"{selected_metric_name} - {ranking_type}",
        xaxis_title="Diputado",
        yaxis_title=selected_metric_name,
        template="plotly_dark",
        height=500,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        xaxis=dict(tickangle=-45)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_screener_card(rank, deputy_info, metric_name, metric_value, value_class=""):
    """Display a single screener card - FIXED VERSION"""
    rank_class = ""
    medal = ""
    if rank == 1:
        rank_class = "gold"
        medal = "🥇 "
    elif rank == 2:
        rank_class = "silver"
        medal = "🥈 "
    elif rank == 3:
        rank_class = "bronze"
        medal = "🥉 "
    
    photo_html = get_deputy_photo_html(deputy_info['photo_path'])
    
    card_html = f'''
    <div class="screener-card">
        <div class="screener-rank {rank_class}">{medal}#{rank}</div>
        {photo_html}
        <div class="screener-info">
            <div class="screener-name">{deputy_info['name']}</div>
            <div class="screener-party">{deputy_info['party']}</div>
            <div class="screener-value {value_class}">{metric_value}</div>
        </div>
    </div>
    '''
    st.markdown(card_html, unsafe_allow_html=True)

def show_disclaimer():
    """Show the comprehensive legal disclaimer page using native Streamlit components."""
    apply_css()
    
    _, col2, _ = st.columns([1, 4, 1])
    
    with col2:
        # We use a markdown 'div' wrapper to apply the border and background from our CSS
        st.markdown('<div class="disclaimer-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD LEGAL</h1>', unsafe_allow_html=True)
        
        st.write("**IMPORTANTE: LEA ATENTAMENTE ANTES DE USAR ESTA APLICACIÓN**")
        st.write(
            'Esta aplicación web de consulta de información pública ("la Aplicación") recopila, procesa y presenta datos obtenidos de fuentes públicas disponibles en la página web oficial del Congreso de los Diputados de España, incluyendo documentos en formato PDF y otros registros de acceso público.'
        )

        st.markdown('<h3 class="disclaimer-section-title">📋 NATURALEZA Y ORIGEN DE LA INFORMACIÓN</h3>', unsafe_allow_html=True)
        st.write("La información mostrada en esta Aplicación proviene exclusivamente de:")
        st.markdown("""
        - Declaraciones de bienes y rentas publicadas en el Portal de Transparencia del Congreso de los Diputados
        - Registros públicos de actividades e intereses de los parlamentarios
        - Documentación oficial de acceso público disponible en www.congreso.es
        """)

        st.markdown('<h3 class="disclaimer-section-title">⚠️ DESCARGO DE RESPONSABILIDAD</h3>', unsafe_allow_html=True)
        st.write(
            "**La Aplicación no pertenece, no está vinculada, afiliada, patrocinada, avalada ni autorizada de ninguna manera por el Congreso de los Diputados**, ni por ninguna institución gubernamental o entidad pública española. Es un proyecto independiente desarrollado con fines informativos y de acceso facilitado a información pública."
        )
        st.write("El contenido mostrado se ofrece únicamente con fines informativos, educativos y de consulta pública. Aunque se realizan esfuerzos razonables para garantizar la precisión y actualización de los datos:")
        st.markdown("""
        - La Aplicación puede contener **errores, inexactitudes, omisiones o información desactualizada**
        - Los datos pueden no reflejar los cambios más recientes en las declaraciones
        - Pueden existir discrepancias entre la información mostrada y los documentos originales
        - La interpretación o procesamiento automatizado de los datos puede introducir errores involuntarios
        """)
        
        st.markdown('<h3 class="disclaimer-section-title">📌 LIMITACIÓN DE RESPONSABILIDAD</h3>', unsafe_allow_html=True)
        st.write("Los desarrolladores y operadores de esta Aplicación:")
        st.markdown("""
        - No garantizan la exactitud, integridad, actualidad o idoneidad de la información para ningún propósito particular
        - No asumen responsabilidad por decisiones tomadas basándose en la información aquí presentada
        - No se responsabilizan de daños directos, indirectos, incidentales o consecuentes derivados del uso de la Aplicación
        - Se reservan el derecho de modificar, suspender o discontinuar el servicio sin previo aviso
        """)

        st.markdown('<h3 class="disclaimer-section-title">✅ FUENTE OFICIAL</h3>', unsafe_allow_html=True)
        st.write("**Para la consulta oficial, íntegra, auténtica y legalmente válida de las declaraciones de bienes y rentas de los diputados, se debe acudir directamente a:**")
        st.info("🔗 **Portal de Transparencia del Congreso de los Diputados:** [www.congreso.es](https://www.congreso.es)")

        st.markdown('<h3 class="disclaimer-section-title">👤 PRIVACIDAD Y DATOS PERSONALES</h3>', unsafe_allow_html=True)
        st.write("Esta Aplicación muestra únicamente información que ya es de dominio público y ha sido publicada oficialmente por el Congreso de los Diputados en cumplimiento de las obligaciones de transparencia establecidas en la legislación española.")

        st.markdown('<h3 class="disclaimer-section-title">⚖️ ACEPTACIÓN DE TÉRMINOS</h3>', unsafe_allow_html=True)
        st.write('Al hacer clic en "ACEPTO Y ENTIENDO" y utilizar esta Aplicación, usted reconoce que:')
        st.markdown("""
        - Ha leído y comprendido este descargo de responsabilidad en su totalidad
        - Acepta usar la Aplicación bajo su propio riesgo
        - Comprende las limitaciones de la información presentada
        - Se compromete a verificar cualquier información crítica en las fuentes oficiales
        """)

        st.warning("**ADVERTENCIA FINAL:** El uso de esta aplicación es responsabilidad exclusiva del usuario. Si no está de acuerdo con estos términos, por favor no utilice la Aplicación.")

        # Close the container div
        st.markdown('</div>', unsafe_allow_html=True)

        st.info(
            "💡 **Recomendación de visualización:** Para una experiencia óptima, te recomendamos usar esta aplicación en un ordenador (🖥️) y activar el modo oscuro (🌙) en tu navegador.",
            icon="✨"
        )
        
        # Center the button in its own sub-column layout
        _, btn_col, _ = st.columns([1, 2, 1])
        if btn_col.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()

        st.error("Para usar esta aplicación debe aceptar los términos y condiciones.")
        
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 2rem;">
                Una aplicación desarrollada por <a href="https://x.com/Gsnchez" target="_blank" style="color: #667eea; text-decoration: none;">@Gsnchez</a> en X.
            </div>
            """,
            unsafe_allow_html=True
        )

def main_app():
    """Main application"""
    apply_css()
    
    st.markdown('<h1 style="text-align: center;">⚖️ Declaración de Bienes</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">Análisis Interactivo de la Transparencia Financiera en el Congreso de los Diputados</p>', unsafe_allow_html=True)
    
    df = load_data()
    interests_df = load_interests_data()
    
    if df.empty:
        st.stop()
    
    # Main navigation
    st.markdown("---")
    main_tab = st.radio(
        "Navegación:",
        ["👤 Consulta Individual", "🔍 Screening Comparativo"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if main_tab == "🔍 Screening Comparativo":
        show_screener(df)
    else:
        # Get unique deputies by name
        unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
        
        # Search bar and controls
        search_col, metric_col, random_col = st.columns([8, 2, 1])
        
        with search_col:
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
        
        with metric_col:
            st.metric("Diputados Encontrados", len(filtered_deputies))
            
        deputy_names = filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist()
        
        with random_col:
            # Enhanced random button with special styling
            st.markdown('<div class="random-button-container">', unsafe_allow_html=True)
            if st.button("🎲", use_container_width=True, help="Seleccionar un diputado aleatorio", key="random_deputy"):
                if deputy_names:
                    st.session_state.selected_deputy_name = random.choice(deputy_names)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        if not deputy_names:
            st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
        else:
            # Initialize session state if it's the first run or if the selected deputy is no longer in the filtered list
            if 'selected_deputy_name' not in st.session_state or st.session_state.selected_deputy_name not in deputy_names:
                st.session_state.selected_deputy_name = deputy_names[0]

            # Find the index for the selectbox based on session state
            try:
                selected_index = deputy_names.index(st.session_state.selected_deputy_name)
            except (ValueError, IndexError):
                selected_index = 0

            # Deputy selector with salary information
            def format_deputy_option(name):
                try:
                    deputy_row = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'] == name]
                    if not deputy_row.empty:
                        salary = deputy_row['scraped_salary'].iloc[0]
                        if pd.notna(salary) and salary:
                            formatted_salary = f"{float(salary):,.0f}".replace(",", ".")
                            return f"👤 {name} - 💰 {formatted_salary}€"
                        else:
                            return f"👤 {name} - 💰 Sin datos"
                except:
                    pass
                return f"👤 {name}"
            
            selected_deputy_name = st.selectbox(
                "Seleccionar Diputado:",
                deputy_names,
                index=selected_index,
                format_func=format_deputy_option
            )
            
            # Update session state with the current selection (from user or from random button)
            st.session_state.selected_deputy_name = selected_deputy_name
            
            # Get all declarations for selected deputy
            deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name].sort_values(by='source_file', ascending=True)
            
            # Declaration selector (if multiple)
            if len(deputy_declarations) > 1:
                st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
                
                declaration_options = []
                for i, (idx, row) in enumerate(deputy_declarations.iterrows()):
                    declaration_number = i + 1
                    label_parts = [f"📄 Declaración {declaration_number}"]

                    cargo = row.get('informacion_personal_cargo', '')
                    if pd.notna(cargo):
                        label_parts.append(f"({cargo.strip()})")

                    doc_date_str = "Fecha Desconocida"
                    source_file = row.get('source_file', '')
                    date_match = re.search(r'_(\d{8})\.json$', source_file)
                    if date_match:
                        try:
                            doc_date = datetime.strptime(date_match.group(1), '%Y%m%d')
                            spanish_months_abbr = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                            month_abbr = spanish_months_abbr[doc_date.month - 1]
                            doc_date_str = f"{doc_date.day} {month_abbr} {doc_date.year}"
                        except ValueError:
                            pass
                    
                    label_parts.append(f"- Doc: {doc_date_str}")
                    
                    observaciones = row.get('observaciones', '')
                    if pd.notna(observaciones) and ('modificación' in observaciones.lower() or 'remito a' in observaciones.lower() or 'actualizar' in observaciones.lower()):
                        label_parts.append("[Modificación]")
                    
                    label = " ".join(label_parts)
                    declaration_options.append((idx, label))
                
                selected_idx = st.selectbox(
                    "Seleccionar Declaración:",
                    [opt[0] for opt in declaration_options],
                    format_func=lambda x: next((opt[1] for opt in declaration_options if opt[0] == x), "Seleccionar")
                )
                
                deputy_data = deputy_declarations.loc[selected_idx]
            else:
                deputy_data = deputy_declarations.iloc[0]
            
            st.markdown("---")
            
            # Layout
            col_left, col_right = st.columns([1.5, 2])
            
            with col_left:
                st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
                st.markdown("### 📋 Información Personal")
                
                info_html = '<div class="info-grid">'
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
                        if not value and default: value = default
                        info_html += f'<div class="info-item"><div class="info-label">{label}</div><div class="info-value">{value}</div></div>'
                
                info_html += '</div>'
                st.markdown(info_html, unsafe_allow_html=True)
                
                social_links = { "𝕏": deputy_data.get('twitter'), "📘": deputy_data.get('facebook'), "📸": deputy_data.get('instagram'), "🌐": deputy_data.get('website') }
                valid_links = {emoji: url for emoji, url in social_links.items() if pd.notna(url) and str(url).lower() != 'nan'}
                
                if valid_links:
                    st.markdown("### 🌐 Redes Sociales")
                    social_html = '<div class="social-pills">'
                    emoji_titles = { "𝕏": "X (Twitter)", "📘": "Facebook", "📸": "Instagram", "🌐": "Sitio Web" }
                    for emoji, url in valid_links.items():
                        title = emoji_titles.get(emoji, "")
                        social_html += f'<a href="{url}" target="_blank" class="social-pill" title="{title}">{emoji}</a>'
                    social_html += '</div>'
                    st.markdown(social_html, unsafe_allow_html=True)
                
                observaciones = deputy_data.get('observaciones', '')
                if observaciones and str(observaciones).lower() != 'nan':
                    st.markdown("### 📝 Observaciones")
                    st.info(observaciones)
            
            with col_right:
                st.markdown(f"## 👤 {deputy_data['informacion_personal_nombre_y_apellidos']}")
                
                # Display salary if available
                salary = deputy_data.get('scraped_salary', None)
                if pd.notna(salary) and salary:
                    formatted_salary = f"{float(salary):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    st.success(f"💰 **Salario Anual: {formatted_salary} €**")
                else:
                    st.info("💰 **Salario Anual: No disponible**")
                
                st.markdown("### 📊 Datos Clave de la Declaración")
                
                metric1, metric2, metric3, metric4, metric5 = st.columns(5)
                
                # Display annual salary
                salary = deputy_data.get('scraped_salary', None)
                if pd.notna(salary) and salary:
                    formatted_salary = f"{float(salary):,.0f}".replace(",", ".")
                    metric1.metric("Salario Anual", f"{formatted_salary}€")
                else:
                    metric1.metric("Salario Anual", "N/D")
                
                irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
                metric2.metric("IRPF Pagado", format_currency(irpf))
                
                urban_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
                rustic_properties = len(parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]')))
                metric3.metric("Inmuebles", urban_properties + rustic_properties)

                vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
                metric4.metric("Vehículos", vehicles_count)
                
                debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
                metric5.metric("Deudas", len(debts))

                st.markdown("---")
                
                tabs = st.tabs(["💵 Ingresos", "🏠 Inmuebles", "💼 Sociedades", "💰 Activos", "🚗 Vehículos", "💳 Deudas", "📋 Actividades", "📄 Otros"])
                
                with tabs[0]:
                    st.markdown("#### 💵 Todas las Fuentes de Ingresos")
                    st.info(f"📋 **IRPF Pagado (Declarado): {format_currency_full(irpf)}**")
                    
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### 💼 Salarios")
                        salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                        if salaries:
                            for i, salary in enumerate(salaries):
                                if isinstance(salary, dict):
                                    concepto = salary.get('concepto', f'Ingreso #{i+1}')
                                    if str(concepto).lower() == 'nan': concepto = f'Ingreso #{i+1}'
                                    amount = extract_currency_value(salary.get('euros'))
                                    st.info(f"💰 **{concepto}**")
                                    st.markdown(f"→ **{format_currency_full(amount)}**")
                        else: st.info("Sin salarios declarados")
                        
                        st.markdown("##### 💸 Otras Rentas")
                        otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', ''))
                        if otras:
                            for item in otras:
                                if isinstance(item, dict):
                                    concepto = item.get('concepto', 'Otra renta'); importe = extract_currency_value(item.get('euros', 0))
                                    if importe > 0: st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                        else: st.info("Sin otras rentas")
                    
                    with tcol2:
                        st.markdown("##### 📈 Dividendos y Participaciones")
                        dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                        if dividends:
                            for div in dividends:
                                if isinstance(div, dict):
                                    concepto = div.get('concepto', 'Inversión')
                                    if str(concepto).lower() == 'nan': concepto = 'Inversión'
                                    st.markdown(f"**📊 {concepto}**")
                                    rendimientos = extract_currency_value(div.get('euros'))
                                    if rendimientos > 0: st.markdown(f"→ **{format_currency_full(rendimientos)}**")
                        else: st.info("Sin dividendos")
                        
                        st.markdown("##### 🏦 Intereses Financieros")
                        intereses = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', ''))
                        if intereses:
                            for item in intereses:
                                if isinstance(item, dict):
                                    concepto = item.get('concepto', 'Interés'); importe = extract_currency_value(item.get('euros', 0))
                                    if importe > 0: st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                        else: st.info("Sin intereses financieros")
                
                with tabs[1]:
                    st.markdown("#### 🏠 Bienes Inmuebles")
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### 🏢 Inmuebles Urbanos")
                        urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                        if urban:
                            for i, prop in enumerate(urban):
                                if isinstance(prop, dict):
                                    st.markdown(f"**📍 Inmueble Urbano #{i+1}**")
                                    for key, value in prop.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else: st.info("Sin inmuebles urbanos")
                    with tcol2:
                        st.markdown("##### 🌾 Inmuebles Rústicos")
                        rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                        if rusticos:
                            for i, prop in enumerate(rusticos):
                                if isinstance(prop, dict):
                                    st.markdown(f"**🚜 Inmueble Rústico #{i+1}**")
                                    for key, value in prop.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else: st.info("Sin inmuebles rústicos")
                
                with tabs[2]:
                    st.markdown("#### 💼 Sociedades y Participaciones")
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### 🏢 Sociedades No Cotizadas")
                        sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                        if sociedades:
                            for i, soc in enumerate(sociedades):
                                if isinstance(soc, dict):
                                    st.markdown(f"**🏭 Sociedad #{i+1}**")
                                    for key, value in soc.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else: st.info("Sin sociedades no cotizadas")
                    with tcol2:
                        st.markdown("##### 📊 Participaciones >5%")
                        participaciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                        if participaciones:
                            for i, part in enumerate(participaciones):
                                if isinstance(part, dict):
                                    st.markdown(f"**📈 Participación #{i+1}**")
                                    for key, value in part.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else: st.info("Sin participaciones superiores al 5%")
                
                with tabs[3]:
                    st.markdown("#### 💰 Activos Financieros")
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### 🏦 Cuentas y Depósitos")
                        accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                        if accounts:
                            total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                            if total_accounts > 0: st.success(f"💰 **Total en cuentas: {format_currency_full(total_accounts)}**")
                            for account in accounts:
                                if isinstance(account, dict):
                                    desc = account.get('descripcion', 'Cuenta')
                                    if str(desc).lower() == 'nan': desc = 'Cuenta'
                                    saldo = extract_currency_value(account.get('saldo'))
                                    if saldo > 0:
                                        st.markdown(f"**🏦 {desc}**"); st.markdown(f"Saldo: **{format_currency_full(saldo)}**")
                        else: st.info("Sin cuentas declaradas")
                        
                        st.markdown("##### 📈 Acciones y Participaciones")
                        acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                        if acciones:
                            for i, accion in enumerate(acciones):
                                if isinstance(accion, dict):
                                    st.markdown(f"**📊 Acción/Participación #{i+1}**")
                                    for key, value in accion.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else: st.info("Sin acciones declaradas")
                    
                    with tcol2:
                        st.markdown("##### 📜 Deuda Pública y Valores")
                        deuda_publica = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
                        if deuda_publica:
                            for i, item in enumerate(deuda_publica):
                                if isinstance(item, dict):
                                    st.markdown(f"**💼 Valor #{i+1}**")
                                    for key, value in item.items():
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else: st.info("Sin deuda pública o valores")
                
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
                                    if str(desc).lower() == 'nan': desc = f'Vehículo #{i+1}'
                                    st.markdown(f"**🚗 {desc}**")
                                    fecha = vehicle.get('fecha_adquisicion', '')
                                    if fecha and str(fecha).lower() != 'nan': st.markdown(f"Adquirido: {fecha}")
                                    st.markdown("")
                    else: st.info("Sin vehículos declarados")
                
                with tabs[5]:
                    st.markdown("#### 💸 Deudas y Obligaciones")
                    total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
                    if debts:
                        st.error(f"💰 **Total Pendiente: {format_currency_full(total_debt)}**")
                        for i, debt in enumerate(debts):
                            if isinstance(debt, dict):
                                desc = debt.get('descripcion', f'Deuda #{i+1}')
                                if str(desc).lower() == 'nan': desc = f'Deuda #{i+1}'
                                st.markdown(f"**📄 {desc}**")
                                original = extract_currency_value(debt.get('importe_concedido'))
                                pending = extract_currency_value(debt.get('saldo_pendiente'))
                                tcol1, tcol2 = st.columns(2)
                                with tcol1:
                                    if original > 0: st.markdown(f"Original: **{format_currency_full(original)}**")
                                    fecha = debt.get('fecha_concesion', '')
                                    if fecha and str(fecha).lower() != 'nan': st.markdown(f"Fecha: {fecha}")
                                with tcol2:
                                    if pending > 0: st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                                    if original > 0 and pending > 0:
                                        paid_pct = ((original - pending) / original) * 100
                                        st.progress(int(paid_pct), text=f"Pagado: {paid_pct:.1f}%")
                                st.markdown("---")
                    else: st.success("✅ No se han declarado deudas")
                
                with tabs[6]:
                    st.markdown("#### 📋 Actividades e Intereses")
                    # Match and display interests data using both ID and name
                    deputy_id = deputy_data.get('deputy_id')
                    deputy_interests = match_deputy_interests(selected_deputy_name, deputy_id, interests_df)
                    
                    display_interests_section(deputy_interests)
                
                with tabs[7]:
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
                                        if value and str(value).lower() != 'nan': st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else: st.write(otros_bienes)
                    else: st.info("No hay otros bienes declarados")
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 2rem;">
            Una aplicación desarrollada por <a href="https://x.com/Gsnchez" target="_blank" style="color: #667eea; text-decoration: none;">@Gsnchez</a> en X.
        </div>
        """,
        unsafe_allow_html=True
    )

# Main execution logic
if not st.session_state.disclaimer_accepted:
    show_disclaimer()
else:
    main_app()
