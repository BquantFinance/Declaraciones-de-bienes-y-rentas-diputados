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
import html

# Page configuration
st.set_page_config(
    page_title="Declaración de Bienes — Congreso de España",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# ─────────────────────────────────────────────
# DESIGN SYSTEM — "Diario Financiero" Editorial
# ─────────────────────────────────────────────
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
        
        :root {
            --ink: #0a1628;
            --ink-light: #1a2744;
            --ink-mid: #2a3a5c;
            --paper: #f5f0e8;
            --paper-dark: #e8e0d0;
            --paper-mid: #ede6da;
            --cream: #faf7f2;
            --gold: #c8a84e;
            --gold-light: #e4cc7a;
            --gold-dark: #a08030;
            --vermillion: #c03020;
            --vermillion-light: #e05040;
            --teal: #1a7a6d;
            --teal-light: #2aa090;
            --slate: #64748b;
            --slate-light: #94a3b8;
            --border: rgba(10, 22, 40, 0.08);
            --shadow-sm: 0 1px 3px rgba(10,22,40,0.06);
            --shadow-md: 0 4px 12px rgba(10,22,40,0.08);
            --shadow-lg: 0 12px 40px rgba(10,22,40,0.12);
            --shadow-xl: 0 24px 60px rgba(10,22,40,0.16);
            --radius-sm: 4px;
            --radius-md: 8px;
            --radius-lg: 12px;
        }
        
        /* ── Base ── */
        .stApp {
            background: var(--cream) !important;
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--ink);
        }
        
        .main .block-container {
            padding-top: 0.5rem;
            max-width: 1500px;
        }
        
        /* ── Masthead / Header ── */
        .masthead {
            text-align: center;
            padding: 2rem 1rem 1.5rem;
            border-bottom: 3px double var(--ink);
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .masthead::before {
            content: '';
            display: block;
            width: 100%;
            height: 1px;
            background: var(--ink);
            margin-bottom: 3px;
            opacity: 0.3;
        }
        
        .masthead-overline {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.65rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: var(--slate);
            margin-bottom: 0.25rem;
        }
        
        .masthead-title {
            font-family: 'DM Serif Display', Georgia, serif;
            font-size: 3rem;
            font-weight: 400;
            color: var(--ink);
            line-height: 1.1;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .masthead-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.85rem;
            color: var(--slate);
            margin-top: 0.5rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }
        
        .masthead-rule {
            width: 60px;
            height: 3px;
            background: var(--gold);
            margin: 0.75rem auto 0;
            border: none;
        }
        
        /* ── Navigation ── */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 0;
        }
        
        .stRadio > div > label {
            background: transparent !important;
            border: 1px solid var(--border) !important;
            border-radius: 0 !important;
            color: var(--ink) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.5px !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        
        .stRadio > div > label:first-child {
            border-radius: var(--radius-sm) 0 0 var(--radius-sm) !important;
        }
        
        .stRadio > div > label:last-child {
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
        }
        
        .stRadio > div > label:hover {
            background: var(--paper) !important;
            border-color: var(--gold) !important;
        }
        
        .stRadio > div > label[data-checked="true"],
        .stRadio > div [data-baseweb="radio"] input:checked + div {
            background: var(--ink) !important;
            color: var(--paper) !important;
            border-color: var(--ink) !important;
        }
        
        /* ── Typography ── */
        h1, h2, h3, h4, h5 {
            font-family: 'DM Serif Display', Georgia, serif !important;
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
            background: none !important;
            -webkit-background-clip: unset !important;
            background-clip: unset !important;
        }
        
        h1 {
            font-size: 2.2rem !important;
            font-weight: 400 !important;
            letter-spacing: -0.3px !important;
        }
        
        h2 {
            font-size: 1.6rem !important;
            font-weight: 400 !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
            font-weight: 400 !important;
        }
        
        p, li, span, div {
            color: var(--ink);
        }
        
        strong {
            color: var(--ink) !important;
            font-weight: 600 !important;
        }
        
        a {
            color: var(--teal) !important;
            text-decoration: none;
        }
        
        a:hover {
            color: var(--gold-dark) !important;
            text-decoration: underline;
        }
        
        /* ── Dividers ── */
        hr {
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 1rem 0 !important;
        }
        
        /* ── Metrics ── */
        div[data-testid="metric-container"] {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem 1.2rem;
            box-shadow: var(--shadow-sm);
            transition: all 0.25s ease;
        }
        
        div[data-testid="metric-container"]:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            border-color: var(--gold);
        }
        
        div[data-testid="metric-container"] label {
            color: var(--slate) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            font-weight: 600 !important;
        }
        
        div[data-testid="metric-container"] div[data-testid="metric-value"] {
            color: var(--ink) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }
        
        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: white;
            border-radius: var(--radius-md);
            padding: 4px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 38px;
            padding: 0 14px;
            background: transparent;
            border: none;
            border-radius: var(--radius-sm);
            color: var(--slate);
            font-family: 'DM Sans', sans-serif;
            font-size: 0.78rem;
            font-weight: 500;
            letter-spacing: 0.3px;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--ink);
            background: var(--paper);
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--ink) !important;
            color: white !important;
            font-weight: 600;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }
        
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }
        
        /* ── Input Fields ── */
        .stSelectbox > div > div,
        .stTextInput > div > div > input {
            background: white !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--ink) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease !important;
            box-shadow: var(--shadow-sm) !important;
        }
        
        .stSelectbox > div > div:hover,
        .stTextInput > div > div > input:hover {
            border-color: var(--gold) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        .stSelectbox > div > div:focus-within,
        .stTextInput > div > div > input:focus {
            border-color: var(--ink) !important;
            box-shadow: 0 0 0 3px rgba(10,22,40,0.08) !important;
        }
        
        /* Style selectbox label */
        .stSelectbox label, .stTextInput label {
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            color: var(--slate) !important;
            font-weight: 600 !important;
        }
        
        /* ── Buttons ── */
        .stButton > button {
            background: white !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--ink) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 1.2rem !important;
            box-shadow: var(--shadow-sm) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
            border-color: var(--gold) !important;
            background: var(--paper) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Primary button */
        .stButton > button[data-testid="baseButton-primary"] {
            background: var(--ink) !important;
            color: var(--paper) !important;
            border-color: var(--ink) !important;
            font-weight: 600 !important;
        }
        
        .stButton > button[data-testid="baseButton-primary"]:hover {
            background: var(--ink-light) !important;
        }
        
        /* Random button */
        .random-button-container {
            margin-top: 27px;
        }
        
        .random-button-container > div > button {
            background: var(--gold) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.3rem !important;
            padding: 0.55rem !important;
            box-shadow: 0 2px 8px rgba(200,168,78,0.3) !important;
            transition: all 0.25s ease !important;
        }
        
        .random-button-container > div > button:hover {
            transform: translateY(-2px) scale(1.05) !important;
            box-shadow: 0 6px 20px rgba(200,168,78,0.4) !important;
            background: var(--gold-dark) !important;
        }
        
        /* ── Alert Boxes ── */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: var(--radius-md) !important;
            font-family: 'DM Sans', sans-serif !important;
            border-left-width: 3px !important;
        }
        
        .stSuccess {
            background: rgba(26,122,109,0.06) !important;
            border-left-color: var(--teal) !important;
        }
        
        .stInfo {
            background: rgba(10,22,40,0.04) !important;
            border-left-color: var(--ink-mid) !important;
        }
        
        .stWarning {
            background: rgba(200,168,78,0.08) !important;
            border-left-color: var(--gold) !important;
        }
        
        .stError {
            background: rgba(192,48,32,0.06) !important;
            border-left-color: var(--vermillion) !important;
        }
        
        /* ── Expander ── */
        .streamlit-expanderHeader {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            color: var(--ink) !important;
            background: white !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }
        
        /* ── Deputy Profile Card ── */
        .profile-header {
            display: flex;
            gap: 2rem;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }
        
        .profile-photo-frame {
            position: relative;
            flex-shrink: 0;
        }
        
        .profile-photo {
            width: 200px;
            height: 250px;
            object-fit: cover;
            display: block;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            border: 3px solid white;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .profile-photo:hover {
            transform: scale(1.03);
            box-shadow: var(--shadow-xl);
        }
        
        .no-photo {
            width: 200px;
            height: 250px;
            background: var(--paper);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--slate);
            border-radius: var(--radius-md);
            border: 2px dashed rgba(10,22,40,0.15);
            font-size: 3rem;
        }
        
        .no-photo span {
            font-size: 0.8rem;
            margin-top: 8px;
            font-family: 'DM Sans', sans-serif;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* ── Badge Gallery ── */
        .image-gallery {
            display: flex;
            gap: 1.5rem;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .badges-container {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            align-items: center;
        }
        
        .badge-frame {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 10px;
            box-shadow: var(--shadow-sm);
            transition: all 0.25s ease;
        }
        
        .badge-frame:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            border-color: var(--gold);
        }
        
        .badge-frame img {
            width: 90px;
            height: 90px;
            object-fit: contain;
            display: block;
        }
        
        /* ── Info Grid ── */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.75rem;
            margin: 1rem 0;
        }
        
        .info-card {
            background: white;
            padding: 0.9rem 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: var(--gold);
        }
        
        .info-card-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.65rem;
            color: var(--slate);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }
        
        .info-card-value {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            color: var(--ink);
            font-weight: 500;
        }
        
        /* ── Social Links ── */
        .social-links {
            display: flex;
            gap: 0.6rem;
            margin-top: 0.75rem;
        }
        
        .social-link {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: white;
            border: 1px solid var(--border);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            text-decoration: none !important;
            transition: all 0.25s ease;
            box-shadow: var(--shadow-sm);
        }
        
        .social-link:hover {
            transform: translateY(-3px) scale(1.1);
            box-shadow: var(--shadow-md);
            border-color: var(--gold);
            background: var(--paper);
        }
        
        /* ── Screener Cards ── */
        .screener-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1rem 1.2rem;
            margin-bottom: 0.75rem;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 1.2rem;
            box-shadow: var(--shadow-sm);
        }
        
        .screener-card:hover {
            transform: translateX(6px);
            border-color: var(--gold);
            box-shadow: var(--shadow-md);
        }
        
        .screener-rank {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--slate);
            min-width: 50px;
            text-align: center;
            padding: 0.4rem;
            border-radius: var(--radius-sm);
            background: var(--paper);
        }
        
        .screener-rank.gold {
            background: linear-gradient(135deg, #c8a84e, #e4cc7a);
            color: white;
        }
        
        .screener-rank.silver {
            background: linear-gradient(135deg, #8a9bb0, #adb9c9);
            color: white;
        }
        
        .screener-rank.bronze {
            background: linear-gradient(135deg, #a07040, #c49060);
            color: white;
        }
        
        .screener-photo {
            width: 60px;
            height: 75px;
            object-fit: cover;
            border-radius: var(--radius-sm);
            box-shadow: var(--shadow-sm);
            border: 2px solid white;
        }
        
        .screener-photo-placeholder {
            width: 60px;
            height: 75px;
            background: var(--paper);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--slate-light);
            border-radius: var(--radius-sm);
            border: 1px dashed rgba(10,22,40,0.15);
            font-size: 1.5rem;
        }
        
        .screener-info {
            flex: 1;
            min-width: 0;
        }
        
        .screener-name {
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            color: var(--ink);
            margin-bottom: 0.15rem;
        }
        
        .screener-party {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            color: var(--slate);
        }
        
        .screener-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--ink);
            text-align: right;
            min-width: 140px;
        }
        
        .screener-value.positive {
            color: var(--teal);
        }
        
        .screener-value.negative {
            color: var(--vermillion);
        }
        
        /* ── Activity Cards ── */
        .activity-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 0.6rem;
            transition: all 0.2s ease;
            border-left: 3px solid var(--gold);
        }
        
        .activity-card:hover {
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }
        
        .activity-type-badge {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 3px;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        
        .badge-cargo {
            background: var(--ink);
            color: var(--paper);
        }
        
        .badge-actividad {
            background: var(--teal);
            color: white;
        }
        
        .badge-partido {
            background: var(--gold);
            color: white;
        }
        
        .badge-otros {
            background: var(--slate);
            color: white;
        }
        
        /* ── Salary Badge ── */
        .salary-badge {
            background: white;
            border: 1px solid var(--border);
            border-left: 4px solid var(--teal);
            border-radius: var(--radius-md);
            padding: 0.8rem 1.2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1rem;
        }
        
        .salary-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--slate);
            font-weight: 600;
        }
        
        .salary-amount {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--teal);
        }
        
        /* ── Deputy Name Header ── */
        .deputy-name {
            font-family: 'DM Serif Display', Georgia, serif;
            font-size: 2rem;
            color: var(--ink);
            margin-bottom: 0.5rem;
            line-height: 1.15;
            border-bottom: 2px solid var(--gold);
            padding-bottom: 0.5rem;
        }
        
        /* ── Section Titles ── */
        .section-title {
            font-family: 'DM Serif Display', Georgia, serif;
            font-size: 1.15rem;
            color: var(--ink);
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 0.75rem;
            margin-top: 0.5rem;
        }
        
        /* ── Disclaimer ── */
        .disclaimer-container {
            background: white;
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 2.5rem 3rem;
            margin: 1.5rem auto;
            max-width: 850px;
            box-shadow: var(--shadow-lg);
        }
        
        h1.disclaimer-title {
            font-family: 'DM Serif Display', Georgia, serif !important;
            font-size: 2rem !important;
            font-weight: 400 !important;
            color: var(--vermillion) !important;
            -webkit-text-fill-color: var(--vermillion) !important;
            text-align: center;
            margin-bottom: 1.5rem !important;
            border-bottom: 2px solid var(--vermillion);
            padding-bottom: 1rem;
        }
        
        h3.disclaimer-section-title {
            font-family: 'DM Serif Display', Georgia, serif !important;
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
            margin-top: 2rem !important;
            margin-bottom: 0.75rem !important;
            font-size: 1.1rem !important;
            font-weight: 400 !important;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.4rem;
        }
        
        /* ── Progress Bars ── */
        .stProgress > div > div {
            background-color: var(--paper) !important;
            border-radius: var(--radius-sm) !important;
        }
        
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--teal), var(--teal-light)) !important;
            border-radius: var(--radius-sm) !important;
        }
        
        /* ── Footer ── */
        .app-footer {
            text-align: center;
            padding: 2rem 0;
            margin-top: 2rem;
            border-top: 1px solid var(--border);
        }
        
        .app-footer a {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            color: var(--slate) !important;
            text-decoration: none;
            transition: color 0.2s ease;
        }
        
        .app-footer a:hover {
            color: var(--gold-dark) !important;
        }
        
        /* ── Scrollbar ── */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--paper);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--slate-light);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--slate);
        }
        
        /* ── Hide Streamlit chrome ── */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ── Responsive ── */
        @media (max-width: 768px) {
            .masthead-title { font-size: 2rem; }
            .info-grid { grid-template-columns: 1fr; }
            .image-gallery { flex-direction: column; }
            .disclaimer-container { padding: 1.5rem; margin: 1rem; }
            .deputy-name { font-size: 1.5rem; }
            .salary-amount { font-size: 1.2rem; }
            .profile-photo, .no-photo { width: 160px; height: 200px; }
        }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING (unchanged logic)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('deputies_with_salaries.csv', encoding='utf-8-sig')
        path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
        for col in path_columns:
            if col in df.columns:
                df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'deputies_with_salaries.csv'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_interests_data():
    try:
        df = pd.read_csv('deputies_economic_interests.csv', encoding='utf-8-sig')
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


# ─────────────────────────────────────────────
# UTILITY FUNCTIONS (all logic preserved)
# ─────────────────────────────────────────────
def normalize_name(name):
    if pd.isna(name):
        return ""
    name = str(name)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return ' '.join(name.lower().split())

def normalize_deputy_id(deputy_id):
    if pd.isna(deputy_id):
        return None
    try:
        return int(deputy_id)
    except (ValueError, TypeError):
        return None

def match_deputy_interests(deputy_id, interests_df):
    if interests_df.empty:
        return pd.DataFrame()
    if pd.isna(deputy_id):
        return pd.DataFrame()
    matches = interests_df[interests_df['metadata_deputy_id'] == deputy_id]
    return matches

def parse_json_field(field_value):
    if pd.isna(field_value) or field_value in ('[]', ''):
        return []
    try:
        cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value))
        return json.loads(cleaned_value)
    except:
        return []

def format_currency(value):
    if not isinstance(value, (int, float)):
        return "0€"
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted}€"
    else:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"

def format_currency_full(value):
    if not isinstance(value, (int, float)):
        return "0,00 €"
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted} €"
    else:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} €"

def extract_irpf_value(value):
    if pd.isna(value) or value == '':
        return 0
    if isinstance(value, (int, float)):
        value = float(value)
        value_str = str(value)
        if value > 200000:
            if '.' in value_str:
                parts = value_str.split('.')
                full_digits = parts[0] + parts[1].rstrip('0')
                if len(full_digits) >= 7:
                    corrected = full_digits[:5] + '.' + full_digits[5:7]
                    return float(corrected)
            value_str_int = str(int(value))
            if len(value_str_int) >= 3:
                corrected = value_str_int[:-2] + '.' + value_str_int[-2:]
                return float(corrected)
        if 10 < value < 200000 and '.' in value_str:
            parts = value_str.split('.')
            if len(parts) == 2:
                integer_part = parts[0]
                decimal_part = parts[1]
                if len(decimal_part) == 3:
                    return float(integer_part + decimal_part)
                elif len(decimal_part) >= 4:
                    combined = integer_part + decimal_part
                    corrected = combined[:-2] + '.' + combined[-2:]
                    return float(corrected)
                elif len(decimal_part) == 2 and value < 1000:
                    return float(integer_part + decimal_part)
        if 20 < value < 100 and '.' in value_str:
            return float(value_str.replace('.', ''))
        return value
    value_str = str(value).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    numeric_part = re.search(r'[\d.,]+', value_str)
    if numeric_part:
        num_str = numeric_part.group(0)
        if ',' in num_str:
            return float(num_str.replace('.', '').replace(',', '.'))
        else:
            return float(num_str.replace(',', ''))
    return 0

def extract_debt_account_value(value_str):
    if pd.isna(value_str) or value_str == '':
        return 0
    if isinstance(value_str, (int, float)):
        value = float(value_str)
        if value > 1000 and value == int(value):
            value_str_int = str(int(value))
            if len(value_str_int) >= 6:
                corrected = value_str_int[:-3] + '.' + value_str_int[-3:]
                corrected_value = float(corrected)
                if corrected_value < 500000 and value > 500000:
                    return corrected_value
        return value
    value_str = str(value_str).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    numeric_part = re.search(r'[\d.,]+', value_str)
    if not numeric_part:
        return 0
    try:
        num_str = numeric_part.group(0)
        dot_count = num_str.count('.')
        comma_count = num_str.count(',')
        if comma_count > 0:
            return float(num_str.replace('.', '').replace(',', '.'))
        if dot_count > 0 and comma_count == 0:
            if dot_count > 1:
                parts = num_str.split('.')
                if len(parts[-1]) <= 2:
                    integer_part = ''.join(parts[:-1])
                    decimal_part = parts[-1]
                    return float(f"{integer_part}.{decimal_part}")
                else:
                    return float(num_str.replace('.', ''))
            parts = num_str.split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
            if len(decimal_part) == 3:
                if decimal_part.endswith('00') or decimal_part == '000':
                    return float(num_str.replace('.', ''))
                elif int(integer_part) < 1000:
                    return float(num_str.replace('.', ''))
                else:
                    return float(num_str.replace('.', ''))
            elif 4 <= len(decimal_part) <= 5:
                combined = integer_part + decimal_part
                corrected = combined[:-2] + '.' + combined[-2:]
                return float(corrected)
            elif len(decimal_part) <= 2:
                return float(num_str)
            else:
                return float(num_str.replace('.', ''))
        return float(num_str)
    except (ValueError, TypeError):
        return 0
    return 0


# ─────────────────────────────────────────────
# UI COMPONENTS — redesigned
# ─────────────────────────────────────────────
def render_masthead():
    """Render the editorial masthead header"""
    st.markdown("""
    <div class="masthead">
        <div class="masthead-overline">Congreso de los Diputados · XV Legislatura</div>
        <h1 class="masthead-title">Declaración de Bienes</h1>
        <div class="masthead-subtitle">Análisis Interactivo de Transparencia Financiera Parlamentaria</div>
        <hr class="masthead-rule">
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render editorial footer"""
    st.markdown("""
    <div class="app-footer">
        <a href="https://x.com/Gsnchez" target="_blank">Desarrollado por @Gsnchez · Fuente: Congreso de los Diputados</a>
    </div>
    """, unsafe_allow_html=True)

def create_image_gallery(deputy_data):
    """Create clean editorial image gallery"""
    gallery_html = '<div class="image-gallery">'
    
    # Main photo
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<div class="profile-photo-frame"><img src="data:image/jpeg;base64,{img_data}" class="profile-photo" alt="Foto del diputado"></div>'
    else:
        gallery_html += '<div class="no-photo">👤<span>Sin Foto</span></div>'
    
    # Badges
    gallery_html += '<div class="badges-container">'
    
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<div class="badge-frame"><img src="data:image/png;base64,{img_data}" alt="Logo del partido"></div>'
    
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<div class="badge-frame"><img src="data:image/png;base64,{img_data}" alt="Posición en hemiciclo"></div>'
    
    gallery_html += '</div></div>'
    return gallery_html

def get_deputy_photo_html(photo_path, size="small"):
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        try:
            with open(photo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" class="screener-photo" alt="Foto">'
        except:
            return '<div class="screener-photo-placeholder">👤</div>'
    else:
        return '<div class="screener-photo-placeholder">👤</div>'


def display_interests_section(deputy_interests):
    """Display interests with editorial styling"""
    if deputy_interests.empty:
        st.info("No hay información de registro de intereses disponible para este diputado.")
        return
    
    st.markdown(f'<div class="section-title">📋 Registro de Intereses — {len(deputy_interests)} Registros</div>', unsafe_allow_html=True)
    
    section_groups = deputy_interests.groupby('seccion')
    
    for section_name, section_data in section_groups:
        section_titles = {
            'actividades': '🏛 Actividades',
            'donaciones': '🎁 Donaciones y Obsequios',
            'fundaciones': '🏢 Fundaciones y Asociaciones',
            'otros_intereses': '📝 Otros Intereses'
        }
        
        section_title = section_titles.get(section_name, f'📌 {section_name.replace("_", " ").title()}')
        
        with st.expander(f"{section_title} ({len(section_data)})", expanded=(section_name == 'actividades')):
            if section_name == 'actividades':
                for idx, row in section_data.iterrows():
                    activity_sector = row.get('actividad_sector', 'Sin especificar')
                    activity_empleador = row.get('actividad_empleador', '')
                    activity_periodo = row.get('actividad_periodo', '')
                    activity_desc = row.get('actividad_descripcion', '')
                    
                    badge_class = 'badge-otros'
                    if pd.notna(activity_sector):
                        s = str(activity_sector).lower()
                        if 'cargo' in s and 'público' in s:
                            badge_class = 'badge-cargo'
                        elif 'partido' in s or 'grupo parlamentario' in s:
                            badge_class = 'badge-partido'
                        elif 'privada' in s or 'docente' in s:
                            badge_class = 'badge-actividad'
                    
                    card_html = f'<div class="activity-card">'
                    card_html += f'<div class="activity-type-badge {badge_class}">{html.escape(str(activity_sector)) if pd.notna(activity_sector) else "Sin especificar"}</div>'
                    if pd.notna(activity_empleador) and str(activity_empleador).strip():
                        card_html += f'<p style="color: var(--ink); font-weight: 600; margin: 0.4rem 0; font-size: 0.95rem;">🏢 {html.escape(str(activity_empleador))}</p>'
                    if pd.notna(activity_desc) and str(activity_desc).strip():
                        card_html += f'<p style="color: var(--ink); margin: 0.3rem 0; font-size: 0.9rem; opacity: 0.8;">{html.escape(str(activity_desc))}</p>'
                    if pd.notna(activity_periodo) and str(activity_periodo).strip():
                        card_html += f'<p style="color: var(--slate); font-size: 0.8rem; margin-top: 0.3rem; font-family: JetBrains Mono, monospace;">📅 {html.escape(str(activity_periodo))}</p>'
                    card_html += '</div>'
                    st.markdown(card_html, unsafe_allow_html=True)
            
            elif section_name == 'otros_intereses':
                for idx, row in section_data.iterrows():
                    otros_texto = row.get('otros_texto', '')
                    if pd.notna(otros_texto) and str(otros_texto).strip():
                        texto_escaped = html.escape(str(otros_texto))
                        st.markdown(f'<div class="activity-card"><p style="color: var(--ink); white-space: pre-wrap; font-size: 0.9rem;">{texto_escaped}</p></div>', unsafe_allow_html=True)
            
            elif section_name == 'donaciones':
                for idx, row in section_data.iterrows():
                    benefactor = row.get('donacion_benefactor', '')
                    descripcion = row.get('donacion_descripcion', '')
                    if pd.notna(benefactor) or pd.notna(descripcion):
                        card_html = '<div class="activity-card">'
                        card_html += '<div class="activity-type-badge badge-otros">Donación</div>'
                        if pd.notna(benefactor) and str(benefactor).strip():
                            card_html += f'<p style="color: var(--ink); font-weight: 600; margin: 0.4rem 0;">🎁 De: {html.escape(str(benefactor))}</p>'
                        if pd.notna(descripcion) and str(descripcion).strip():
                            card_html += f'<p style="color: var(--ink); margin: 0.3rem 0; opacity: 0.8;">{html.escape(str(descripcion))}</p>'
                        card_html += '</div>'
                        st.markdown(card_html, unsafe_allow_html=True)
            
            elif section_name == 'fundaciones':
                for idx, row in section_data.iterrows():
                    destinatario = row.get('fundacion_destinatario', '')
                    descripcion = row.get('fundacion_descripcion', '')
                    if pd.notna(destinatario) or pd.notna(descripcion):
                        card_html = '<div class="activity-card">'
                        card_html += '<div class="activity-type-badge badge-actividad">Fundación</div>'
                        if pd.notna(destinatario) and str(destinatario).strip():
                            card_html += f'<p style="color: var(--ink); font-weight: 600; margin: 0.4rem 0;">🏢 {html.escape(str(destinatario))}</p>'
                        if pd.notna(descripcion) and str(descripcion).strip():
                            card_html += f'<p style="color: var(--ink); margin: 0.3rem 0; opacity: 0.8;">{html.escape(str(descripcion))}</p>'
                        card_html += '</div>'
                        st.markdown(card_html, unsafe_allow_html=True)
            
            else:
                for idx, row in section_data.iterrows():
                    st.markdown(f'<div class="activity-card"><p style="color: var(--ink);">Registro de {section_name.replace("_", " ")}</p></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SCREENER
# ─────────────────────────────────────────────
def prepare_screener_data(df):
    """Prepare data for screener — all logic preserved"""
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
            'salary': 0, 'irpf': 0, 'properties_count': 0, 'vehicles_count': 0,
            'debt_total': 0, 'accounts_balance': 0, 'max_account': 0,
            'max_debt': 0, 'max_debt_original': 0, 'total_assets': 0,
        }
        
        salary = row.get('scraped_salary', None)
        if pd.notna(salary) and salary:
            try: deputy_info['salary'] = float(salary)
            except: deputy_info['salary'] = 0
        
        deputy_info['irpf'] = extract_irpf_value(row.get('irpf_cantidad_pagada', 0))
        
        urban_properties = parse_json_field(row['bienes_patrimoniales_inmuebles_urbanos'])
        rustic_properties = parse_json_field(row.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))
        deputy_info['properties_count'] = len(urban_properties) + len(rustic_properties)
        
        vehicles = parse_json_field(row['vehiculos'])
        deputy_info['vehicles_count'] = len(vehicles)
        
        debts = parse_json_field(row['deudas_y_obligaciones'])
        debt_pending, debt_original = [], []
        for debt in debts:
            if isinstance(debt, dict):
                pending = extract_debt_account_value(debt.get('saldo_pendiente', 0))
                original = extract_debt_account_value(debt.get('importe_concedido', 0))
                if pending > 0: debt_pending.append(pending)
                if original > 0: debt_original.append(original)
        deputy_info['debt_total'] = sum(debt_pending)
        deputy_info['max_debt'] = max(debt_pending) if debt_pending else 0
        deputy_info['max_debt_original'] = max(debt_original) if debt_original else 0
        
        accounts = parse_json_field(row['depositos_y_cuentas_cuentas'])
        account_balances = []
        for account in accounts:
            if isinstance(account, dict):
                saldo = extract_debt_account_value(account.get('saldo', 0))
                if saldo > 0: account_balances.append(saldo)
        deputy_info['accounts_balance'] = sum(account_balances)
        deputy_info['max_account'] = max(account_balances) if account_balances else 0
        
        total_assets = deputy_info['accounts_balance']
        acciones = parse_json_field(row.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
        for accion in acciones:
            if isinstance(accion, dict):
                total_assets += extract_debt_account_value(accion.get('valor', 0))
        deuda_publica = parse_json_field(row.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
        for valor in deuda_publica:
            if isinstance(valor, dict):
                total_assets += extract_debt_account_value(valor.get('valor', 0))
        deputy_info['total_assets'] = total_assets
        
        screener_data.append(deputy_info)
    
    return pd.DataFrame(screener_data)

def display_screener_card(rank, deputy_info, metric_name, metric_value, value_class=""):
    rank_class = ""
    medal = ""
    if rank == 1: rank_class = "gold"; medal = "🥇 "
    elif rank == 2: rank_class = "silver"; medal = "🥈 "
    elif rank == 3: rank_class = "bronze"; medal = "🥉 "
    
    photo_html = get_deputy_photo_html(deputy_info['photo_path'])
    
    st.markdown(f'''
    <div class="screener-card">
        <div class="screener-rank {rank_class}">{medal}#{rank}</div>
        {photo_html}
        <div class="screener-info">
            <div class="screener-name">{deputy_info['name']}</div>
            <div class="screener-party">{deputy_info['party']}</div>
        </div>
        <div class="screener-value {value_class}">{metric_value}</div>
    </div>
    ''', unsafe_allow_html=True)

def show_screener(df):
    st.markdown('<div class="section-title" style="font-size: 1.4rem; text-align: center;">🔍 Screening de Diputados</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: var(--slate); font-size: 0.9rem; margin-bottom: 1rem;">Explora y compara las métricas financieras de los diputados</p>', unsafe_allow_html=True)
    
    screener_df = prepare_screener_data(df)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metric_options = {
            '💰 Salario Anual': ('salary', 'positive', 'currency'),
            '💵 IRPF Pagado': ('irpf', 'positive', 'currency'),
            '🏠 Número de Inmuebles': ('properties_count', 'positive', 'number'),
            '🚗 Número de Vehículos': ('vehicles_count', 'positive', 'number'),
            '💳 Deuda Total Pendiente': ('debt_total', 'negative', 'currency'),
            '⚠️ Préstamo Más Alto (Pendiente)': ('max_debt', 'negative', 'currency'),
            '📊 Préstamo Más Alto (Original)': ('max_debt_original', 'negative', 'currency'),
            '🏦 Saldo Total en Cuentas': ('accounts_balance', 'positive', 'currency'),
            '💎 Cuenta Más Grande': ('max_account', 'positive', 'currency'),
            '💼 Total Activos Líquidos': ('total_assets', 'positive', 'currency'),
        }
        selected_metric_name = st.selectbox("Seleccionar Métrica:", list(metric_options.keys()))
    
    with col2:
        ranking_type = st.radio("Ranking:", ["🔝 Top 10", "🔻 Bottom 10"], horizontal=True)
    
    metric_column, value_class, format_type = metric_options[selected_metric_name]
    
    st.markdown("---")
    
    ascending = ranking_type == "🔻 Bottom 10"
    top_deputies = screener_df.nlargest(10, metric_column) if not ascending else screener_df.nsmallest(10, metric_column)
    
    # Summary stats
    col1, col2 = st.columns(2)
    with col1:
        avg_value = screener_df[metric_column].mean()
        st.metric("Promedio", format_currency(avg_value) if format_type == 'currency' else f"{avg_value:.1f}")
    with col2:
        max_value = screener_df[metric_column].max()
        st.metric("Máximo", format_currency(max_value) if format_type == 'currency' else f"{int(max_value)}")
    
    st.markdown("---")
    
    for idx, (_, deputy) in enumerate(top_deputies.iterrows(), 1):
        metric_val = deputy[metric_column]
        formatted_value = format_currency_full(metric_val) if format_type == 'currency' else f"{int(metric_val)}"
        display_screener_card(idx, deputy, selected_metric_name, formatted_value, value_class)
    
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Visualización Comparativa</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    text_values = top_deputies[metric_column].apply(lambda x: format_currency(x)) if format_type == 'currency' else top_deputies[metric_column].apply(lambda x: f"{int(x)}")
    
    fig.add_trace(go.Bar(
        x=top_deputies['name'],
        y=top_deputies[metric_column],
        marker=dict(
            color=top_deputies[metric_column],
            colorscale=[[0, '#1a7a6d'], [0.5, '#c8a84e'], [1, '#c03020']],
            showscale=True,
            colorbar=dict(
                tickfont=dict(color='#0a1628', family='JetBrains Mono'),
                title=dict(font=dict(color='#64748b', family='DM Sans', size=11))
            )
        ),
        text=text_values,
        textposition='auto',
        textfont=dict(family='JetBrains Mono', size=11, color='white'),
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{selected_metric_name}",
            font=dict(family='DM Serif Display', size=18, color='#0a1628')
        ),
        xaxis_title="",
        yaxis_title="",
        template="plotly_white",
        height=450,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0a1628', family='DM Sans'),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(family='DM Sans', size=10, color='#64748b'),
            gridcolor='rgba(10,22,40,0.05)',
        ),
        yaxis=dict(
            tickfont=dict(family='JetBrains Mono', size=10, color='#64748b'),
            gridcolor='rgba(10,22,40,0.06)',
        ),
        margin=dict(t=50, b=100),
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# DISCLAIMER
# ─────────────────────────────────────────────
def show_disclaimer():
    apply_css()
    _, col2, _ = st.columns([1, 4, 1])
    
    with col2:
        st.markdown('<div class="disclaimer-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="disclaimer-title">⚖️ Descargo de Responsabilidad Legal</h1>', unsafe_allow_html=True)
        
        st.write("**IMPORTANTE: LEA ATENTAMENTE ANTES DE USAR ESTA APLICACIÓN**")
        st.write('Esta aplicación web de consulta de información pública ("la Aplicación") recopila, procesa y presenta datos obtenidos de fuentes públicas disponibles en la página web oficial del Congreso de los Diputados de España, incluyendo documentos en formato PDF y otros registros de acceso público.')
        
        st.markdown('<h3 class="disclaimer-section-title">📋 Naturaleza y Origen de la Información</h3>', unsafe_allow_html=True)
        st.write("La información mostrada en esta Aplicación proviene exclusivamente de:")
        st.markdown("""
        - Declaraciones de bienes y rentas publicadas en el Portal de Transparencia del Congreso de los Diputados
        - Registros públicos de actividades e intereses de los parlamentarios
        - Documentación oficial de acceso público disponible en www.congreso.es
        """)
        
        st.markdown('<h3 class="disclaimer-section-title">⚠️ Descargo de Responsabilidad</h3>', unsafe_allow_html=True)
        st.write("**La Aplicación no pertenece, no está vinculada, afiliada, patrocinada, avalada ni autorizada de ninguna manera por el Congreso de los Diputados**, ni por ninguna institución gubernamental o entidad pública española. Es un proyecto independiente desarrollado con fines informativos y de acceso facilitado a información pública.")
        st.write("El contenido mostrado se ofrece únicamente con fines informativos, educativos y de consulta pública. Aunque se realizan esfuerzos razonables para garantizar la precisión y actualización de los datos:")
        st.markdown("""
        - La Aplicación puede contener **errores, inexactitudes, omisiones o información desactualizada**
        - Los datos pueden no reflejar los cambios más recientes en las declaraciones
        - Pueden existir discrepancias entre la información mostrada y los documentos originales
        - La interpretación o procesamiento automatizado de los datos puede introducir errores involuntarios
        """)
        
        st.markdown('<h3 class="disclaimer-section-title">📌 Limitación de Responsabilidad</h3>', unsafe_allow_html=True)
        st.write("Los desarrolladores y operadores de esta Aplicación:")
        st.markdown("""
        - No garantizan la exactitud, integridad, actualidad o idoneidad de la información para ningún propósito particular
        - No asumen responsabilidad por decisiones tomadas basándose en la información aquí presentada
        - No se responsabilizan de daños directos, indirectos, incidentales o consecuentes derivados del uso de la Aplicación
        - Se reservan el derecho de modificar, suspender o discontinuar el servicio sin previo aviso
        """)
        
        st.markdown('<h3 class="disclaimer-section-title">✅ Fuente Oficial</h3>', unsafe_allow_html=True)
        st.write("**Para la consulta oficial, íntegra, auténtica y legalmente válida de las declaraciones de bienes y rentas de los diputados, se debe acudir directamente a:**")
        st.info("🔗 **Portal de Transparencia del Congreso de los Diputados:** [www.congreso.es](https://www.congreso.es)")
        
        st.markdown('<h3 class="disclaimer-section-title">👤 Privacidad y Datos Personales</h3>', unsafe_allow_html=True)
        st.write("Esta Aplicación muestra únicamente información que ya es de dominio público y ha sido publicada oficialmente por el Congreso de los Diputados en cumplimiento de las obligaciones de transparencia establecidas en la legislación española.")
        
        st.markdown('<h3 class="disclaimer-section-title">⚖️ Aceptación de Términos</h3>', unsafe_allow_html=True)
        st.write('Al hacer clic en "ACEPTO Y ENTIENDO" y utilizar esta Aplicación, usted reconoce que:')
        st.markdown("""
        - Ha leído y comprendido este descargo de responsabilidad en su totalidad
        - Acepta usar la Aplicación bajo su propio riesgo
        - Comprende las limitaciones de la información presentada
        - Se compromete a verificar cualquier información crítica en las fuentes oficiales
        """)
        
        st.warning("**ADVERTENCIA FINAL:** El uso de esta aplicación es responsabilidad exclusiva del usuario. Si no está de acuerdo con estos términos, por favor no utilice la Aplicación.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.info("💡 **Recomendación:** Para una experiencia óptima, usa esta aplicación en un ordenador.", icon="✨")
        
        _, btn_col, _ = st.columns([1, 2, 1])
        if btn_col.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()
        
        st.error("Para usar esta aplicación debe aceptar los términos y condiciones.")
        st.markdown("---")
        render_footer()


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main_app():
    apply_css()
    render_masthead()
    
    df = load_data()
    interests_df = load_interests_data()
    
    if df.empty:
        st.stop()
    
    # Navigation
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
        unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
        
        search_col, metric_col, random_col = st.columns([8, 2, 1])
        
        with search_col:
            search_term = st.text_input(
                "Buscar diputado",
                placeholder="🔍 Buscar diputado por nombre...",
                key="search",
                label_visibility="collapsed"
            )
        
        filtered_deputies = unique_deputies.copy()
        if search_term:
            filtered_deputies = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
        
        with metric_col:
            st.metric("Diputados", len(filtered_deputies))
        
        deputy_names = filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist()
        
        with random_col:
            st.markdown('<div class="random-button-container">', unsafe_allow_html=True)
            if st.button("🎲", use_container_width=True, help="Aleatorio", key="random_deputy"):
                if deputy_names:
                    st.session_state.selected_deputy_name = random.choice(deputy_names)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if not deputy_names:
            st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
        else:
            if 'selected_deputy_name' not in st.session_state or st.session_state.selected_deputy_name not in deputy_names:
                st.session_state.selected_deputy_name = deputy_names[0]
            
            try:
                selected_index = deputy_names.index(st.session_state.selected_deputy_name)
            except (ValueError, IndexError):
                selected_index = 0
            
            def format_deputy_option(name):
                try:
                    deputy_row = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'] == name]
                    if not deputy_row.empty:
                        salary = deputy_row['scraped_salary'].iloc[0]
                        if pd.notna(salary) and salary:
                            formatted_salary = f"{float(salary):,.0f}".replace(",", ".")
                            return f"{name}  ·  {formatted_salary}€"
                except:
                    pass
                return name
            
            selected_deputy_name = st.selectbox(
                "Seleccionar Diputado:",
                deputy_names,
                index=selected_index,
                format_func=format_deputy_option
            )
            
            st.session_state.selected_deputy_name = selected_deputy_name
            
            deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name].sort_values(by='source_file', ascending=True)
            
            if len(deputy_declarations) > 1:
                st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
                
                declaration_options = []
                for i, (idx, row) in enumerate(deputy_declarations.iterrows()):
                    declaration_number = i + 1
                    label_parts = [f"Declaración {declaration_number}"]
                    
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
                    
                    label_parts.append(f"· {doc_date_str}")
                    
                    observaciones = row.get('observaciones', '')
                    if pd.notna(observaciones) and ('modificación' in observaciones.lower() or 'remito a' in observaciones.lower() or 'actualizar' in observaciones.lower()):
                        label_parts.append("[Mod.]")
                    
                    declaration_options.append((idx, " ".join(label_parts)))
                
                selected_idx = st.selectbox(
                    "Seleccionar Declaración:",
                    [opt[0] for opt in declaration_options],
                    format_func=lambda x: next((opt[1] for opt in declaration_options if opt[0] == x), "Seleccionar")
                )
                deputy_data = deputy_declarations.loc[selected_idx]
            else:
                deputy_data = deputy_declarations.iloc[0]
            
            st.markdown("---")
            
            # ── PROFILE LAYOUT ──
            col_left, col_right = st.columns([1.5, 2])
            
            with col_left:
                st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
                
                st.markdown('<div class="section-title">📋 Información Personal</div>', unsafe_allow_html=True)
                
                info_html = '<div class="info-grid">'
                personal_fields = [
                    ('Cargo', 'informacion_personal_cargo', 'Diputado'),
                    ('Circunscripción', 'informacion_personal_circunscripcion', None),
                    ('Estado Civil', 'informacion_personal_estado_civil', None),
                    ('Régimen Económico', 'informacion_personal_regimen_economico_matrimonial', None),
                    ('Fecha Elección', 'informacion_personal_fecha_eleccion', None),
                    ('Presentación Credencial', 'informacion_personal_fecha_presentacion_credencial', None),
                ]
                
                for label, field, default in personal_fields:
                    value = deputy_data.get(field, default)
                    if value and str(value).lower() != 'nan':
                        if not value and default: value = default
                        info_html += f'<div class="info-card"><div class="info-card-label">{label}</div><div class="info-card-value">{value}</div></div>'
                
                info_html += '</div>'
                st.markdown(info_html, unsafe_allow_html=True)
                
                # Social links
                social_links = {"𝕏": deputy_data.get('twitter'), "📘": deputy_data.get('facebook'), "📸": deputy_data.get('instagram'), "🌐": deputy_data.get('website')}
                valid_links = {emoji: url for emoji, url in social_links.items() if pd.notna(url) and str(url).lower() != 'nan'}
                
                if valid_links:
                    st.markdown('<div class="section-title" style="margin-top: 1rem;">🌐 Redes Sociales</div>', unsafe_allow_html=True)
                    social_html = '<div class="social-links">'
                    emoji_titles = {"𝕏": "X (Twitter)", "📘": "Facebook", "📸": "Instagram", "🌐": "Sitio Web"}
                    for emoji, url in valid_links.items():
                        title = emoji_titles.get(emoji, "")
                        social_html += f'<a href="{url}" target="_blank" class="social-link" title="{title}">{emoji}</a>'
                    social_html += '</div>'
                    st.markdown(social_html, unsafe_allow_html=True)
                
                observaciones = deputy_data.get('observaciones', '')
                if observaciones and str(observaciones).lower() != 'nan':
                    st.markdown('<div class="section-title" style="margin-top: 1rem;">📝 Observaciones</div>', unsafe_allow_html=True)
                    st.info(observaciones)
            
            with col_right:
                # Deputy name
                name = deputy_data['informacion_personal_nombre_y_apellidos']
                st.markdown(f'<div class="deputy-name">{name}</div>', unsafe_allow_html=True)
                
                # Salary badge
                salary = deputy_data.get('scraped_salary', None)
                if pd.notna(salary) and salary:
                    formatted_salary = f"{float(salary):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    st.markdown(f'''
                    <div class="salary-badge">
                        <div class="salary-label">Salario Anual</div>
                        <div class="salary-amount">{formatted_salary} €</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown('''
                    <div class="salary-badge" style="border-left-color: var(--slate-light);">
                        <div class="salary-label">Salario Anual</div>
                        <div class="salary-amount" style="color: var(--slate-light);">No disponible</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Key metrics
                st.markdown('<div class="section-title">📊 Datos Clave</div>', unsafe_allow_html=True)
                
                m1, m2, m3, m4, m5 = st.columns(5)
                
                if pd.notna(deputy_data.get('scraped_salary')) and deputy_data.get('scraped_salary'):
                    formatted_salary = f"{float(deputy_data['scraped_salary']):,.0f}".replace(",", ".")
                    m1.metric("Salario", f"{formatted_salary}€")
                else:
                    m1.metric("Salario", "N/D")
                
                irpf = extract_irpf_value(deputy_data.get('irpf_cantidad_pagada', 0))
                m2.metric("IRPF", format_currency(irpf))
                
                urban_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
                rustic_properties = len(parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]')))
                m3.metric("Inmuebles", urban_properties + rustic_properties)
                
                vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
                m4.metric("Vehículos", vehicles_count)
                
                debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
                m5.metric("Deudas", len(debts))
                
                st.markdown("---")
                
                # ── TABS ──
                tabs = st.tabs(["💵 Ingresos", "🏠 Inmuebles", "💼 Sociedades", "💰 Activos", "🚗 Vehículos", "💳 Deudas", "📋 Actividades", "📄 Otros"])
                
                with tabs[0]:
                    st.markdown('<div class="section-title">💵 Fuentes de Ingresos</div>', unsafe_allow_html=True)
                    st.info(f"**IRPF Pagado (Declarado): {format_currency_full(irpf)}**")
                    
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### Salarios")
                        salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                        if salaries:
                            for i, salary in enumerate(salaries):
                                if isinstance(salary, dict):
                                    concepto = salary.get('concepto', f'Ingreso #{i+1}')
                                    if str(concepto).lower() == 'nan': concepto = f'Ingreso #{i+1}'
                                    amount = extract_debt_account_value(salary.get('euros'))
                                    st.info(f"**{concepto}**")
                                    st.markdown(f"→ **{format_currency_full(amount)}**")
                        else:
                            st.info("Sin salarios declarados")
                        
                        st.markdown("##### Otras Rentas")
                        otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', ''))
                        if otras:
                            for item in otras:
                                if isinstance(item, dict):
                                    concepto = item.get('concepto', 'Otra renta')
                                    importe = extract_debt_account_value(item.get('euros', 0))
                                    if importe > 0:
                                        st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                        else:
                            st.info("Sin otras rentas")
                    
                    with tcol2:
                        st.markdown("##### Dividendos y Participaciones")
                        dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                        if dividends:
                            for div in dividends:
                                if isinstance(div, dict):
                                    concepto = div.get('concepto', 'Inversión')
                                    if str(concepto).lower() == 'nan': concepto = 'Inversión'
                                    st.markdown(f"**📊 {concepto}**")
                                    rendimientos = extract_debt_account_value(div.get('euros'))
                                    if rendimientos > 0:
                                        st.markdown(f"→ **{format_currency_full(rendimientos)}**")
                        else:
                            st.info("Sin dividendos")
                        
                        st.markdown("##### Intereses Financieros")
                        intereses = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', ''))
                        if intereses:
                            for item in intereses:
                                if isinstance(item, dict):
                                    concepto = item.get('concepto', 'Interés')
                                    importe = extract_debt_account_value(item.get('euros', 0))
                                    if importe > 0:
                                        st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                        else:
                            st.info("Sin intereses financieros")
                
                with tabs[1]:
                    st.markdown('<div class="section-title">🏠 Bienes Inmuebles</div>', unsafe_allow_html=True)
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### Inmuebles Urbanos")
                        urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                        if urban:
                            for i, prop in enumerate(urban):
                                if isinstance(prop, dict):
                                    st.markdown(f"**📍 Inmueble #{i+1}**")
                                    for key, value in prop.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else:
                            st.info("Sin inmuebles urbanos")
                    with tcol2:
                        st.markdown("##### Inmuebles Rústicos")
                        rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                        if rusticos:
                            for i, prop in enumerate(rusticos):
                                if isinstance(prop, dict):
                                    st.markdown(f"**🚜 Inmueble #{i+1}**")
                                    for key, value in prop.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else:
                            st.info("Sin inmuebles rústicos")
                
                with tabs[2]:
                    st.markdown('<div class="section-title">💼 Sociedades y Participaciones</div>', unsafe_allow_html=True)
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### Sociedades No Cotizadas")
                        sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                        if sociedades:
                            for i, soc in enumerate(sociedades):
                                if isinstance(soc, dict):
                                    st.markdown(f"**🏭 Sociedad #{i+1}**")
                                    for key, value in soc.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else:
                            st.info("Sin sociedades no cotizadas")
                    with tcol2:
                        st.markdown("##### Participaciones >5%")
                        participaciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                        if participaciones:
                            for i, part in enumerate(participaciones):
                                if isinstance(part, dict):
                                    st.markdown(f"**📈 Participación #{i+1}**")
                                    for key, value in part.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                                    st.markdown("")
                        else:
                            st.info("Sin participaciones superiores al 5%")
                
                with tabs[3]:
                    st.markdown('<div class="section-title">💰 Activos Financieros</div>', unsafe_allow_html=True)
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.markdown("##### Cuentas y Depósitos")
                        accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                        if accounts:
                            total_accounts = sum(extract_debt_account_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                            if total_accounts > 0:
                                st.success(f"**Total en cuentas: {format_currency_full(total_accounts)}**")
                            for account in accounts:
                                if isinstance(account, dict):
                                    desc = account.get('descripcion', 'Cuenta')
                                    if str(desc).lower() == 'nan': desc = 'Cuenta'
                                    saldo = extract_debt_account_value(account.get('saldo'))
                                    if saldo > 0:
                                        st.markdown(f"**🏦 {desc}**")
                                        st.markdown(f"Saldo: **{format_currency_full(saldo)}**")
                        else:
                            st.info("Sin cuentas declaradas")
                        
                        st.markdown("##### Acciones y Participaciones")
                        acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                        if acciones:
                            for i, accion in enumerate(acciones):
                                if isinstance(accion, dict):
                                    st.markdown(f"**📊 Acción #{i+1}**")
                                    for key, value in accion.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else:
                            st.info("Sin acciones declaradas")
                    
                    with tcol2:
                        st.markdown("##### Deuda Pública y Valores")
                        deuda_publica = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
                        if deuda_publica:
                            for i, item in enumerate(deuda_publica):
                                if isinstance(item, dict):
                                    st.markdown(f"**💼 Valor #{i+1}**")
                                    for key, value in item.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else:
                            st.info("Sin deuda pública o valores")
                
                with tabs[4]:
                    st.markdown('<div class="section-title">🚗 Vehículos</div>', unsafe_allow_html=True)
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        st.info(f"**Total vehículos: {len(vehicles)}**")
                        cols = st.columns(2)
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                with cols[i % 2]:
                                    desc = vehicle.get('descripcion', f'Vehículo #{i+1}')
                                    if str(desc).lower() == 'nan': desc = f'Vehículo #{i+1}'
                                    st.markdown(f"**🚗 {desc}**")
                                    fecha = vehicle.get('fecha_adquisicion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"Adquirido: {fecha}")
                                    st.markdown("")
                    else:
                        st.info("Sin vehículos declarados")
                
                with tabs[5]:
                    st.markdown('<div class="section-title">💸 Deudas y Obligaciones</div>', unsafe_allow_html=True)
                    total_debt = sum(extract_debt_account_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
                    if debts:
                        st.error(f"**Total Pendiente: {format_currency_full(total_debt)}**")
                        for i, debt in enumerate(debts):
                            if isinstance(debt, dict):
                                desc = debt.get('descripcion', f'Deuda #{i+1}')
                                if str(desc).lower() == 'nan': desc = f'Deuda #{i+1}'
                                st.markdown(f"**📄 {desc}**")
                                original = extract_debt_account_value(debt.get('importe_concedido'))
                                pending = extract_debt_account_value(debt.get('saldo_pendiente'))
                                tcol1, tcol2 = st.columns(2)
                                with tcol1:
                                    if original > 0:
                                        st.markdown(f"Original: **{format_currency_full(original)}**")
                                    fecha = debt.get('fecha_concesion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"Fecha: {fecha}")
                                with tcol2:
                                    if pending > 0:
                                        st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                                    if original > 0 and pending > 0:
                                        paid_pct = ((original - pending) / original) * 100
                                        st.progress(int(paid_pct), text=f"Pagado: {paid_pct:.1f}%")
                                st.markdown("---")
                    else:
                        st.success("✅ No se han declarado deudas")
                
                with tabs[6]:
                    st.markdown('<div class="section-title">📋 Actividades e Intereses</div>', unsafe_allow_html=True)
                    deputy_id = deputy_data.get('deputy_id')
                    deputy_interests = match_deputy_interests(deputy_id, interests_df)
                    display_interests_section(deputy_interests)
                
                with tabs[7]:
                    st.markdown('<div class="section-title">📄 Otros Bienes y Derechos</div>', unsafe_allow_html=True)
                    otros_bienes = deputy_data.get('otros_bienes_no_declarados_anteriormente', '')
                    if otros_bienes and str(otros_bienes).lower() != 'nan':
                        st.markdown("##### Otros Bienes No Declarados Anteriormente")
                        otros_parsed = parse_json_field(otros_bienes)
                        if otros_parsed:
                            for i, item in enumerate(otros_parsed):
                                if isinstance(item, dict):
                                    st.markdown(f"**Item #{i+1}**")
                                    for key, value in item.items():
                                        if value and str(value).lower() != 'nan':
                                            st.markdown(f"• {key.replace('_', ' ').title()}: {value}")
                        else:
                            st.write(otros_bienes)
                    else:
                        st.info("No hay otros bienes declarados")
    
    st.markdown("---")
    render_footer()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if not st.session_state.disclaimer_accepted:
    show_disclaimer()
else:
    main_app()
