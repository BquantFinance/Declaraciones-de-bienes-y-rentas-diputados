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

# Page configuration — set primaryColor to gold to kill the green
st.set_page_config(
    page_title="Declaracion de Bienes - Congreso de Espana",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# ═══════════════════════════════════════════════════
# DESIGN SYSTEM v3 — "El Hemiciclo"
# Fixes: radio buttons, alert colors, global consistency
# ═══════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── OVERRIDE STREAMLIT THEME COLORS ── */
:root {
    --primary-color: #b8860b !important;
}

/* Force Streamlit's internal primary color variable */
.stApp {
    --primary-color: #b8860b;
}

/* ── CSS VARIABLES ── */
:root {
    --bg: #f7f5f0;
    --bg-warm: #f0ece3;
    --bg-card: #ffffff;
    --ink: #1a1a2e;
    --ink-soft: #2d2d44;
    --ink-muted: #555570;
    --ink-faint: #8888a0;
    --gold: #b8860b;
    --gold-light: #d4a843;
    --gold-pale: rgba(184,134,11,0.08);
    --gold-hover: #9a7209;
    --teal: #1a7a6d;
    --teal-bg: rgba(26,122,109,0.06);
    --red: #b83232;
    --red-bg: rgba(184,50,50,0.06);
    --blue: #2d5fa0;
    --blue-bg: rgba(45,95,160,0.06);
    --border: rgba(26,26,46,0.10);
    --border-strong: rgba(26,26,46,0.18);
    --sh-xs: 0 1px 2px rgba(26,26,46,0.05);
    --sh-sm: 0 2px 6px rgba(26,26,46,0.07);
    --sh-md: 0 6px 20px rgba(26,26,46,0.09);
    --sh-lg: 0 14px 44px rgba(26,26,46,0.12);
    --r-sm: 6px;
    --r-md: 10px;
    --r-lg: 14px;
    --r-xl: 20px;
}

/* ── BASE ── */
.stApp {
    background: var(--bg) !important;
    font-family: 'Source Sans 3', -apple-system, sans-serif !important;
    color: var(--ink) !important;
}
.main .block-container { padding-top: 0; max-width: 1440px; }

/* ── TYPOGRAPHY ── */
h1, h2, h3, h4, h5 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    background: none !important;
    -webkit-background-clip: unset !important;
}
h1 { font-size: 2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
h3 { font-size: 1.15rem !important; font-weight: 600 !important; }
h4, h5 { font-size: 0.95rem !important; font-weight: 600 !important; }
p, li { color: var(--ink-soft); font-family: 'Source Sans 3', sans-serif; }
strong { color: var(--ink) !important; font-weight: 600 !important; }
a { color: var(--gold) !important; text-decoration: none; }
a:hover { color: var(--gold-hover) !important; }
hr { border: none !important; height: 1px !important; background: var(--border) !important; margin: 1rem 0 !important; }

/* ── RADIO BUTTONS ── */
/* Override Streamlit green → use gold/ink */
.stRadio > div[role="radiogroup"],
.stRadio > div {
    gap: 0 !important;
    background: var(--bg-card) !important;
    border-radius: var(--r-lg) !important;
    padding: 4px !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: var(--sh-sm) !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    flex-direction: row !important;
}

.stRadio > div > label {
    background: transparent !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    color: var(--ink-muted) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.3rem !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    margin: 0 !important;
    transition: all 0.2s ease !important;
}
.stRadio > div > label:hover {
    color: var(--ink) !important;
    background: var(--bg-warm) !important;
}

/* Hide radio circle/dot entirely */
.stRadio [data-baseweb="radio"] > div:first-child,
.stRadio svg,
.stRadio > div > label > div:first-child > div {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* Selected radio — kill the green, use dark ink */
.stRadio > div > label[data-checked="true"],
.stRadio > div > label[data-selected="true"],
.stRadio [data-baseweb="radio"][aria-checked="true"] {
    background: var(--ink) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: var(--sh-xs) !important;
    border-radius: var(--r-md) !important;
}
.stRadio > div > label[data-checked="true"] *,
.stRadio > div > label[data-selected="true"] *,
.stRadio > div > label[data-checked="true"] p,
.stRadio > div > label[data-selected="true"] p {
    color: white !important;
}

/* Nuclear option: override ALL Streamlit green/primary colored elements */
.stRadio [aria-checked="true"] + div,
.stRadio label[data-checked="true"],
.stRadio div[data-checked="true"] {
    background: var(--ink) !important;
    color: white !important;
}

/* Hide the top label "Navegacion:" etc */
.stRadio > label[data-testid="stWidgetLabel"] {
    display: none !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px !important;
    background: var(--bg-warm) !important;
    border-radius: var(--r-lg) !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    height: 36px !important;
    padding: 0 14px !important;
    background: transparent !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink-faint) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--ink) !important;
    background: rgba(255,255,255,0.6) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--ink) !important;
    font-weight: 700 !important;
    box-shadow: var(--sh-sm) !important;
}
/* Kill default underline */
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 0.5rem !important; }

/* ── METRICS ── */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    padding: 0.9rem 1rem !important;
    border-radius: var(--r-md) !important;
    box-shadow: var(--sh-xs) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: var(--sh-md) !important;
    border-color: var(--gold) !important;
}
div[data-testid="metric-container"] label {
    color: var(--ink-faint) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-weight: 700 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"],
div[data-testid="metric-container"] div[data-testid="stMetricValue"] > div {
    color: var(--ink) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--r-md) !important;
    color: var(--ink) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.9rem !important;
    box-shadow: var(--sh-xs) !important;
}
.stSelectbox > div > div:hover,
.stTextInput > div > div > input:hover {
    border-color: var(--gold) !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-pale) !important;
}
.stSelectbox label, .stTextInput label {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--ink-faint) !important;
    font-weight: 700 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--r-md) !important;
    color: var(--ink) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    box-shadow: var(--sh-xs) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--sh-md) !important;
    border-color: var(--gold) !important;
}
.stButton > button:active,
.stButton > button:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(184,134,11,0.12) !important;
    background: var(--bg-card) !important;
    color: var(--ink) !important;
    transform: none !important;
}
/* Primary variant */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--gold) !important;
    color: #fff !important;
    border-color: var(--gold) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--gold-hover) !important;
    border-color: var(--gold-hover) !important;
}
.stButton > button[kind="primary"]:active,
.stButton > button[kind="primary"]:focus,
.stButton > button[data-testid="baseButton-primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:focus {
    background: var(--gold) !important;
    border-color: var(--gold) !important;
    color: #fff !important;
    box-shadow: 0 0 0 3px rgba(184,134,11,0.2) !important;
}

/* Random dice */
.random-button-container { margin-top: 27px; }
.random-button-container > div > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--gold) !important;
    color: var(--gold) !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
    border-radius: var(--r-md) !important;
    box-shadow: var(--sh-xs) !important;
    padding: 0.4rem 0.8rem !important;
}
.random-button-container > div > button:hover {
    background: var(--gold-pale) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--sh-sm) !important;
    color: var(--gold-hover) !important;
    border-color: var(--gold-hover) !important;
}
.random-button-container > div > button:active,
.random-button-container > div > button:focus {
    background: var(--gold-pale) !important;
    color: var(--gold) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(184,134,11,0.12) !important;
}

/* ── ALERT BOXES ── */
/* Blanket override for ALL Streamlit notification/alert variants */
[data-baseweb="notification"] {
    border-radius: var(--r-md) !important;
    border: none !important;
    border-left: 4px solid var(--blue) !important;
    background-color: var(--blue-bg) !important;
}
[data-baseweb="notification"] div,
[data-baseweb="notification"] p,
[data-baseweb="notification"] span {
    color: var(--ink-soft) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}
/* Override icon colors — kill the default blue/green/red svgs */
[data-baseweb="notification"] svg {
    display: none !important;
}

/* Success = teal */
[data-baseweb="notification"][kind="positive"] {
    background-color: var(--teal-bg) !important;
    border-left-color: var(--teal) !important;
}
/* Warning = gold */
[data-baseweb="notification"][kind="warning"] {
    background-color: var(--gold-pale) !important;
    border-left-color: var(--gold) !important;
}
/* Error = red */
[data-baseweb="notification"][kind="negative"] {
    background-color: var(--red-bg) !important;
    border-left-color: var(--red) !important;
}
/* Info = blue (default above) */
[data-baseweb="notification"][kind="info"] {
    background-color: var(--blue-bg) !important;
    border-left-color: var(--blue) !important;
}

/* Also target Streamlit's newer alert components */
.stAlert > div, div[data-testid="stNotification"] > div {
    border-radius: var(--r-md) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    background: var(--bg-card) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    background: var(--bg-card) !important;
}
[data-testid="stExpander"] summary:hover {
    background: var(--bg-warm) !important;
}
/* Kill any dark backgrounds on expander elements */
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"],
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary div {
    color: var(--ink) !important;
    background: transparent !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div { background-color: var(--bg-warm) !important; border-radius: 6px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--teal), #2aaa95) !important; border-radius: 6px !important; }

/* ═════════════════════════════════ */
/* CUSTOM COMPONENTS                 */
/* ═════════════════════════════════ */

/* Masthead */
.masthead {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    margin: -1rem -4rem 0 -4rem;
    padding: 2.2rem 2rem 1.8rem;
    text-align: center;
    position: relative; overflow: hidden;
}
.masthead::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(184,134,11,0.07), transparent 60%),
                radial-gradient(ellipse at 70% 50%, rgba(184,134,11,0.04), transparent 60%);
    pointer-events: none;
}
.masthead::after {
    content: '';
    position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 100px; height: 3px; background: var(--gold);
}
.masthead-overline {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.6rem;
    letter-spacing: 5px; text-transform: uppercase;
    color: rgba(255,255,255,0.35); margin-bottom: 0.4rem; position: relative;
}
.masthead-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2rem, 4vw, 3rem); font-weight: 700;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    line-height: 1.1; margin: 0; position: relative;
}
.masthead-title .accent-dot { color: var(--gold) !important; -webkit-text-fill-color: var(--gold) !important; }
.masthead-subtitle {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.82rem;
    color: rgba(255,255,255,0.45); margin-top: 0.5rem;
    font-weight: 300; letter-spacing: 0.8px; position: relative;
}
.masthead-edition {
    display: inline-block; margin-top: 0.7rem; padding: 0.2rem 0.9rem;
    background: rgba(184,134,11,0.12); border: 1px solid rgba(184,134,11,0.25);
    border-radius: 20px; font-family: 'Source Sans 3', sans-serif;
    font-size: 0.65rem; color: var(--gold-light);
    letter-spacing: 1.5px; text-transform: uppercase; position: relative;
}

/* Section headings */
.section-heading {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.1rem; font-weight: 600; color: var(--ink);
    display: flex; align-items: center; gap: 0.5rem;
    margin: 1.2rem 0 0.8rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--ink); position: relative;
}
.section-heading::after {
    content: '';
    position: absolute; bottom: -2px; left: 0;
    width: 40px; height: 2px; background: var(--gold);
}
.section-heading-light {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1rem; font-weight: 600; color: var(--ink);
    margin: 0.8rem 0 0.6rem; padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* Deputy name */
.deputy-name-header {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.8rem; font-weight: 700; color: var(--ink);
    line-height: 1.15; margin-bottom: 0.75rem;
    position: relative; padding-bottom: 0.6rem;
}
.deputy-name-header::after {
    content: '';
    position: absolute; bottom: 0; left: 0;
    width: 50px; height: 3px; background: var(--gold); border-radius: 2px;
}

/* Salary card */
.salary-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: var(--r-lg); padding: 1rem 1.4rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.2rem; box-shadow: var(--sh-md);
    position: relative; overflow: hidden;
}
.salary-card::before {
    content: '';
    position: absolute; top: 0; right: 0; width: 200px; height: 100%;
    background: radial-gradient(ellipse at right, rgba(184,134,11,0.12), transparent 70%);
    pointer-events: none;
}
.salary-label {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.65rem;
    text-transform: uppercase; letter-spacing: 2px;
    color: rgba(255,255,255,0.5); font-weight: 600; position: relative;
}
.salary-amount {
    font-family: 'JetBrains Mono', monospace; font-size: 1.7rem; font-weight: 700;
    color: var(--gold-light); position: relative; letter-spacing: -0.5px;
}
.salary-na { color: rgba(255,255,255,0.3); font-size: 1.2rem; }

/* Photo gallery */
.image-gallery {
    display: flex; gap: 1.5rem; align-items: center;
    justify-content: center; margin-bottom: 1.5rem; flex-wrap: wrap;
}
.photo-frame {
    position: relative; border-radius: var(--r-lg); overflow: hidden;
    box-shadow: var(--sh-lg); transition: all 0.4s ease;
    border: 3px solid var(--bg-card);
}
.photo-frame:hover { transform: translateY(-6px) scale(1.02); }
.photo-frame img { width: 200px; height: 250px; object-fit: cover; display: block; }
.photo-frame::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 50%;
    background: linear-gradient(transparent, rgba(26,26,46,0.1));
    pointer-events: none;
}
.no-photo {
    width: 200px; height: 250px;
    background: linear-gradient(135deg, var(--bg-warm), var(--bg));
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: var(--ink-faint); border-radius: var(--r-lg);
    border: 2px dashed var(--border-strong); font-size: 3rem;
}
.no-photo span {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.7rem;
    margin-top: 8px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600;
}
.badges-container { display: flex; flex-direction: column; gap: 0.6rem; align-items: center; }
.badge-frame {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-md); padding: 10px; box-shadow: var(--sh-sm);
    transition: all 0.3s ease;
}
.badge-frame:hover { transform: translateY(-4px) rotate(-3deg); box-shadow: var(--sh-md); border-color: var(--gold); }
.badge-frame img { width: 85px; height: 85px; object-fit: contain; display: block; }

/* Info grid */
.info-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.5rem; margin: 0.6rem 0;
}
.info-chip {
    background: var(--bg-card); padding: 0.65rem 0.85rem;
    border-radius: var(--r-md); border: 1px solid var(--border);
    box-shadow: var(--sh-xs); transition: all 0.25s ease;
}
.info-chip:hover { transform: translateY(-2px); box-shadow: var(--sh-sm); border-color: var(--gold); }
.info-chip-label {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.58rem;
    color: var(--ink-faint); text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 700; margin-bottom: 0.2rem;
}
.info-chip-value {
    font-family: 'Source Sans 3', sans-serif; font-size: 0.88rem;
    color: var(--ink); font-weight: 600;
}

/* Social links */
.social-row { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.social-btn {
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--bg-card); border: 1px solid var(--border);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 1.1rem; text-decoration: none !important;
    transition: all 0.3s ease; box-shadow: var(--sh-xs);
}
.social-btn:hover {
    transform: translateY(-3px) scale(1.1); box-shadow: var(--sh-md);
    border-color: var(--gold); background: var(--gold-pale);
}

/* Screener cards */
.screener-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-lg); padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem; transition: all 0.3s ease;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: var(--sh-xs); position: relative; overflow: hidden;
}
.screener-card::before {
    content: ''; position: absolute; left: 0; top: 0;
    width: 3px; height: 100%; background: var(--gold);
    opacity: 0; transition: opacity 0.25s ease;
}
.screener-card:hover { transform: translateX(6px); border-color: var(--gold); box-shadow: var(--sh-md); }
.screener-card:hover::before { opacity: 1; }
.screener-rank {
    font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700;
    color: var(--ink-faint); min-width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    border-radius: var(--r-sm); background: var(--bg-warm);
    border: 1px solid var(--border); flex-shrink: 0;
}
.screener-rank.gold { background: linear-gradient(135deg, #b8860b, #d4a843); color: white; border: none; box-shadow: 0 2px 8px rgba(184,134,11,0.3); }
.screener-rank.silver { background: linear-gradient(135deg, #7a8599, #a0aabb); color: white; border: none; }
.screener-rank.bronze { background: linear-gradient(135deg, #8b6035, #b08050); color: white; border: none; }
.screener-photo { width: 50px; height: 62px; object-fit: cover; border-radius: var(--r-sm); box-shadow: var(--sh-sm); flex-shrink: 0; }
.screener-photo-placeholder {
    width: 50px; height: 62px; background: var(--bg-warm);
    display: flex; align-items: center; justify-content: center;
    color: var(--ink-faint); border-radius: var(--r-sm);
    border: 1px dashed var(--border-strong); font-size: 1.2rem; flex-shrink: 0;
}
.screener-info { flex: 1; min-width: 0; }
.screener-name { font-family: 'Source Sans 3', sans-serif; font-size: 0.92rem; font-weight: 600; color: var(--ink); }
.screener-party { font-family: 'Source Sans 3', sans-serif; font-size: 0.72rem; color: var(--ink-faint); }
.screener-value { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; color: var(--ink); text-align: right; min-width: 120px; flex-shrink: 0; }
.screener-value.positive { color: var(--teal); }
.screener-value.negative { color: var(--red); }

/* Activity cards */
.activity-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 0 var(--r-md) var(--r-md) 0;
    padding: 0.85rem 1rem; margin-bottom: 0.5rem;
    transition: all 0.25s ease;
}
.activity-card:hover { transform: translateX(4px); box-shadow: var(--sh-sm); border-left-color: var(--ink); }
.activity-badge {
    display: inline-block; padding: 0.12rem 0.55rem; border-radius: 3px;
    font-family: 'Source Sans 3', sans-serif; font-size: 0.58rem; font-weight: 700;
    margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 1px;
}
.badge-cargo { background: var(--ink); color: white; }
.badge-actividad { background: var(--teal); color: white; }
.badge-partido { background: var(--gold); color: white; }
.badge-otros { background: var(--ink-faint); color: white; }

/* Disclaimer */
.disclaimer-box {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--r-xl); padding: 2.5rem 3rem;
    margin: 1.5rem auto; max-width: 850px; box-shadow: var(--sh-lg);
}
h1.disclaimer-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 1.8rem !important; font-weight: 700 !important;
    color: var(--red) !important; -webkit-text-fill-color: var(--red) !important;
    text-align: center; margin-bottom: 1.5rem !important;
    padding-bottom: 1rem; border-bottom: 2px solid var(--red);
}
h3.disclaimer-section-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
    margin-top: 1.8rem !important; margin-bottom: 0.6rem !important;
    font-size: 1.05rem !important; font-weight: 600 !important;
    padding-bottom: 0.3rem; border-bottom: 1px solid var(--border);
}

/* Footer */
.app-footer {
    text-align: center; padding: 1.5rem 0 1rem; margin-top: 1.5rem;
    border-top: 2px solid var(--ink); position: relative;
}
.app-footer::before {
    content: ''; position: absolute; top: -2px; left: 0;
    width: 40px; height: 2px; background: var(--gold);
}
.app-footer-text { font-family: 'Source Sans 3', sans-serif; font-size: 0.75rem; color: var(--ink-faint); }
.app-footer-text a { color: var(--gold) !important; font-weight: 600; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--ink-faint); border-radius: 10px; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
    .masthead { margin: -1rem -1rem 0 -1rem; padding: 2rem 1rem 1.5rem; }
    .info-grid { grid-template-columns: 1fr 1fr; }
    .image-gallery { flex-direction: column; }
    .disclaimer-box { padding: 1.5rem; margin: 1rem; }
    .deputy-name-header { font-size: 1.4rem; }
    .salary-amount { font-size: 1.3rem; }
    .photo-frame img, .no-photo { width: 160px; height: 200px; }
}
</style>
"""

def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
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
        st.error("No se encontro el archivo 'deputies_with_salaries.csv'.")
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
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────
def normalize_name(name):
    if pd.isna(name): return ""
    name = str(name)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return ' '.join(name.lower().split())

def normalize_deputy_id(deputy_id):
    if pd.isna(deputy_id): return None
    try: return int(deputy_id)
    except (ValueError, TypeError): return None

def match_deputy_interests(deputy_id, interests_df):
    if interests_df.empty: return pd.DataFrame()
    if pd.isna(deputy_id): return pd.DataFrame()
    return interests_df[interests_df['metadata_deputy_id'] == deputy_id]

def parse_json_field(field_value):
    if pd.isna(field_value) or field_value in ('[]', ''): return []
    try:
        cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value))
        return json.loads(cleaned_value)
    except: return []

def format_currency(value):
    if not isinstance(value, (int, float)): return "0E"
    if value == int(value):
        return f"{int(value):,}E".replace(",", ".").replace("E", "€")
    else:
        return f"{value:,.2f}E".replace(",", "X").replace(".", ",").replace("X", ".").replace("E", "€")

def format_currency_full(value):
    if not isinstance(value, (int, float)): return "0,00 €"
    if value == int(value):
        return f"{int(value):,} €".replace(",", ".")
    else:
        return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def extract_irpf_value(value):
    if pd.isna(value) or value == '': return 0
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
                integer_part, decimal_part = parts
                if len(decimal_part) == 3: return float(integer_part + decimal_part)
                elif len(decimal_part) >= 4:
                    combined = integer_part + decimal_part
                    return float(combined[:-2] + '.' + combined[-2:])
                elif len(decimal_part) == 2 and value < 1000: return float(integer_part + decimal_part)
        if 20 < value < 100 and '.' in value_str: return float(value_str.replace('.', ''))
        return value
    value_str = str(value).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    numeric_part = re.search(r'[\d.,]+', value_str)
    if numeric_part:
        num_str = numeric_part.group(0)
        if ',' in num_str: return float(num_str.replace('.', '').replace(',', '.'))
        else: return float(num_str.replace(',', ''))
    return 0

def extract_debt_account_value(value_str):
    if pd.isna(value_str) or value_str == '': return 0
    if isinstance(value_str, (int, float)):
        value = float(value_str)
        if value > 1000 and value == int(value):
            value_str_int = str(int(value))
            if len(value_str_int) >= 6:
                corrected = value_str_int[:-3] + '.' + value_str_int[-3:]
                corrected_value = float(corrected)
                if corrected_value < 500000 and value > 500000: return corrected_value
        return value
    value_str = str(value_str).strip()
    value_str = re.sub(r'[€$£\s]', '', value_str)
    numeric_part = re.search(r'[\d.,]+', value_str)
    if not numeric_part: return 0
    try:
        num_str = numeric_part.group(0)
        dot_count = num_str.count('.')
        comma_count = num_str.count(',')
        if comma_count > 0: return float(num_str.replace('.', '').replace(',', '.'))
        if dot_count > 0 and comma_count == 0:
            if dot_count > 1:
                parts = num_str.split('.')
                if len(parts[-1]) <= 2: return float(''.join(parts[:-1]) + '.' + parts[-1])
                else: return float(num_str.replace('.', ''))
            parts = num_str.split('.')
            integer_part, decimal_part = parts
            if len(decimal_part) == 3: return float(num_str.replace('.', ''))
            elif 4 <= len(decimal_part) <= 5:
                combined = integer_part + decimal_part
                return float(combined[:-2] + '.' + combined[-2:])
            elif len(decimal_part) <= 2: return float(num_str)
            else: return float(num_str.replace('.', ''))
        return float(num_str)
    except (ValueError, TypeError): return 0


# ─────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────
def render_masthead():
    st.markdown("""
    <div class="masthead">
        <div class="masthead-overline">Congreso de los Diputados · XV Legislatura</div>
        <h1 class="masthead-title">Declaración de Bienes<span class="accent-dot">.</span></h1>
        <div class="masthead-subtitle">Análisis Interactivo de Transparencia Financiera Parlamentaria</div>
        <div class="masthead-edition">Datos Públicos · Información Oficial</div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="app-footer">
        <div class="app-footer-text">
            Desarrollado por <a href="https://x.com/Gsnchez" target="_blank">@Gsnchez</a> · 
            Fuente: <a href="https://www.congreso.es" target="_blank">Congreso de los Diputados</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_image_gallery(deputy_data):
    gallery_html = '<div class="image-gallery">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<div class="photo-frame"><img src="data:image/jpeg;base64,{img_data}" alt="Foto del diputado"></div>'
    else:
        gallery_html += '<div class="no-photo">👤<span>Sin Foto</span></div>'
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

def get_deputy_photo_html(photo_path):
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        try:
            with open(photo_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
                return f'<img src="data:image/jpeg;base64,{img_data}" class="screener-photo" alt="Foto">'
        except: pass
    return '<div class="screener-photo-placeholder">👤</div>'

def display_interests_section(deputy_interests):
    if deputy_interests.empty:
        st.info("No hay información de registro de intereses disponible para este diputado.")
        return
    st.markdown(f'<div class="section-heading">📋 Registro de Intereses — {len(deputy_interests)} Registros</div>', unsafe_allow_html=True)
    for section_name, section_data in deputy_interests.groupby('seccion'):
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
                    sector = row.get('actividad_sector', 'Sin especificar')
                    empleador = row.get('actividad_empleador', '')
                    periodo = row.get('actividad_periodo', '')
                    desc = row.get('actividad_descripcion', '')
                    badge_class = 'badge-otros'
                    if pd.notna(sector):
                        s = str(sector).lower()
                        if 'cargo' in s and 'público' in s: badge_class = 'badge-cargo'
                        elif 'partido' in s or 'grupo parlamentario' in s: badge_class = 'badge-partido'
                        elif 'privada' in s or 'docente' in s: badge_class = 'badge-actividad'
                    c = f'<div class="activity-card">'
                    c += f'<div class="activity-badge {badge_class}">{html.escape(str(sector)) if pd.notna(sector) else "Sin especificar"}</div>'
                    if pd.notna(empleador) and str(empleador).strip():
                        c += f'<p style="color:var(--ink);font-weight:600;margin:0.35rem 0;font-size:0.9rem;">🏢 {html.escape(str(empleador))}</p>'
                    if pd.notna(desc) and str(desc).strip():
                        c += f'<p style="color:var(--ink-soft);margin:0.25rem 0;font-size:0.85rem;">{html.escape(str(desc))}</p>'
                    if pd.notna(periodo) and str(periodo).strip():
                        c += f'<p style="color:var(--ink-faint);font-size:0.78rem;margin-top:0.25rem;font-family:JetBrains Mono,monospace;">📅 {html.escape(str(periodo))}</p>'
                    c += '</div>'
                    st.markdown(c, unsafe_allow_html=True)
            elif section_name == 'otros_intereses':
                for idx, row in section_data.iterrows():
                    texto = row.get('otros_texto', '')
                    if pd.notna(texto) and str(texto).strip():
                        st.markdown(f'<div class="activity-card"><p style="color:var(--ink-soft);white-space:pre-wrap;font-size:0.85rem;">{html.escape(str(texto))}</p></div>', unsafe_allow_html=True)
            elif section_name == 'donaciones':
                for idx, row in section_data.iterrows():
                    benefactor = row.get('donacion_benefactor', '')
                    descripcion = row.get('donacion_descripcion', '')
                    if pd.notna(benefactor) or pd.notna(descripcion):
                        c = '<div class="activity-card"><div class="activity-badge badge-otros">Donación</div>'
                        if pd.notna(benefactor) and str(benefactor).strip():
                            c += f'<p style="color:var(--ink);font-weight:600;margin:0.35rem 0;">🎁 De: {html.escape(str(benefactor))}</p>'
                        if pd.notna(descripcion) and str(descripcion).strip():
                            c += f'<p style="color:var(--ink-soft);margin:0.25rem 0;font-size:0.85rem;">{html.escape(str(descripcion))}</p>'
                        c += '</div>'
                        st.markdown(c, unsafe_allow_html=True)
            elif section_name == 'fundaciones':
                for idx, row in section_data.iterrows():
                    destinatario = row.get('fundacion_destinatario', '')
                    descripcion = row.get('fundacion_descripcion', '')
                    if pd.notna(destinatario) or pd.notna(descripcion):
                        c = '<div class="activity-card"><div class="activity-badge badge-actividad">Fundación</div>'
                        if pd.notna(destinatario) and str(destinatario).strip():
                            c += f'<p style="color:var(--ink);font-weight:600;margin:0.35rem 0;">🏢 {html.escape(str(destinatario))}</p>'
                        if pd.notna(descripcion) and str(descripcion).strip():
                            c += f'<p style="color:var(--ink-soft);margin:0.25rem 0;font-size:0.85rem;">{html.escape(str(descripcion))}</p>'
                        c += '</div>'
                        st.markdown(c, unsafe_allow_html=True)
            else:
                for idx, row in section_data.iterrows():
                    st.markdown(f'<div class="activity-card"><p style="color:var(--ink-soft);">Registro de {section_name.replace("_", " ")}</p></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SCREENER
# ─────────────────────────────────────────────
def prepare_screener_data(df):
    df_copy = df.copy()
    df_copy['normalized_name'] = df_copy['informacion_personal_nombre_y_apellidos'].apply(normalize_name)
    df_sorted = df_copy.sort_values('source_file', ascending=True)
    unique_deputies = df_sorted.groupby('normalized_name').last().reset_index()
    screener_data = []
    for idx, row in unique_deputies.iterrows():
        d = {
            'name': row['informacion_personal_nombre_y_apellidos'],
            'photo_path': row.get('photo_path', ''),
            'party': row.get('informacion_personal_cargo', 'Diputado'),
            'salary': 0, 'irpf': 0, 'properties_count': 0, 'vehicles_count': 0,
            'debt_total': 0, 'accounts_balance': 0, 'max_account': 0,
            'max_debt': 0, 'max_debt_original': 0, 'total_assets': 0,
        }
        salary = row.get('scraped_salary', None)
        if pd.notna(salary) and salary:
            try: d['salary'] = float(salary)
            except: pass
        d['irpf'] = extract_irpf_value(row.get('irpf_cantidad_pagada', 0))
        d['properties_count'] = len(parse_json_field(row['bienes_patrimoniales_inmuebles_urbanos'])) + len(parse_json_field(row.get('bienes_patrimoniales_inmuebles_rusticos', '[]')))
        d['vehicles_count'] = len(parse_json_field(row['vehiculos']))
        debts = parse_json_field(row['deudas_y_obligaciones'])
        dp, do_list = [], []
        for debt in debts:
            if isinstance(debt, dict):
                p = extract_debt_account_value(debt.get('saldo_pendiente', 0))
                o = extract_debt_account_value(debt.get('importe_concedido', 0))
                if p > 0: dp.append(p)
                if o > 0: do_list.append(o)
        d['debt_total'] = sum(dp)
        d['max_debt'] = max(dp) if dp else 0
        d['max_debt_original'] = max(do_list) if do_list else 0
        accounts = parse_json_field(row['depositos_y_cuentas_cuentas'])
        ab = [extract_debt_account_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict) and extract_debt_account_value(a.get('saldo', 0)) > 0]
        d['accounts_balance'] = sum(ab)
        d['max_account'] = max(ab) if ab else 0
        ta = d['accounts_balance']
        for accion in parse_json_field(row.get('otros_bienes_y_derechos_acciones_y_participaciones', '')):
            if isinstance(accion, dict): ta += extract_debt_account_value(accion.get('valor', 0))
        for valor in parse_json_field(row.get('otros_bienes_y_derechos_deuda_publica_y_valores', '')):
            if isinstance(valor, dict): ta += extract_debt_account_value(valor.get('valor', 0))
        d['total_assets'] = ta
        screener_data.append(d)
    return pd.DataFrame(screener_data)

def display_screener_card(rank, deputy_info, metric_name, metric_value, value_class=""):
    rank_class = ""
    medal = ""
    if rank == 1: rank_class = "gold"; medal = "🥇"
    elif rank == 2: rank_class = "silver"; medal = "🥈"
    elif rank == 3: rank_class = "bronze"; medal = "🥉"
    rank_display = medal if medal else f"#{rank}"
    photo_html = get_deputy_photo_html(deputy_info['photo_path'])
    st.markdown(f'''
    <div class="screener-card">
        <div class="screener-rank {rank_class}">{rank_display}</div>
        {photo_html}
        <div class="screener-info">
            <div class="screener-name">{deputy_info['name']}</div>
            <div class="screener-party">{deputy_info['party']}</div>
        </div>
        <div class="screener-value {value_class}">{metric_value}</div>
    </div>
    ''', unsafe_allow_html=True)

def show_screener(df):
    st.markdown('<div class="section-heading" style="font-size:1.3rem;justify-content:center;">🔍 Screening de Diputados</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:var(--ink-faint);font-size:0.85rem;margin-bottom:1rem;">Explora y compara las métricas financieras de los diputados</p>', unsafe_allow_html=True)
    screener_df = prepare_screener_data(df)
    col1, col2 = st.columns([2, 1])
    with col1:
        metric_options = {
            '💰 Salario Anual': ('salary', 'positive', 'currency'),
            '💵 IRPF Pagado': ('irpf', 'positive', 'currency'),
            '🏠 Número de Inmuebles': ('properties_count', 'positive', 'number'),
            '🚗 Número de Vehículos': ('vehicles_count', 'positive', 'number'),
            '💳 Deuda Total Pendiente': ('debt_total', 'negative', 'currency'),
            '⚠ Préstamo Más Alto (Pendiente)': ('max_debt', 'negative', 'currency'),
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
    c1, c2 = st.columns(2)
    with c1:
        avg = screener_df[metric_column].mean()
        st.metric("Promedio", format_currency(avg) if format_type == 'currency' else f"{avg:.1f}")
    with c2:
        mx = screener_df[metric_column].max()
        st.metric("Máximo", format_currency(mx) if format_type == 'currency' else f"{int(mx)}")
    st.markdown("---")
    for idx, (_, deputy) in enumerate(top_deputies.iterrows(), 1):
        val = deputy[metric_column]
        fv = format_currency_full(val) if format_type == 'currency' else f"{int(val)}"
        display_screener_card(idx, deputy, selected_metric_name, fv, value_class)
    st.markdown("---")
    st.markdown('<div class="section-heading">📊 Visualización Comparativa</div>', unsafe_allow_html=True)
    fig = go.Figure()
    text_vals = top_deputies[metric_column].apply(lambda x: format_currency(x) if format_type == 'currency' else f"{int(x)}")
    fig.add_trace(go.Bar(
        x=top_deputies['name'], y=top_deputies[metric_column],
        marker=dict(
            color=top_deputies[metric_column],
            colorscale=[[0, '#1a7a6d'], [0.5, '#b8860b'], [1, '#b83232']],
            showscale=True,
            colorbar=dict(tickfont=dict(color='#1a1a2e', family='JetBrains Mono', size=10))
        ),
        text=text_vals, textposition='auto',
        textfont=dict(family='JetBrains Mono', size=10, color='white'),
    ))
    fig.update_layout(
        title=dict(text=selected_metric_name, font=dict(family='Playfair Display', size=16, color='#1a1a2e')),
        template="plotly_white", height=420, showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1a1a2e', family='Source Sans 3'),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9, color='#555570'), gridcolor='rgba(26,26,46,0.04)'),
        yaxis=dict(tickfont=dict(family='JetBrains Mono', size=9, color='#555570'), gridcolor='rgba(26,26,46,0.05)'),
        margin=dict(t=50, b=100, l=60, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# DISCLAIMER
# ─────────────────────────────────────────────
def show_disclaimer():
    apply_css()
    _, col2, _ = st.columns([1, 4, 1])
    with col2:
        st.markdown('<div class="disclaimer-box">', unsafe_allow_html=True)
        st.markdown('<h1 class="disclaimer-title">⚖ Descargo de Responsabilidad Legal</h1>', unsafe_allow_html=True)
        st.write("**IMPORTANTE: LEA ATENTAMENTE ANTES DE USAR ESTA APLICACIÓN**")
        st.write('Esta aplicación web de consulta de información pública ("la Aplicación") recopila, procesa y presenta datos obtenidos de fuentes públicas disponibles en la página web oficial del Congreso de los Diputados de España.')
        st.markdown('<h3 class="disclaimer-section-title">📋 Naturaleza y Origen de la Información</h3>', unsafe_allow_html=True)
        st.write("La información proviene exclusivamente de:")
        st.markdown("- Declaraciones de bienes y rentas del Portal de Transparencia del Congreso\n- Registros públicos de actividades e intereses parlamentarios\n- Documentación oficial de acceso público en www.congreso.es")
        st.markdown('<h3 class="disclaimer-section-title">⚠ Descargo de Responsabilidad</h3>', unsafe_allow_html=True)
        st.write("**La Aplicación no pertenece, no está vinculada, afiliada, patrocinada, avalada ni autorizada por el Congreso de los Diputados**, ni por ninguna institución gubernamental española.")
        st.write("El contenido se ofrece con fines informativos y educativos:")
        st.markdown("- Puede contener **errores, inexactitudes u omisiones**\n- Los datos pueden no reflejar cambios recientes\n- El procesamiento automatizado puede introducir errores involuntarios")
        st.markdown('<h3 class="disclaimer-section-title">📌 Limitación de Responsabilidad</h3>', unsafe_allow_html=True)
        st.markdown("- No se garantiza exactitud, integridad o idoneidad de la información\n- No se asume responsabilidad por decisiones basadas en estos datos\n- Se reserva el derecho de modificar o discontinuar el servicio")
        st.markdown('<h3 class="disclaimer-section-title">✅ Fuente Oficial</h3>', unsafe_allow_html=True)
        st.info("🔗 **Portal de Transparencia:** [www.congreso.es](https://www.congreso.es)")
        st.markdown('<h3 class="disclaimer-section-title">👤 Privacidad</h3>', unsafe_allow_html=True)
        st.write("Solo se muestra información de dominio público publicada oficialmente por el Congreso.")
        st.markdown('<h3 class="disclaimer-section-title">⚖ Aceptación de Términos</h3>', unsafe_allow_html=True)
        st.write('Al aceptar, usted reconoce que:')
        st.markdown("- Ha leído y comprendido este descargo\n- Acepta usar la Aplicación bajo su propio riesgo\n- Se compromete a verificar información crítica en fuentes oficiales")
        st.warning("**El uso de esta aplicación es responsabilidad exclusiva del usuario.**")
        st.markdown('</div>', unsafe_allow_html=True)
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
    if df.empty: st.stop()
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
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
            search_term = st.text_input("Buscar diputado", placeholder="🔍 Buscar diputado por nombre...", key="search", label_visibility="collapsed")
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
            try: selected_index = deputy_names.index(st.session_state.selected_deputy_name)
            except (ValueError, IndexError): selected_index = 0
            def format_deputy_option(name):
                try:
                    row = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'] == name]
                    if not row.empty:
                        s = row['scraped_salary'].iloc[0]
                        if pd.notna(s) and s:
                            return f"{name}  ·  {float(s):,.0f}€".replace(",", ".")
                except: pass
                return name
            selected_deputy_name = st.selectbox("Seleccionar Diputado:", deputy_names, index=selected_index, format_func=format_deputy_option)
            st.session_state.selected_deputy_name = selected_deputy_name
            deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name].sort_values(by='source_file', ascending=True)
            if len(deputy_declarations) > 1:
                st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
                declaration_options = []
                for i, (idx, row) in enumerate(deputy_declarations.iterrows()):
                    label_parts = [f"Declaración {i+1}"]
                    cargo = row.get('informacion_personal_cargo', '')
                    if pd.notna(cargo): label_parts.append(f"({cargo.strip()})")
                    doc_date_str = "Fecha Desconocida"
                    source_file = row.get('source_file', '')
                    date_match = re.search(r'_(\d{8})\.json$', source_file)
                    if date_match:
                        try:
                            doc_date = datetime.strptime(date_match.group(1), '%Y%m%d')
                            months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
                            doc_date_str = f"{doc_date.day} {months[doc_date.month-1]} {doc_date.year}"
                        except ValueError: pass
                    label_parts.append(f"· {doc_date_str}")
                    obs = row.get('observaciones', '')
                    if pd.notna(obs) and any(w in obs.lower() for w in ['modificación', 'remito a', 'actualizar']):
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
            col_left, col_right = st.columns([1.5, 2])
            with col_left:
                st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
                st.markdown('<div class="section-heading">📋 Información Personal</div>', unsafe_allow_html=True)
                info_html = '<div class="info-grid">'
                for label, field, default in [
                    ('Cargo', 'informacion_personal_cargo', 'Diputado'),
                    ('Circunscripción', 'informacion_personal_circunscripcion', None),
                    ('Estado Civil', 'informacion_personal_estado_civil', None),
                    ('Régimen Económico', 'informacion_personal_regimen_economico_matrimonial', None),
                    ('Fecha Elección', 'informacion_personal_fecha_eleccion', None),
                    ('Credencial', 'informacion_personal_fecha_presentacion_credencial', None),
                ]:
                    value = deputy_data.get(field, default)
                    if value and str(value).lower() != 'nan':
                        if not value and default: value = default
                        info_html += f'<div class="info-chip"><div class="info-chip-label">{label}</div><div class="info-chip-value">{value}</div></div>'
                info_html += '</div>'
                st.markdown(info_html, unsafe_allow_html=True)
                social_links = {"𝕏": deputy_data.get('twitter'), "📘": deputy_data.get('facebook'), "📸": deputy_data.get('instagram'), "🌐": deputy_data.get('website')}
                valid_links = {e: u for e, u in social_links.items() if pd.notna(u) and str(u).lower() != 'nan'}
                if valid_links:
                    st.markdown('<div class="section-heading-light">🌐 Redes Sociales</div>', unsafe_allow_html=True)
                    titles = {"𝕏": "X (Twitter)", "📘": "Facebook", "📸": "Instagram", "🌐": "Web"}
                    social_html = '<div class="social-row">'
                    for emoji, url in valid_links.items():
                        social_html += f'<a href="{url}" target="_blank" class="social-btn" title="{titles.get(emoji, "")}">{emoji}</a>'
                    social_html += '</div>'
                    st.markdown(social_html, unsafe_allow_html=True)
                obs = deputy_data.get('observaciones', '')
                if obs and str(obs).lower() != 'nan':
                    st.markdown('<div class="section-heading-light">📝 Observaciones</div>', unsafe_allow_html=True)
                    st.info(obs)
            with col_right:
                name = deputy_data['informacion_personal_nombre_y_apellidos']
                st.markdown(f'<div class="deputy-name-header">{name}</div>', unsafe_allow_html=True)
                salary = deputy_data.get('scraped_salary', None)
                if pd.notna(salary) and salary:
                    fs = f"{float(salary):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    st.markdown(f'''
                    <div class="salary-card">
                        <div class="salary-label">Salario Anual</div>
                        <div class="salary-amount">{fs} €</div>
                    </div>''', unsafe_allow_html=True)
                else:
                    st.markdown('''
                    <div class="salary-card">
                        <div class="salary-label">Salario Anual</div>
                        <div class="salary-amount salary-na">No disponible</div>
                    </div>''', unsafe_allow_html=True)
                st.markdown('<div class="section-heading">📊 Datos Clave</div>', unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                if pd.notna(deputy_data.get('scraped_salary')) and deputy_data.get('scraped_salary'):
                    m1.metric("Salario", f"{float(deputy_data['scraped_salary']):,.0f}€".replace(",", "."))
                else:
                    m1.metric("Salario", "N/D")
                irpf = extract_irpf_value(deputy_data.get('irpf_cantidad_pagada', 0))
                m2.metric("IRPF", format_currency(irpf))
                m3.metric("Inmuebles", len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])) + len(parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))))
                m4.metric("Vehículos", len(parse_json_field(deputy_data['vehiculos'])))
                debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
                m5.metric("Deudas", len(debts))
                st.markdown("---")
                tabs = st.tabs(["💵 Ingresos", "🏠 Inmuebles", "💼 Sociedades", "💰 Activos", "🚗 Vehículos", "💳 Deudas", "📋 Actividades", "📄 Otros"])
                with tabs[0]:
                    st.markdown('<div class="section-heading">💵 Fuentes de Ingresos</div>', unsafe_allow_html=True)
                    st.info(f"**IRPF Pagado (Declarado): {format_currency_full(irpf)}**")
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        st.markdown("##### Salarios")
                        salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                        if salaries:
                            for i, s in enumerate(salaries):
                                if isinstance(s, dict):
                                    c = s.get('concepto', f'Ingreso #{i+1}')
                                    if str(c).lower() == 'nan': c = f'Ingreso #{i+1}'
                                    a = extract_debt_account_value(s.get('euros'))
                                    st.info(f"**{c}**"); st.markdown(f"→ **{format_currency_full(a)}**")
                        else: st.info("Sin salarios declarados")
                        st.markdown("##### Otras Rentas")
                        otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', ''))
                        if otras:
                            for item in otras:
                                if isinstance(item, dict):
                                    imp = extract_debt_account_value(item.get('euros', 0))
                                    if imp > 0: st.markdown(f"**{item.get('concepto', 'Otra renta')}**: {format_currency_full(imp)}")
                        else: st.info("Sin otras rentas")
                    with tc2:
                        st.markdown("##### Dividendos y Participaciones")
                        divs = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                        if divs:
                            for d in divs:
                                if isinstance(d, dict):
                                    c = d.get('concepto', 'Inversión')
                                    if str(c).lower() == 'nan': c = 'Inversión'
                                    st.markdown(f"**📊 {c}**")
                                    r = extract_debt_account_value(d.get('euros'))
                                    if r > 0: st.markdown(f"→ **{format_currency_full(r)}**")
                        else: st.info("Sin dividendos")
                        st.markdown("##### Intereses Financieros")
                        ints = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', ''))
                        if ints:
                            for item in ints:
                                if isinstance(item, dict):
                                    imp = extract_debt_account_value(item.get('euros', 0))
                                    if imp > 0: st.markdown(f"**{item.get('concepto', 'Interés')}**: {format_currency_full(imp)}")
                        else: st.info("Sin intereses financieros")
                with tabs[1]:
                    st.markdown('<div class="section-heading">🏠 Bienes Inmuebles</div>', unsafe_allow_html=True)
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        st.markdown("##### Inmuebles Urbanos")
                        urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                        if urban:
                            for i, p in enumerate(urban):
                                if isinstance(p, dict):
                                    st.markdown(f"**📍 Inmueble #{i+1}**")
                                    for k, v in p.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                                    st.markdown("")
                        else: st.info("Sin inmuebles urbanos")
                    with tc2:
                        st.markdown("##### Inmuebles Rústicos")
                        rust = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                        if rust:
                            for i, p in enumerate(rust):
                                if isinstance(p, dict):
                                    st.markdown(f"**🚜 Inmueble #{i+1}**")
                                    for k, v in p.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                                    st.markdown("")
                        else: st.info("Sin inmuebles rústicos")
                with tabs[2]:
                    st.markdown('<div class="section-heading">💼 Sociedades y Participaciones</div>', unsafe_allow_html=True)
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        st.markdown("##### Sociedades No Cotizadas")
                        socs = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                        if socs:
                            for i, s in enumerate(socs):
                                if isinstance(s, dict):
                                    st.markdown(f"**🏭 Sociedad #{i+1}**")
                                    for k, v in s.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                                    st.markdown("")
                        else: st.info("Sin sociedades no cotizadas")
                    with tc2:
                        st.markdown("##### Participaciones >5%")
                        parts = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                        if parts:
                            for i, p in enumerate(parts):
                                if isinstance(p, dict):
                                    st.markdown(f"**📈 Participación #{i+1}**")
                                    for k, v in p.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                                    st.markdown("")
                        else: st.info("Sin participaciones superiores al 5%")
                with tabs[3]:
                    st.markdown('<div class="section-heading">💰 Activos Financieros</div>', unsafe_allow_html=True)
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        st.markdown("##### Cuentas y Depósitos")
                        accs = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                        if accs:
                            total_accs = sum(extract_debt_account_value(a.get('saldo', 0)) for a in accs if isinstance(a, dict))
                            if total_accs > 0: st.success(f"**Total en cuentas: {format_currency_full(total_accs)}**")
                            for a in accs:
                                if isinstance(a, dict):
                                    desc = a.get('descripcion', 'Cuenta')
                                    if str(desc).lower() == 'nan': desc = 'Cuenta'
                                    saldo = extract_debt_account_value(a.get('saldo'))
                                    if saldo > 0:
                                        st.markdown(f"**🏦 {desc}**"); st.markdown(f"Saldo: **{format_currency_full(saldo)}**")
                        else: st.info("Sin cuentas declaradas")
                        st.markdown("##### Acciones y Participaciones")
                        accs2 = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                        if accs2:
                            for i, a in enumerate(accs2):
                                if isinstance(a, dict):
                                    st.markdown(f"**📊 Acción #{i+1}**")
                                    for k, v in a.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                        else: st.info("Sin acciones declaradas")
                    with tc2:
                        st.markdown("##### Deuda Pública y Valores")
                        dp = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
                        if dp:
                            for i, item in enumerate(dp):
                                if isinstance(item, dict):
                                    st.markdown(f"**💼 Valor #{i+1}**")
                                    for k, v in item.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                        else: st.info("Sin deuda pública o valores")
                with tabs[4]:
                    st.markdown('<div class="section-heading">🚗 Vehículos</div>', unsafe_allow_html=True)
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        st.info(f"**Total vehículos: {len(vehicles)}**")
                        cols = st.columns(2)
                        for i, v in enumerate(vehicles):
                            if isinstance(v, dict):
                                with cols[i % 2]:
                                    desc = v.get('descripcion', f'Vehículo #{i+1}')
                                    if str(desc).lower() == 'nan': desc = f'Vehículo #{i+1}'
                                    st.markdown(f"**🚗 {desc}**")
                                    f2 = v.get('fecha_adquisicion', '')
                                    if f2 and str(f2).lower() != 'nan': st.markdown(f"Adquirido: {f2}")
                                    st.markdown("")
                    else: st.info("Sin vehículos declarados")
                with tabs[5]:
                    st.markdown('<div class="section-heading">💸 Deudas y Obligaciones</div>', unsafe_allow_html=True)
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
                                tc1, tc2 = st.columns(2)
                                with tc1:
                                    if original > 0: st.markdown(f"Original: **{format_currency_full(original)}**")
                                    f2 = debt.get('fecha_concesion', '')
                                    if f2 and str(f2).lower() != 'nan': st.markdown(f"Fecha: {f2}")
                                with tc2:
                                    if pending > 0: st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                                    if original > 0 and pending > 0:
                                        pct = ((original - pending) / original) * 100
                                        st.progress(int(pct), text=f"Pagado: {pct:.1f}%")
                                st.markdown("---")
                    else: st.success("✅ No se han declarado deudas")
                with tabs[6]:
                    st.markdown('<div class="section-heading">📋 Actividades e Intereses</div>', unsafe_allow_html=True)
                    deputy_id = deputy_data.get('deputy_id')
                    deputy_interests = match_deputy_interests(deputy_id, interests_df)
                    display_interests_section(deputy_interests)
                with tabs[7]:
                    st.markdown('<div class="section-heading">📄 Otros Bienes y Derechos</div>', unsafe_allow_html=True)
                    otros = deputy_data.get('otros_bienes_no_declarados_anteriormente', '')
                    if otros and str(otros).lower() != 'nan':
                        st.markdown("##### Otros Bienes No Declarados Anteriormente")
                        parsed = parse_json_field(otros)
                        if parsed:
                            for i, item in enumerate(parsed):
                                if isinstance(item, dict):
                                    st.markdown(f"**Item #{i+1}**")
                                    for k, v in item.items():
                                        if v and str(v).lower() != 'nan': st.markdown(f"• {k.replace('_',' ').title()}: {v}")
                        else: st.write(otros)
                    else: st.info("No hay otros bienes declarados")
    st.markdown("---")
    render_footer()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if not st.session_state.disclaimer_accepted:
    show_disclaimer()
else:
    main_app()
