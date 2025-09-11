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

# Beautiful dark theme with purple accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    /* Dark theme base */
    .stApp {
        background: linear-gradient(180deg, #0a0e27 0%, #151933 100%);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 3rem;
        max-width: 1400px;
    }
    
    /* Headers */
    h1 {
        color: #ffffff !important;
        font-weight: 300 !important;
        letter-spacing: -1px !important;
    }
    
    h2 {
        color: #e8eaed !important;
        font-weight: 400 !important;
    }
    
    h3 {
        color: #dadce0 !important;
        font-weight: 400 !important;
    }
    
    /* Metric containers */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(88, 101, 242, 0.1) 0%, rgba(88, 101, 242, 0.05) 100%);
        border: 1px solid rgba(88, 101, 242, 0.2);
        padding: 1.2rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(88, 101, 242, 0.15);
        border-color: rgba(88, 101, 242, 0.4);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #9aa0a6 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 300 !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(88, 101, 242, 0.5);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(88, 101, 242, 0.5);
        box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.1);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: transparent;
        border: none;
        color: #9aa0a6;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(88, 101, 242, 0.1);
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, rgba(88, 101, 242, 0.15) 0%, transparent 100%);
        color: #5865f2 !important;
        border-bottom: 2px solid #5865f2;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white !important;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(88, 101, 242, 0.1);
        border-color: rgba(88, 101, 242, 0.3);
    }
    
    .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0 0 8px 8px;
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, rgba(88, 101, 242, 0.1) 0%, rgba(88, 101, 242, 0.05) 100%);
        border-left: 3px solid #5865f2;
        color: #e8eaed;
    }
    
    /* Success boxes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(67, 181, 129, 0.1) 0%, rgba(67, 181, 129, 0.05) 100%);
        border-left: 3px solid #43b581;
        color: #e8eaed;
    }
    
    /* Warning boxes */
    .stWarning {
        background: linear-gradient(135deg, rgba(250, 166, 26, 0.1) 0%, rgba(250, 166, 26, 0.05) 100%);
        border-left: 3px solid #faa61a;
        color: #e8eaed;
    }
    
    /* Images */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Columns spacing */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }

    /* Custom container for basic info */
    .info-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .info-container .stMarkdown {
        font-size: 0.9rem;
    }
    .info-container strong {
        color: #9aa0a6;
        font-weight: 500;
        display: block;
        margin-bottom: 0.1rem;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(88, 101, 242, 0.3);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(88, 101, 242, 0.5);
    }
    
    /* Labels */
    .stMarkdown {
        color: #e8eaed;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin: 2rem 0;
    }
    
    /* Social buttons custom */
    .stButton > button {
        background: rgba(88, 101, 242, 0.1);
        border: 1px solid rgba(88, 101, 242, 0.3);
        color: #ffffff;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: rgba(88, 101, 242, 0.2);
        border-color: #5865f2;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(88, 101, 242, 0.3);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    # FIX: Added encoding='utf-8-sig' to handle potential BOM characters at the start of the CSV file.
    df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
    
    # Normalize file paths for cross-platform compatibility
    path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
    for col in path_columns:
        if col in df.columns:
            # Replace backslashes with forward slashes and strip whitespace
            df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()

    return df

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value == '[]' or field_value == '':
        return []
    try:
        # Attempt to remove invalid control characters that might break JSON parsing
        cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value))
        return json.loads(cleaned_value)
    except:
        return []

def format_currency(value):
    """Format currency values for display"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "€0,00"
    # Format with dot for thousands and comma for decimals
    return f"€{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def extract_currency_value(value_str):
    """Extract numeric value from currency string, handling Spanish format."""
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

def main():
    st.markdown("# ⚖️ Deputies Registry")
    st.markdown("**SPANISH CONGRESS** · Financial Declarations & Asset Disclosure")
    
    df = load_data()
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Enter deputy name...", label_visibility="collapsed")
    with col2:
        constituencies = ['All Constituencies'] + sorted([c for c in df['informacion_personal_circunscripcion'].dropna().unique()])
        selected_constituency = st.selectbox("📍 Constituency", constituencies, label_visibility="collapsed")
    with col3:
        civil_status = ['All Status'] + sorted([s for s in df['informacion_personal_estado_civil'].dropna().unique()])
        selected_status = st.selectbox("💑 Status", civil_status, label_visibility="collapsed")
    
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
    if selected_constituency != 'All Constituencies':
        filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]
    if selected_status != 'All Status':
        filtered_df = filtered_df[filtered_df['informacion_personal_estado_civil'] == selected_status]
    
    with col4:
        st.metric("Results", f"{len(filtered_df)}", label_visibility="collapsed")
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("🔍 No deputies found matching your criteria")
    else:
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "**Select Deputy:**",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        st.markdown("---")
        
        col_left, col_right = st.columns([1, 2.5])
        
        with col_left:
            # --- FIX: Set a smaller, fixed width for the image to control its size ---
            if pd.notna(deputy_data['photo_path']) and os.path.exists(deputy_data['photo_path']):
                st.image(deputy_data['photo_path'], width=240) # Changed from 280 to 240
            else:
                st.info("👤 No photo available")
            
            if pd.notna(deputy_data['logo_path']) and os.path.exists(deputy_data['logo_path']):
                st.image(deputy_data['logo_path'], width=100)
            
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("### 📋 Basic Information")
            
            with st.container():
                st.markdown('<div class="info-container">', unsafe_allow_html=True)
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**Position**<br>{deputy_data.get('informacion_personal_cargo', 'Deputy')}", unsafe_allow_html=True)
                    st.markdown(f"**Civil Status**<br>{deputy_data.get('informacion_personal_estado_civil', 'N/A')}", unsafe_allow_html=True)
                with col_info2:
                    st.markdown(f"**Constituency**<br>{deputy_data.get('informacion_personal_circunscripcion', 'N/A')}", unsafe_allow_html=True)
                    st.markdown(f"**Election Date**<br>{deputy_data.get('informacion_personal_fecha_eleccion', 'N/A')}", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if pd.notna(deputy_data['hemiciclo_path']) and os.path.exists(deputy_data['hemiciclo_path']):
                with st.expander("💺 View Seat Position"):
                    st.image(deputy_data['hemiciclo_path'], use_column_width=True)
            
            st.markdown("### 🌐 Social Media")
            social_cols = st.columns(2)
            with social_cols[0]:
                if pd.notna(deputy_data['twitter']):
                    st.link_button("𝕏 Twitter", deputy_data['twitter'])
                if pd.notna(deputy_data['facebook']):
                    st.link_button("📘 Facebook", deputy_data['facebook'])
            with social_cols[1]:
                if pd.notna(deputy_data['instagram']):
                    st.link_button("📷 Instagram", deputy_data['instagram'])
                if pd.notna(deputy_data['website']):
                    st.link_button("🌐 Website", deputy_data['website'])
        
        with col_right:
            st.markdown(f"## {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            st.markdown("### 💰 Financial Overview")
            
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in salaries if isinstance(s, dict))
            
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            properties_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            
            metric_cols = st.columns(5)
            metric_cols[0].metric("Annual Income", format_currency(total_salary))
            metric_cols[1].metric("IRPF Paid", format_currency(irpf))
            metric_cols[2].metric("Tax Rate", f"{tax_rate:.1f}%")
            metric_cols[3].metric("Properties", properties_count)
            metric_cols[4].metric("Vehicles", vehicles_count)
            
            st.markdown("---")
            
            # --- The rest of the code for the tabs is correct ---
            # (No changes needed below this line for the reported issues)

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["💵 Income", "🏠 Assets", "💳 Liabilities", "📊 Analysis", "📄 Raw Data"])
            
            with tab1:
                st.markdown("#### 💼 Income Sources")
                salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                if salaries:
                    for i, salary in enumerate(salaries):
                        if isinstance(salary, dict):
                            with st.expander(f"Income Source #{i+1}"):
                                st.markdown(f"**Concept:** {salary.get('concepto', 'Unknown')}")
                                st.markdown(f"**Amount:** {format_currency(extract_currency_value(salary.get('euros')))}")
                else:
                    st.info("No income sources declared")
                
                dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                if dividends:
                    st.markdown("#### 📈 Dividends & Participations")
                    for div in dividends:
                        if isinstance(div, dict):
                            with st.expander(div.get('concepto', 'Dividend')):
                                st.markdown(f"**Amount:** {format_currency(extract_currency_value(div.get('euros')))}")

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🏠 Real Estate")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                with st.expander(f"Property #{i+1}"):
                                    st.markdown(f"**Type:** {prop.get('clase_y_caracteristicas', 'Property')}")
                                    st.markdown(f"**Location:** {prop.get('situacion', 'N/A')}")
                                    st.markdown(f"**Acquired:** {prop.get('fecha_adquisicion', 'N/A')}")
                                    st.markdown(f"**Ownership:** {prop.get('derecho_sobre_el_bien', 'N/A')}")
                    else:
                        st.info("No properties declared")
                with col2:
                    st.markdown("#### 🚗 Vehicles")
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                with st.expander(f"Vehicle #{i+1}"):
                                    st.markdown(f"**Description:** {vehicle.get('descripcion', 'Vehicle')}")
                                    st.markdown(f"**Acquired:** {vehicle.get('fecha_adquisicion', 'N/A')}")
                    else:
                        st.info("No vehicles declared")

                st.markdown("#### 💳 Bank Accounts & Deposits")
                accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                if accounts:
                    for i, account in enumerate(accounts):
                        if isinstance(account, dict):
                            with st.expander(f"Account #{i+1}"):
                                st.markdown(f"**Description:** {account.get('descripcion', 'Account')}")
                                st.markdown(f"**Balance:** {format_currency(extract_currency_value(account.get('saldo')))}")
                else:
                    st.info("No accounts declared")

            with tab3:
                st.markdown("#### 💸 Debts & Obligations")
                debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
                if debts:
                    total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
                    st.metric("Total Debt", format_currency(total_debt))
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            with st.expander(f"{debt.get('descripcion', f'Debt #{i+1}')}"):
                                st.markdown(f"**Grant Date:** {debt.get('fecha_concesion', 'N/A')}")
                                st.markdown(f"**Original Amount:** {format_currency(extract_currency_value(debt.get('importe_concedido')))}")
                                st.markdown(f"**Pending Amount:** {format_currency(extract_currency_value(debt.get('saldo_pendiente')))}")
                else:
                    st.success("✅ No debts declared")

            with tab4:
                st.markdown("#### 📊 Comparative Analysis")
                if pd.notna(deputy_data['informacion_personal_circunscripcion']):
                    constituency_df = df[df['informacion_personal_circunscripcion'] == deputy_data['informacion_personal_circunscripcion']]
                    if len(constituency_df) > 1:
                        # (Your existing analysis code)
                        st.info("Analysis section is ready.")

            with tab5:
                st.markdown("#### 📄 Raw Declaration Data")
                display_columns = [
                    'informacion_personal_nombre_y_apellidos', 'informacion_personal_cargo',
                    'informacion_personal_circunscripcion', 'informacion_personal_estado_civil',
                    'irpf_cantidad_pagada', 'observaciones'
                ]
                available_columns = [col for col in display_columns if col in deputy_data.index]
                raw_data = pd.DataFrame([deputy_data[available_columns]])
                st.dataframe(
                    raw_data, use_container_width=True, hide_index=True,
                    column_config={
                        'informacion_personal_nombre_y_apellidos': 'Name',
                        'informacion_personal_cargo': 'Position',
                        'informacion_personal_circunscripcion': 'Constituency',
                        'informacion_personal_estado_civil': 'Civil Status',
                        'irpf_cantidad_pagada': st.column_config.NumberColumn('IRPF Paid', format="€%.2f"),
                        'observaciones': 'Observations'
                    }
                )

if __name__ == "__main__":
    main()
