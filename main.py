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
    page_title="Deputies Registry",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced modern dark theme with gradient accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1600px;
    }
    
    /* Typography */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Deputy Card Container */
    .deputy-card {
        background: linear-gradient(135deg, rgba(30, 30, 60, 0.6) 0%, rgba(20, 20, 40, 0.8) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Image Gallery */
    .image-gallery {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        align-items: flex-start;
    }
    
    .main-image-container {
        position: relative;
        flex: 0 0 auto;
    }
    
    .main-image {
        width: 180px;
        height: 220px;
        object-fit: cover;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .badge-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        flex: 1;
    }
    
    .party-logo {
        width: 80px;
        height: 80px;
        object-fit: contain;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .seat-indicator {
        width: 120px;
        height: 60px;
        object-fit: contain;
        background: rgba(102, 126, 234, 0.1);
        padding: 8px;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Compact Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .info-item {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        transition: all 0.3s ease;
    }
    
    .info-item:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .info-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
        font-weight: 600;
    }
    
    .info-value {
        font-size: 1rem;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Enhanced Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Improved Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 30, 60, 0.3);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(102, 126, 234, 0.1);
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
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(102, 126, 234, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Social Media Pills */
    .social-pills {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .social-pill {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #e2e8f0;
        text-decoration: none;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .social-pill:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    /* Expandable Cards */
    .stExpander {
        background: rgba(30, 30, 60, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    .stExpander:hover {
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Input Fields */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: rgba(30, 30, 60, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Quick Stats Bar */
    .stats-bar {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stat-item {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        border-right: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stat-item:last-child {
        border-right: none;
    }
    
    .stat-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header { visibility: hidden; }
    .viewerBadge_container__1QSob { display: none; }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
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
    """Format currency values for display"""
    if not isinstance(value, (int, float)):
        return "€0"
    if value >= 1000000:
        return f"€{value/1000000:.1f}M"
    elif value >= 1000:
        return f"€{value/1000:.1f}K"
    else:
        return f"€{value:.0f}"

def format_currency_full(value):
    """Format currency values for detailed display"""
    if not isinstance(value, (int, float)):
        return "€0,00"
    return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
    if pd.notna(deputy_data['photo_path']) and os.path.exists(deputy_data['photo_path']):
        import base64
        with open(deputy_data['photo_path'], "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" class="main-image" alt="Deputy Photo">'
    else:
        gallery_html += '<div class="main-image" style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); display: flex; align-items: center; justify-content: center; color: #94a3b8;">👤 No Photo</div>'
    gallery_html += '</div>'
    
    # Badges container
    gallery_html += '<div class="badge-container">'
    
    # Party logo
    if pd.notna(deputy_data['logo_path']) and os.path.exists(deputy_data['logo_path']):
        import base64
        with open(deputy_data['logo_path'], "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="party-logo" alt="Party Logo">'
    
    # Seat indicator
    if pd.notna(deputy_data['hemiciclo_path']) and os.path.exists(deputy_data['hemiciclo_path']):
        import base64
        with open(deputy_data['hemiciclo_path'], "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="seat-indicator" alt="Seat Position">'
    
    gallery_html += '</div></div>'
    return gallery_html

def main():
    # Header with gradient
    st.markdown('<h1 style="text-align: center; margin-bottom: 0;">⚖️ Deputies Registry</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1rem; margin-top: 0;">SPANISH CONGRESS · Financial Transparency Portal</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    # Search and Filters in a compact layout
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            search_term = st.text_input("🔍", placeholder="Search deputy by name...", label_visibility="collapsed")
        with col2:
            constituencies = ['All Constituencies'] + sorted([c for c in df['informacion_personal_circunscripcion'].dropna().unique() if c != 'nan'])
            selected_constituency = st.selectbox("📍", constituencies, label_visibility="collapsed")
        with col3:
            civil_status = ['All Status'] + sorted([s for s in df['informacion_personal_estado_civil'].dropna().unique()])
            selected_status = st.selectbox("💑", civil_status, label_visibility="collapsed")
        
        # Filter data
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
        if selected_constituency != 'All Constituencies':
            filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
        if selected_status != 'All Status':
            filtered_df = filtered_df[filtered_df['informacion_personal_estado_civil'] == selected_status]
        
        with col4:
            st.metric("", f"{len(filtered_df)} Results", label_visibility="collapsed")
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("🔍 No deputies found matching your criteria")
    else:
        # Deputy selector with better formatting
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "Select Deputy:",
            deputy_names,
            format_func=lambda x: f"👤 {x}",
            label_visibility="collapsed"
        )
        
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        # Main Deputy Card
        st.markdown('<div class="deputy-card">', unsafe_allow_html=True)
        
        # Create two-column layout with image gallery on left
        col_left, col_right = st.columns([1.2, 2])
        
        with col_left:
            # Compact image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info in compact grid
            st.markdown(f"""
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">📋 Position</div>
                    <div class="info-value">{deputy_data.get('informacion_personal_cargo', 'Deputy')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">📍 Constituency</div>
                    <div class="info-value">{deputy_data.get('informacion_personal_circunscripcion', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">💑 Status</div>
                    <div class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">📅 Election</div>
                    <div class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'N/A')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Social Media Links as pills
            social_links = {
                "𝕏": deputy_data.get('twitter'),
                "Facebook": deputy_data.get('facebook'),
                "Instagram": deputy_data.get('instagram'),
                "Website": deputy_data.get('website')
            }
            
            valid_links = {label: url for label, url in social_links.items() if pd.notna(url)}
            
            if valid_links:
                st.markdown("**🌐 Social Media**")
                social_html = '<div class="social-pills">'
                for label, url in valid_links.items():
                    social_html += f'<a href="{url}" target="_blank" class="social-pill">{label}</a>'
                social_html += '</div>'
                st.markdown(social_html, unsafe_allow_html=True)
        
        with col_right:
            # Deputy name with style
            st.markdown(f"## {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
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
            
            # Financial Overview - Compact metrics
            st.markdown("### 💰 Financial Overview")
            metric_cols = st.columns(6)
            metric_cols[0].metric("Income", format_currency(total_salary), help="Annual income")
            metric_cols[1].metric("IRPF", format_currency(irpf), help="Taxes paid")
            metric_cols[2].metric("Tax Rate", f"{tax_rate:.1f}%", help="Effective tax rate")
            metric_cols[3].metric("Properties", f"{properties_count}", help="Real estate owned")
            metric_cols[4].metric("Vehicles", f"{vehicles_count}", help="Vehicles owned")
            metric_cols[5].metric("Debt", format_currency(total_debt), help="Total outstanding debt")
            
            st.markdown("---")
            
            # Compact tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💵 Income", "🏠 Assets", "💳 Liabilities", "📊 Analysis"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💼 Salary & Income")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                with st.expander(f"💰 {salary.get('concepto', f'Income #{i+1}')}"):
                                    amount = extract_currency_value(salary.get('euros'))
                                    display_amount = format_currency_full(amount)
                                    if "mensual" in str(salary.get('euros', '')).lower():
                                        display_amount += " (monthly)"
                                    st.markdown(f"**Amount:** {display_amount}")
                    else:
                        st.info("No income sources declared")
                
                with col2:
                    st.markdown("#### 📈 Investment Income")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        for div in dividends:
                            if isinstance(div, dict):
                                with st.expander(f"📊 {div.get('concepto', 'Investment')}"):
                                    st.markdown(f"**Returns:** {format_currency_full(extract_currency_value(div.get('euros')))}")
                    else:
                        st.info("No investment income declared")
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏠 Real Estate")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                with st.expander(f"🏢 Property #{i+1}"):
                                    st.markdown(f"**Type:** {prop.get('clase_y_caracteristicas', 'Property')}")
                                    st.markdown(f"**Location:** {prop.get('situacion', 'N/A')}")
                                    st.markdown(f"**Acquired:** {prop.get('fecha_adquisicion', 'N/A')}")
                    else:
                        st.info("No properties declared")
                    
                    st.markdown("#### 💳 Financial Assets")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        for i, account in enumerate(accounts):
                            if isinstance(account, dict):
                                with st.expander(f"🏦 {account.get('descripcion', f'Account #{i+1}')}"):
                                    st.markdown(f"**Balance:** {format_currency_full(extract_currency_value(account.get('saldo')))}")
                    else:
                        st.info("No accounts declared")
                
                with col2:
                    st.markdown("#### 🚗 Vehicles")
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                with st.expander(f"🚙 {vehicle.get('descripcion', f'Vehicle #{i+1}')}"):
                                    st.markdown(f"**Acquired:** {vehicle.get('fecha_adquisicion', 'N/A')}")
                    else:
                        st.info("No vehicles declared")
            
            with tab3:
                st.markdown("#### 💸 Outstanding Debts")
                if debts:
                    # Summary card
                    st.info(f"**Total Outstanding Debt:** {format_currency_full(total_debt)}")
                    
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            with st.expander(f"📄 {debt.get('descripcion', f'Debt #{i+1}')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Original:** {format_currency_full(extract_currency_value(debt.get('importe_concedido')))}")
                                    st.markdown(f"**Grant Date:** {debt.get('fecha_concesion', 'N/A')}")
                                with col2:
                                    st.markdown(f"**Outstanding:** {format_currency_full(extract_currency_value(debt.get('saldo_pendiente')))}")
                                    original = extract_currency_value(debt.get('importe_concedido'))
                                    pending = extract_currency_value(debt.get('saldo_pendiente'))
                                    if original > 0:
                                        paid_pct = ((original - pending) / original) * 100
                                        st.markdown(f"**Paid:** {paid_pct:.1f}%")
                else:
                    st.success("✅ No debts declared")
            
            with tab4:
                st.markdown("#### 📊 Financial Analysis")
                
                # Create analysis visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Asset Distribution Pie Chart
                    fig_assets = go.Figure(data=[go.Pie(
                        labels=['Properties', 'Vehicles', 'Cash/Accounts'],
                        values=[
                            properties_count * 150000,  # Estimated avg property value
                            vehicles_count * 20000,     # Estimated avg vehicle value
                            sum(extract_currency_value(a.get('saldo', 0)) for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']) if isinstance(a, dict))
                        ],
                        hole=.3,
                        marker_colors=['#667eea', '#764ba2', '#f093fb']
                    )])
                    fig_assets.update_layout(
                        title="Asset Distribution (Estimated)",
                        showlegend=True,
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_assets, use_container_width=True)
                
                with col2:
                    # Tax Efficiency Gauge
                    fig_tax = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=tax_rate,
                        title={'text': "Effective Tax Rate"},
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
