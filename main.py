import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Deputies Registry",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimalist dark theme with gold accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Main theme */
    .stApp {
        background: #0a0a0a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Deputy name header */
    .deputy-name {
        font-size: 3rem;
        font-weight: 200;
        letter-spacing: -2px;
        color: #fff;
        margin: 0;
        line-height: 1.1;
    }
    
    .deputy-title {
        font-size: 1.1rem;
        color: #888;
        font-weight: 300;
        margin-top: 0.5rem;
    }
    
    /* Info cards */
    .info-card {
        background: #111111;
        border: 1px solid #222;
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .info-card:hover {
        border-color: #444;
        background: #141414;
    }
    
    .card-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #666;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .card-value {
        font-size: 1.5rem;
        color: #fff;
        font-weight: 300;
    }
    
    .card-value.large {
        font-size: 2rem;
        font-weight: 200;
    }
    
    /* Gold accent for important values */
    .gold-accent {
        color: #d4af37;
    }
    
    /* Property item */
    .property-item {
        background: #0f0f0f;
        border-left: 2px solid #d4af37;
        padding: 1rem;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        color: #ccc;
    }
    
    .property-item strong {
        color: #fff;
        font-weight: 500;
    }
    
    /* Social media links - minimal style */
    .social-links {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .social-link {
        color: #666;
        text-decoration: none;
        font-size: 0.85rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid #333;
        border-radius: 3px;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .social-link:hover {
        color: #fff;
        border-color: #666;
        background: #1a1a1a;
    }
    
    /* Section headers */
    .section-header {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #666;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #222;
        font-weight: 600;
    }
    
    /* Data grid */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Search box */
    .stTextInput > div > div > input {
        background: #111;
        border: 1px solid #333;
        color: #fff;
        font-weight: 300;
        border-radius: 3px;
    }
    
    .stSelectbox > div > div {
        background: #111;
        border: 1px solid #333;
        border-radius: 3px;
    }
    
    /* Tabs - minimal style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #222;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #666;
        padding: 0.5rem 0;
        font-weight: 400;
        font-size: 0.95rem;
        border-radius: 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #fff;
        border-bottom: 2px solid #d4af37;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: #111;
        border: 1px solid #222;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    [data-testid="metric-container"] label {
        color: #666;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 300;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    .divider {
        height: 1px;
        background: #222;
        margin: 2rem 0;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    
    /* Photo container */
    .photo-container {
        width: 120px;
        height: 120px;
        border-radius: 4px;
        overflow: hidden;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
    
    .photo-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    df = pd.read_csv('deputies_full_dataset.csv')
    return df

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value == '[]' or field_value == '':
        return []
    try:
        return json.loads(field_value)
    except:
        return []

def format_currency(value):
    """Format currency values"""
    if pd.isna(value):
        return "€0"
    if isinstance(value, (int, float)):
        return f"€{value:,.0f}"
    if isinstance(value, str):
        numeric = re.findall(r'[\d,\.]+', value)
        if numeric:
            try:
                num = float(numeric[0].replace(',', '').replace('.', ''))
                return f"€{num:,.0f}"
            except:
                return str(value)
    return str(value)

def extract_currency_value(value_str):
    """Extract numeric value from currency string"""
    if pd.isna(value_str) or value_str == '':
        return 0
    if isinstance(value_str, (int, float)):
        return float(value_str)
    numeric = re.findall(r'[\d,\.]+', str(value_str))
    if numeric:
        try:
            return float(numeric[0].replace(',', '').replace('.', ''))
        except:
            return 0
    return 0

def main():
    # Header
    st.markdown('<h1 class="main-header">Deputies Registry</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">SPANISH CONGRESS · FINANCIAL DECLARATIONS</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Top search bar
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        search_term = st.text_input("", placeholder="Search deputy by name...", label_visibility="collapsed")
    
    with col2:
        constituencies = ['All Constituencies'] + sorted([c for c in df['informacion_personal_circunscripcion'].dropna().unique()])
        selected_constituency = st.selectbox("", constituencies, label_visibility="collapsed")
    
    with col3:
        civil_status = ['All Status'] + sorted([s for s in df['informacion_personal_estado_civil'].dropna().unique()])
        selected_status = st.selectbox("", civil_status, label_visibility="collapsed")
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
    
    if selected_constituency != 'All Constituencies':
        filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
    
    if selected_status != 'All Status':
        filtered_df = filtered_df[filtered_df['informacion_personal_estado_civil'] == selected_status]
    
    with col4:
        st.markdown(f'<div style="text-align: right; color: #666; margin-top: 2rem;">{len(filtered_df)} results</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if len(filtered_df) == 0:
        st.markdown('<div class="empty-state">No deputies found matching your criteria</div>', unsafe_allow_html=True)
    else:
        # Deputy selector (minimal dropdown)
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "Select Deputy",
            deputy_names,
            label_visibility="collapsed"
        )
        
        # Get selected deputy data
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        # Main content layout
        col_left, col_right = st.columns([1, 3])
        
        with col_left:
            # Photo
            if pd.notna(deputy_data['photo_path']):
                try:
                    st.image(deputy_data['photo_path'], width=180)
                except:
                    st.markdown('<div class="photo-container"><div style="padding: 3rem; color: #444;">No photo</div></div>', unsafe_allow_html=True)
            
            # Basic info
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="color: #666; font-size: 0.8rem; margin-bottom: 0.3rem;">POSITION</div>
                <div style="color: #fff; margin-bottom: 1rem;">{deputy_data.get('informacion_personal_cargo', 'Deputy')}</div>
                
                <div style="color: #666; font-size: 0.8rem; margin-bottom: 0.3rem;">CONSTITUENCY</div>
                <div style="color: #fff; margin-bottom: 1rem;">{deputy_data.get('informacion_personal_circunscripcion', 'N/A')}</div>
                
                <div style="color: #666; font-size: 0.8rem; margin-bottom: 0.3rem;">CIVIL STATUS</div>
                <div style="color: #fff; margin-bottom: 1rem;">{deputy_data.get('informacion_personal_estado_civil', 'N/A')}</div>
                
                <div style="color: #666; font-size: 0.8rem; margin-bottom: 0.3rem;">ELECTED</div>
                <div style="color: #fff; margin-bottom: 1rem;">{deputy_data.get('informacion_personal_fecha_eleccion', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Social media - compact links
            social_html = '<div style="margin-top: 2rem;">'
            if pd.notna(deputy_data['twitter']):
                social_html += f'<a href="{deputy_data["twitter"]}" target="_blank" class="social-link">Twitter</a> '
            if pd.notna(deputy_data['instagram']):
                social_html += f'<a href="{deputy_data["instagram"]}" target="_blank" class="social-link">Instagram</a> '
            if pd.notna(deputy_data['facebook']):
                social_html += f'<a href="{deputy_data["facebook"]}" target="_blank" class="social-link">Facebook</a> '
            if pd.notna(deputy_data['website']):
                social_html += f'<a href="{deputy_data["website"]}" target="_blank" class="social-link">Web</a>'
            social_html += '</div>'
            
            if any([pd.notna(deputy_data[x]) for x in ['twitter', 'instagram', 'facebook', 'website']]):
                st.markdown(social_html, unsafe_allow_html=True)
        
        with col_right:
            # Deputy name
            st.markdown(f'<h1 class="deputy-name">{deputy_data["informacion_personal_nombre_y_apellidos"]}</h1>', unsafe_allow_html=True)
            
            # Financial summary
            st.markdown('<div class="section-header">FINANCIAL OVERVIEW</div>', unsafe_allow_html=True)
            
            # Calculate totals
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = 0
            for salary in salaries:
                if isinstance(salary, dict) and 'euros' in salary and salary['euros']:
                    total_salary += extract_currency_value(salary['euros'])
            
            irpf = deputy_data['irpf_cantidad_pagada'] if pd.notna(deputy_data['irpf_cantidad_pagada']) else 0
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            
            # Financial metrics
            fcol1, fcol2, fcol3, fcol4 = st.columns(4)
            with fcol1:
                st.markdown(f"""
                <div class="info-card">
                    <div class="card-label">Annual Income</div>
                    <div class="card-value">{format_currency(total_salary)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with fcol2:
                st.markdown(f"""
                <div class="info-card">
                    <div class="card-label">IRPF Paid</div>
                    <div class="card-value gold-accent">{format_currency(irpf)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with fcol3:
                st.markdown(f"""
                <div class="info-card">
                    <div class="card-label">Tax Rate</div>
                    <div class="card-value">{tax_rate:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with fcol4:
                # Count properties
                properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
                st.markdown(f"""
                <div class="info-card">
                    <div class="card-label">Properties</div>
                    <div class="card-value">{properties}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tabs for detailed information
            tab1, tab2, tab3, tab4 = st.tabs(["Income", "Assets", "Liabilities", "Analysis"])
            
            with tab1:
                st.markdown('<div class="section-header">INCOME SOURCES</div>', unsafe_allow_html=True)
                
                if salaries:
                    for salary in salaries:
                        if isinstance(salary, dict):
                            concept = salary.get('concepto', 'Unknown')
                            amount = salary.get('euros', 'N/A')
                            st.markdown(f"""
                            <div class="property-item">
                                <strong>{concept}</strong><br>
                                <span class="gold-accent">{amount}</span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color: #666;">No income sources declared</div>', unsafe_allow_html=True)
                
                # Other income
                dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                if dividends and len(dividends) > 0:
                    st.markdown('<div class="section-header">DIVIDENDS</div>', unsafe_allow_html=True)
                    for div in dividends:
                        if isinstance(div, dict):
                            st.markdown(f"""
                            <div class="property-item">
                                <strong>{div.get('concepto', 'Dividend')}</strong><br>
                                {div.get('euros', 'N/A')}
                            </div>
                            """, unsafe_allow_html=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="section-header">REAL ESTATE</div>', unsafe_allow_html=True)
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for prop in urban:
                            if isinstance(prop, dict):
                                st.markdown(f"""
                                <div class="property-item">
                                    <strong>{prop.get('clase_y_caracteristicas', 'Property')}</strong><br>
                                    {prop.get('situacion', 'N/A')} · {prop.get('fecha_adquisicion', 'N/A')}<br>
                                    <span style="color: #888; font-size: 0.85rem;">{prop.get('derecho_sobre_el_bien', 'N/A')}</span>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #666;">No properties declared</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="section-header">VEHICLES</div>', unsafe_allow_html=True)
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        for vehicle in vehicles:
                            if isinstance(vehicle, dict):
                                st.markdown(f"""
                                <div class="property-item">
                                    <strong>{vehicle.get('descripcion', 'Vehicle')}</strong><br>
                                    Acquired: {vehicle.get('fecha_adquisicion', 'N/A')}
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #666;">No vehicles declared</div>', unsafe_allow_html=True)
                
                # Bank accounts
                st.markdown('<div class="section-header">BANK ACCOUNTS</div>', unsafe_allow_html=True)
                accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                if accounts:
                    for account in accounts:
                        if isinstance(account, dict):
                            st.markdown(f"""
                            <div class="property-item">
                                <strong>{account.get('descripcion', 'Account')}</strong><br>
                                Balance: <span class="gold-accent">{account.get('saldo', 'N/A')}</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            with tab3:
                st.markdown('<div class="section-header">DEBTS & OBLIGATIONS</div>', unsafe_allow_html=True)
                debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
                if debts:
                    total_debt = 0
                    for debt in debts:
                        if isinstance(debt, dict):
                            pending = extract_currency_value(debt.get('saldo_pendiente', 0))
                            total_debt += pending
                            st.markdown(f"""
                            <div class="property-item">
                                <strong>{debt.get('descripcion', 'Debt')}</strong><br>
                                Granted: {debt.get('fecha_concesion', 'N/A')}<br>
                                Original: {debt.get('importe_concedido', 'N/A')}<br>
                                <span class="gold-accent">Pending: {debt.get('saldo_pendiente', 'N/A')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown(f'<div style="margin-top: 2rem; padding: 1rem; background: #111; border-left: 3px solid #d4af37;"><strong>Total Debt:</strong> <span class="gold-accent">{format_currency(total_debt)}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color: #666;">No debts declared</div>', unsafe_allow_html=True)
            
            with tab4:
                st.markdown('<div class="section-header">COMPARATIVE ANALYSIS</div>', unsafe_allow_html=True)
                
                if pd.notna(deputy_data['informacion_personal_circunscripcion']):
                    constituency_df = df[df['informacion_personal_circunscripcion'] == deputy_data['informacion_personal_circunscripcion']]
                    
                    if len(constituency_df) > 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Tax comparison
                            avg_constituency_irpf = constituency_df['irpf_cantidad_pagada'].mean()
                            deputy_irpf = deputy_data['irpf_cantidad_pagada'] if pd.notna(deputy_data['irpf_cantidad_pagada']) else 0
                            
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                x=['This Deputy', f'{deputy_data["informacion_personal_circunscripcion"]} Average'],
                                y=[deputy_irpf, avg_constituency_irpf],
                                marker_color=['#d4af37', '#444'],
                                text=[format_currency(deputy_irpf), format_currency(avg_constituency_irpf)],
                                textposition='outside',
                                textfont=dict(color='white', size=12)
                            ))
                            
                            fig.update_layout(
                                title="IRPF Tax Comparison",
                                title_font=dict(size=12, color='#666'),
                                plot_bgcolor='#0a0a0a',
                                paper_bgcolor='#0a0a0a',
                                font=dict(color='#666'),
                                height=300,
                                showlegend=False,
                                yaxis=dict(showgrid=True, gridcolor='#222', zeroline=False),
                                xaxis=dict(showgrid=False)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Calculate net worth estimate
                            properties_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
                            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
                            accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                            
                            total_accounts = 0
                            for acc in accounts:
                                if isinstance(acc, dict):
                                    total_accounts += extract_currency_value(acc.get('saldo', 0))
                            
                            # Asset composition
                            fig = go.Figure(data=[go.Pie(
                                labels=['Properties', 'Vehicles', 'Liquid Assets'],
                                values=[properties_count * 150000, vehicles_count * 25000, total_accounts],
                                hole=.5,
                                marker=dict(colors=['#d4af37', '#888', '#555']),
                                textfont=dict(color='white'),
                                hoverinfo='label+percent'
                            )])
                            
                            fig.update_layout(
                                title="Estimated Asset Distribution",
                                title_font=dict(size=12, color='#666'),
                                plot_bgcolor='#0a0a0a',
                                paper_bgcolor='#0a0a0a',
                                font=dict(color='#666'),
                                height=300,
                                showlegend=True,
                                legend=dict(font=dict(color='#666'))
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Percentile ranking
                        all_irpf = df['irpf_cantidad_pagada'].dropna()
                        percentile = (all_irpf < deputy_irpf).sum() / len(all_irpf) * 100
                        
                        st.markdown(f"""
                        <div style="margin-top: 2rem; padding: 1rem; background: #111; border-radius: 4px;">
                            <strong>Tax Contribution Ranking:</strong> This deputy's IRPF payment is in the <span class="gold-accent">{percentile:.0f}th percentile</span> among all deputies
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
