import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Deputies Information Portal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and beautiful styling
st.markdown("""
<style>
    /* Dark theme override */
    .stApp {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Custom card styling */
    .deputy-card {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(100, 100, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .deputy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(100, 100, 255, 0.2);
        border-color: rgba(100, 100, 255, 0.4);
    }
    
    .info-section {
        background: rgba(40, 40, 60, 0.6);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: scale(1.05);
        border-color: rgba(99, 102, 241, 0.6);
    }
    
    .header-gradient {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .social-link {
        display: inline-block;
        margin: 5px;
        padding: 8px 16px;
        border-radius: 25px;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .metric-label {
        color: #a0a0b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        color: #fff;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(20, 20, 35, 0.95);
    }
    
    /* Search box styling */
    .stTextInput > div > div > input {
        background: rgba(40, 40, 60, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        color: white;
    }
    
    .stSelectbox > div > div {
        background: rgba(40, 40, 60, 0.8);
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 30, 50, 0.5);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #a0a0b8;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
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
        return f"€{value:,.2f}"
    # Handle string values with euro symbol
    if isinstance(value, str):
        # Extract numeric value
        numeric = re.findall(r'[\d,\.]+', value)
        if numeric:
            return f"€{numeric[0]}"
    return str(value)

def create_financial_summary(row):
    """Create a financial summary visualization"""
    # Parse salary information
    salaries = parse_json_field(row['rentas_percibidas_percepciones_salariales'])
    total_salary = 0
    for salary in salaries:
        if isinstance(salary, dict) and 'euros' in salary and salary['euros']:
            amount = re.findall(r'[\d,\.]+', str(salary['euros']))
            if amount:
                total_salary += float(amount[0].replace(',', '').replace('.', '').replace('€', ''))
    
    # Get IRPF paid
    irpf = row['irpf_cantidad_pagada'] if pd.notna(row['irpf_cantidad_pagada']) else 0
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-label">Total Income</div>
            <div class="metric-value">{format_currency(total_salary)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-label">IRPF Paid</div>
            <div class="metric-value">{format_currency(irpf)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="metric-label">Tax Rate</div>
            <div class="metric-value">{tax_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

def display_properties(row):
    """Display property information"""
    urban = parse_json_field(row['bienes_patrimoniales_inmuebles_urbanos'])
    rural = parse_json_field(row['bienes_patrimoniales_inmuebles_rusticos'])
    vehicles = parse_json_field(row['vehiculos'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Real Estate")
        if urban:
            for prop in urban:
                if isinstance(prop, dict):
                    st.markdown(f"""
                    <div class="info-section">
                        <b>{prop.get('clase_y_caracteristicas', 'Property')}</b><br>
                        📍 {prop.get('situacion', 'N/A')}<br>
                        📅 Acquired: {prop.get('fecha_adquisicion', 'N/A')}<br>
                        📜 {prop.get('derecho_sobre_el_bien', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No urban properties declared")
    
    with col2:
        st.markdown("### 🚗 Vehicles")
        if vehicles:
            for vehicle in vehicles:
                if isinstance(vehicle, dict):
                    st.markdown(f"""
                    <div class="info-section">
                        <b>{vehicle.get('descripcion', 'Vehicle')}</b><br>
                        📅 Acquired: {vehicle.get('fecha_adquisicion', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No vehicles declared")

def display_social_media(row):
    """Display social media links"""
    social_links = []
    
    if pd.notna(row['twitter']):
        social_links.append(f"[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)]({row['twitter']})")
    if pd.notna(row['instagram']):
        social_links.append(f"[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)]({row['instagram']})")
    if pd.notna(row['facebook']):
        social_links.append(f"[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)]({row['facebook']})")
    if pd.notna(row['website']):
        social_links.append(f"[![Website](https://img.shields.io/badge/Website-000000?style=for-the-badge&logo=About.me&logoColor=white)]({row['website']})")
    
    if social_links:
        st.markdown(" ".join(social_links))
    else:
        st.info("No social media profiles available")

def main():
    # Header
    st.markdown('<h1 class="header-gradient">🏛️ Deputies Information Portal</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #a0a0b8; font-size: 1.2rem;">Explore comprehensive information about Spanish deputies</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("## 🔍 Search & Filter")
        
        # Search by name
        search_term = st.text_input("🔎 Search by name", placeholder="Enter deputy name...")
        
        # Filter by constituency
        constituencies = ['All'] + sorted([c for c in df['informacion_personal_circunscripcion'].dropna().unique()])
        selected_constituency = st.selectbox("📍 Constituency", constituencies)
        
        # Filter by civil status
        civil_status = ['All'] + sorted([s for s in df['informacion_personal_estado_civil'].dropna().unique()])
        selected_status = st.selectbox("💑 Civil Status", civil_status)
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
        
        if selected_constituency != 'All':
            filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
        
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['informacion_personal_estado_civil'] == selected_status]
        
        st.markdown("---")
        st.markdown(f"### 📊 Results: {len(filtered_df)} deputies")
        
        # Statistics
        if len(filtered_df) > 0:
            avg_irpf = filtered_df['irpf_cantidad_pagada'].mean()
            st.metric("Average IRPF Paid", format_currency(avg_irpf))
    
    # Main content area
    if len(filtered_df) == 0:
        st.warning("No deputies found matching your criteria. Please adjust your filters.")
    else:
        # Deputy selector
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "Select a Deputy",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        # Get selected deputy data
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        # Display deputy information
        st.markdown('<div class="deputy-card">', unsafe_allow_html=True)
        
        # Header with photo
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if pd.notna(deputy_data['photo_path']):
                try:
                    st.image(deputy_data['photo_path'], width=150, caption="Deputy Photo")
                except:
                    st.markdown("👤", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"# {deputy_data['informacion_personal_nombre_y_apellidos']}")
            st.markdown(f"**Position:** {deputy_data.get('informacion_personal_cargo', 'N/A')}")
            st.markdown(f"**Constituency:** {deputy_data.get('informacion_personal_circunscripcion', 'N/A')}")
            st.markdown(f"**Civil Status:** {deputy_data.get('informacion_personal_estado_civil', 'N/A')}")
            if pd.notna(deputy_data.get('informacion_personal_fecha_eleccion')):
                st.markdown(f"**Election Date:** {deputy_data['informacion_personal_fecha_eleccion']}")
        
        with col3:
            if pd.notna(deputy_data['logo_path']):
                try:
                    st.image(deputy_data['logo_path'], width=100, caption="Party Logo")
                except:
                    pass
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabs for different information sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Financial", "🏠 Assets", "💳 Debts", "📱 Social Media", "📊 Analysis"])
        
        with tab1:
            st.markdown("### 💰 Financial Information")
            create_financial_summary(deputy_data)
            
            # Detailed income breakdown
            st.markdown("#### 📋 Income Sources")
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            if salaries:
                for salary in salaries:
                    if isinstance(salary, dict):
                        concept = salary.get('concepto', 'Unknown')
                        amount = salary.get('euros', 'N/A')
                        st.markdown(f"""
                        <div class="info-section">
                            <b>{concept}</b><br>
                            💶 {amount}
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 🏠 Assets & Properties")
            display_properties(deputy_data)
            
            # Bank accounts
            st.markdown("### 💳 Bank Accounts")
            accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
            if accounts:
                for account in accounts:
                    if isinstance(account, dict):
                        st.markdown(f"""
                        <div class="info-section">
                            <b>{account.get('descripcion', 'Account')}</b><br>
                            💰 Balance: {account.get('saldo', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown("### 💳 Debts & Obligations")
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            if debts:
                total_debt = 0
                for debt in debts:
                    if isinstance(debt, dict):
                        st.markdown(f"""
                        <div class="info-section">
                            <b>{debt.get('descripcion', 'Debt')}</b><br>
                            📅 Granted: {debt.get('fecha_concesion', 'N/A')}<br>
                            💵 Original: {debt.get('importe_concedido', 'N/A')}<br>
                            ⏳ Pending: {debt.get('saldo_pendiente', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("No debts declared")
        
        with tab4:
            st.markdown("### 📱 Social Media Presence")
            display_social_media(deputy_data)
        
        with tab5:
            st.markdown("### 📊 Comparative Analysis")
            
            # Compare with constituency average
            if pd.notna(deputy_data['informacion_personal_circunscripcion']):
                constituency_df = df[df['informacion_personal_circunscripcion'] == deputy_data['informacion_personal_circunscripcion']]
                
                if len(constituency_df) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # IRPF comparison
                        avg_constituency_irpf = constituency_df['irpf_cantidad_pagada'].mean()
                        deputy_irpf = deputy_data['irpf_cantidad_pagada'] if pd.notna(deputy_data['irpf_cantidad_pagada']) else 0
                        
                        fig = go.Figure(data=[
                            go.Bar(name='Deputy', x=['IRPF Paid'], y=[deputy_irpf], marker_color='#6366f1'),
                            go.Bar(name='Constituency Avg', x=['IRPF Paid'], y=[avg_constituency_irpf], marker_color='#8b5cf6')
                        ])
                        fig.update_layout(
                            title="IRPF Comparison",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Distribution pie chart
                        property_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
                        vehicle_count = len(parse_json_field(deputy_data['vehiculos']))
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=['Properties', 'Vehicles', 'Other Assets'],
                            values=[property_count, vehicle_count, max(1, property_count//2)],
                            hole=.3,
                            marker=dict(colors=['#6366f1', '#8b5cf6', '#ec4899'])
                        )])
                        fig.update_layout(
                            title="Asset Distribution",
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
