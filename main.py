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

# Simplified CSS with better compatibility
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
    
    /* Typography */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-clip: text;
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
    
    h4 {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    
    .info-item {
        background: rgba(102, 126, 234, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        transition: transform 0.2s ease;
    }
    
    .info-item:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .info-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .info-value {
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 12px;
        transition: transform 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    }
    
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 30, 60, 0.3);
        border-radius: 10px;
        padding: 4px;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0 20px;
        background: transparent;
        border: none;
        border-radius: 6px;
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
        background: rgba(102, 126, 234, 0.2);
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Social Media Pills */
    .social-pills {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .social-pill {
        background: rgba(102, 126, 234, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.3);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        font-size: 1.5rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease;
    }
    
    .social-pill:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: scale(1.1);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    /* Input Fields */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: rgba(30, 30, 60, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Success, Warning, Error, Info messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        border-radius: 8px;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
    }
    
    /* Strong text */
    strong {
        color: #ffffff !important;
        font-weight: 600 !important;
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
        background: rgba(30, 30, 60, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.7);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .info-grid {
            grid-template-columns: 1fr;
        }
    }
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
        import base64
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
        import base64
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" style="width: 120px; height: 120px; object-fit: contain; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px;">'
    
    # Seat indicator
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        import base64
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" style="width: 120px; height: 120px; object-fit: contain; background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 10px;">'
    
    gallery_html += '</div></div>'
    return gallery_html

def main():
    st.markdown('<h1 style="text-align: center;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Search bar
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado por nombre...")
    
    # Filter data
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
    
    with col2:
        st.metric("Resultados", len(filtered_df))
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
    else:
        # Deputy selector
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "Seleccionar Diputado:",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        st.markdown("---")
        
        # Layout
        col_left, col_right = st.columns([1.5, 2])
        
        with col_left:
            # Image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info
            st.markdown("### 📋 Información Básica")
            
            info_html = '<div class="info-grid">'
            
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
                    <div class="info-label">📅 ELECCIÓN</div>
                    <div class="info-value">{fecha_eleccion}</div>
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
            properties_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
            
            # Financial summary
            st.markdown("### 💰 Resumen Financiero")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**💵 Ingresos**")
                st.markdown(f"# {format_currency(total_salary)}")
                st.markdown(f"IRPF: **{format_currency(irpf)}**")
                st.markdown(f"Tipo: **{tax_rate:.2f}%**")
            
            with col2:
                st.markdown("**🏠 Patrimonio**")
                st.markdown(f"# {properties_count + vehicles_count}")
                st.markdown(f"Inmuebles: **{properties_count}**")
                st.markdown(f"Vehículos: **{vehicles_count}**")
            
            with col3:
                st.markdown("**💳 Deudas**")
                st.markdown(f"# {format_currency(total_debt)}")
                if total_debt > 0:
                    st.markdown(f"Activas: **{len(debts)}**")
                else:
                    st.markdown("*Sin deudas*")
            
            st.markdown("---")
            
            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💵 Ingresos", "🏠 Patrimonio", "💳 Deudas", "📊 Análisis"])
            
            with tab1:
                st.markdown("#### 💵 Fuentes de Ingresos")
                
                if total_salary > 0:
                    st.success(f"💰 **Total Anual: {format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"📋 **IRPF: {format_currency_full(irpf)}** ({tax_rate:.2f}%)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Salarios")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                concepto = salary.get('concepto', f'Ingreso #{i+1}')
                                if str(concepto).lower() == 'nan':
                                    concepto = f'Ingreso #{i+1}'
                                
                                amount = extract_currency_value(salary.get('euros'))
                                if amount > 100000:
                                    st.error(f"💰 **{concepto}**")
                                elif amount > 50000:
                                    st.warning(f"💰 **{concepto}**")
                                else:
                                    st.info(f"💰 **{concepto}**")
                                
                                st.markdown(f"→ **{format_currency_full(amount)}**")
                    else:
                        st.info("Sin salarios declarados")
                
                with col2:
                    st.markdown("##### Rentas del Capital")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        for div in dividends:
                            if isinstance(div, dict):
                                concepto = div.get('concepto', 'Inversión')
                                if str(concepto).lower() == 'nan':
                                    concepto = 'Inversión'
                                st.markdown(f"**📊 {concepto}**")
                                rendimientos = extract_currency_value(div.get('euros'))
                                if rendimientos > 0:
                                    st.markdown(f"→ **{format_currency_full(rendimientos)}**")
                    else:
                        st.info("Sin rentas del capital")
            
            with tab2:
                st.markdown("#### 🏠 Patrimonio Declarado")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Inmuebles")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                st.markdown(f"**📍 Inmueble #{i+1}**")
                                
                                tipo = prop.get('clase_y_caracteristicas', '')
                                if tipo and str(tipo).lower() != 'nan':
                                    st.markdown(f"Tipo: {tipo}")
                                
                                ubicacion = prop.get('situacion', '')
                                if ubicacion and str(ubicacion).lower() != 'nan':
                                    st.markdown(f"Ubicación: {ubicacion}")
                                
                                fecha = prop.get('fecha_adquisicion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Adquirido: {fecha}")
                                
                                st.markdown("")
                    else:
                        st.info("Sin propiedades")
                    
                    st.markdown("##### Cuentas")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        for account in accounts:
                            if isinstance(account, dict):
                                desc = account.get('descripcion', 'Cuenta')
                                if str(desc).lower() == 'nan':
                                    desc = 'Cuenta'
                                saldo = extract_currency_value(account.get('saldo'))
                                if saldo > 0:
                                    st.markdown(f"**🏦 {desc}**")
                                    st.markdown(f"Saldo: **{format_currency_full(saldo)}**")
                    else:
                        st.info("Sin cuentas")
                
                with col2:
                    st.markdown("##### Vehículos")
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                desc = vehicle.get('descripcion', f'Vehículo #{i+1}')
                                if str(desc).lower() == 'nan':
                                    desc = f'Vehículo #{i+1}'
                                st.markdown(f"**🚗 {desc}**")
                                
                                fecha = vehicle.get('fecha_adquisicion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Adquirido: {fecha}")
                                st.markdown("")
                    else:
                        st.info("Sin vehículos")
            
            with tab3:
                st.markdown("#### 💸 Deudas y Obligaciones")
                if debts:
                    st.error(f"💰 **Total Pendiente: {format_currency_full(total_debt)}**")
                    
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            desc = debt.get('descripcion', f'Deuda #{i+1}')
                            if str(desc).lower() == 'nan':
                                desc = f'Deuda #{i+1}'
                            
                            st.markdown(f"**📄 {desc}**")
                            
                            original = extract_currency_value(debt.get('importe_concedido'))
                            pending = extract_currency_value(debt.get('saldo_pendiente'))
                            
                            if original > 0:
                                st.markdown(f"Original: **{format_currency_full(original)}**")
                            if pending > 0:
                                st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                            
                            fecha = debt.get('fecha_concesion', '')
                            if fecha and str(fecha).lower() != 'nan':
                                st.markdown(f"Fecha: {fecha}")
                            
                            if original > 0 and pending > 0:
                                paid_pct = ((original - pending) / original) * 100
                                if paid_pct > 50:
                                    st.success(f"✅ Pagado: {paid_pct:.1f}%")
                                else:
                                    st.warning(f"⏳ Pagado: {paid_pct:.1f}%")
                            
                            st.markdown("---")
                else:
                    st.success("✅ No se han declarado deudas")
            
            with tab4:
                st.markdown("#### 📊 Análisis Financiero")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    accounts_total = sum(extract_currency_value(a.get('saldo', 0)) 
                                       for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']) 
                                       if isinstance(a, dict))
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=['Propiedades', 'Vehículos', 'Cuentas'],
                        values=[
                            properties_count * 150000,
                            vehicles_count * 20000,
                            accounts_total
                        ],
                        hole=.3,
                        marker_colors=['#667eea', '#764ba2', '#f093fb']
                    )])
                    fig.update_layout(
                        title="Distribución Patrimonio (Estimado)",
                        showlegend=True,
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Tax gauge
                    fig2 = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=tax_rate,
                        number={'suffix': "%", 'valueformat': ".2f"},
                        title={'text': "Tipo Impositivo"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 50]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 15], 'color': "rgba(102, 126, 234, 0.1)"},
                                {'range': [15, 30], 'color': "rgba(102, 126, 234, 0.2)"},
                                {'range': [30, 50], 'color': "rgba(102, 126, 234, 0.3)"}
                            ]
                        }
                    ))
                    fig2.update_layout(
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
