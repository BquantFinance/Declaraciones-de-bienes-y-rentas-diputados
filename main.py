import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64

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

# Apply dark theme CSS - Simplified and guaranteed to work
def inject_css():
    css = """
    <style>
        /* Force dark background */
        .stApp {
            background-color: #0E1117;
            background-image: linear-gradient(180deg, #0E1117 0%, #262730 100%);
        }
        
        /* Style the main content area */
        .main {
            padding-top: 2rem;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #FAFAFA !important;
        }
        
        /* Metrics containers */
        [data-testid="metric-container"] {
            background-color: rgba(28, 131, 225, 0.1);
            border: 1px solid #1c83e1;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            background-color: #262730;
            color: #FAFAFA;
            border: 1px solid #4A4B5C;
        }
        
        /* Select boxes */
        .stSelectbox > div > div {
            background-color: #262730;
            color: #FAFAFA;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #1c83e1;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border-radius: 0.5rem;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: #2b91f0;
            transform: translateY(-2px);
        }
        
        /* Success/Error/Warning/Info boxes */
        .stSuccess {
            background-color: rgba(0, 255, 0, 0.1);
            color: #00FF00;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #00FF00;
        }
        
        .stError {
            background-color: rgba(255, 0, 0, 0.1);
            color: #FF4444;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #FF4444;
        }
        
        .stWarning {
            background-color: rgba(255, 193, 7, 0.1);
            color: #FFC107;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #FFC107;
        }
        
        .stInfo {
            background-color: rgba(0, 123, 255, 0.1);
            color: #007BFF;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #007BFF;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(28, 131, 225, 0.1);
            padding: 4px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #FAFAFA;
            padding: 8px 16px;
            background-color: transparent;
            border-radius: 6px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1c83e1;
        }
        
        /* Dividers */
        hr {
            border-color: #4A4B5C;
        }
        
        /* Custom classes */
        .deputy-card {
            background-color: rgba(28, 131, 225, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #1c83e1;
            margin-bottom: 1rem;
        }
        
        .info-label {
            color: #B0B3B8;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        
        .info-value {
            color: #FAFAFA;
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .highlight-box {
            background: linear-gradient(90deg, #1c83e1, #0066cc);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Make text more readable */
        p, li, span {
            color: #FAFAFA;
        }
        
        /* Style disclaimer */
        .disclaimer-box {
            background: rgba(255, 71, 87, 0.1);
            border: 2px solid #ff4757;
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
        }
        
        .disclaimer-title {
            color: #ff4757;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .disclaimer-text {
            color: #FAFAFA;
            line-height: 1.6;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

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
    """Format currency values"""
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

def show_disclaimer():
    """Show the legal disclaimer page"""
    inject_css()
    
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD</div>
        <div class="disclaimer-text">
            <p><strong>Esta aplicación recopila información pública del Congreso de los Diputados.</strong></p>
            <p>No está vinculada oficialmente al Congreso de los Diputados, ni cuenta con su aval, autorización o patrocinio.</p>
            <p>Los datos pueden contener errores, inexactitudes u omisiones.</p>
            <p>Para información oficial, visite directamente la página web del Congreso de los Diputados.</p>
            <p>El uso de esta aplicación es responsabilidad exclusiva del usuario.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ **ACEPTO Y ENTIENDO**", type="primary", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()

def display_deputy_photo(deputy_data):
    """Display deputy photo or placeholder"""
    photo_path = deputy_data.get('photo_path', '')
    
    try:
        if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
            st.image(photo_path, width=250, caption=deputy_data['informacion_personal_nombre_y_apellidos'])
        else:
            # Placeholder
            st.markdown("""
            <div style="background: #262730; border: 2px solid #1c83e1; border-radius: 10px; 
                        width: 250px; height: 300px; display: flex; align-items: center; 
                        justify-content: center; font-size: 72px; margin: 0 auto;">
                👤
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading photo: {str(e)}")

def main_app():
    """Main application"""
    inject_css()
    
    # Header with gradient effect
    st.markdown("""
    <div class="highlight-box">
        <h1 style="margin: 0; color: white;">⚖️ Registro de Diputados</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Verify required columns
    if 'informacion_personal_nombre_y_apellidos' not in df.columns:
        st.error("❌ El archivo CSV no tiene el formato esperado")
        st.stop()
    
    # Get unique deputies
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Search section with columns
    st.markdown("### 🔍 Búsqueda de Diputados")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        search_term = st.text_input(
            "Buscar diputado",
            placeholder="Escriba el nombre del diputado...",
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
        st.metric("Total", f"{len(filtered_deputies)}", label_visibility="visible")
    
    if len(filtered_deputies) == 0:
        st.warning("⚠️ No se encontraron diputados con ese criterio de búsqueda")
        return
    
    # Deputy selector
    st.markdown("### 👤 Seleccionar Diputado")
    
    selected_deputy_name = st.selectbox(
        "Diputado",
        filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist(),
        format_func=lambda x: f"📋 {x}",
        label_visibility="collapsed"
    )
    
    if not selected_deputy_name:
        return
    
    # Get all declarations for selected deputy
    deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
    
    # If multiple declarations, let user choose
    if len(deputy_declarations) > 1:
        st.info(f"📄 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
        
        declaration_options = []
        for idx, row in deputy_declarations.iterrows():
            fecha = row.get('informacion_personal_fecha_eleccion', '')
            label = f"Declaración {idx - deputy_declarations.index[0] + 1}"
            if fecha and str(fecha).lower() != 'nan':
                label += f" - {fecha}"
            declaration_options.append((idx, label))
        
        selected_idx = st.selectbox(
            "Seleccionar declaración",
            [opt[0] for opt in declaration_options],
            format_func=lambda x: next(opt[1] for opt in declaration_options if opt[0] == x),
            label_visibility="collapsed"
        )
        
        deputy_data = deputy_declarations.loc[selected_idx]
    else:
        deputy_data = deputy_declarations.iloc[0]
    
    st.divider()
    
    # Deputy information display
    st.markdown(f"## {deputy_data['informacion_personal_nombre_y_apellidos']}")
    
    # Layout with columns
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        # Photo
        display_deputy_photo(deputy_data)
        
        # Basic information card
        st.markdown("### 📋 Información Personal")
        
        with st.container():
            info_fields = [
                ('CARGO', deputy_data.get('informacion_personal_cargo', 'Diputado')),
                ('CIRCUNSCRIPCIÓN', deputy_data.get('informacion_personal_circunscripcion', 'N/A')),
                ('ESTADO CIVIL', deputy_data.get('informacion_personal_estado_civil', 'N/A')),
                ('FECHA ELECCIÓN', deputy_data.get('informacion_personal_fecha_eleccion', 'N/A')),
            ]
            
            for label, value in info_fields:
                if value and str(value).lower() not in ['nan', 'n/a']:
                    st.markdown(f"""
                    <div class="deputy-card">
                        <div class="info-label">{label}</div>
                        <div class="info-value">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Social media if available
        social_links = []
        if pd.notna(deputy_data.get('twitter')) and str(deputy_data.get('twitter')).lower() != 'nan':
            social_links.append(f"[𝕏 Twitter]({deputy_data.get('twitter')})")
        if pd.notna(deputy_data.get('facebook')) and str(deputy_data.get('facebook')).lower() != 'nan':
            social_links.append(f"[📘 Facebook]({deputy_data.get('facebook')})")
        if pd.notna(deputy_data.get('instagram')) and str(deputy_data.get('instagram')).lower() != 'nan':
            social_links.append(f"[📸 Instagram]({deputy_data.get('instagram')})")
        if pd.notna(deputy_data.get('website')) and str(deputy_data.get('website')).lower() != 'nan':
            social_links.append(f"[🌐 Web]({deputy_data.get('website')})")
        
        if social_links:
            st.markdown("### 🌐 Redes Sociales")
            st.markdown(" | ".join(social_links))
    
    with col_right:
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
        
        # Financial summary
        st.markdown("### 💰 Resumen Financiero")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 INGRESOS", format_currency(total_salary))
        
        with col2:
            st.metric("📊 IRPF", f"{tax_rate:.1f}%")
        
        with col3:
            st.metric("🏠 PROPIEDADES", total_properties)
        
        with col4:
            st.metric("💳 DEUDAS", format_currency(total_debt))
        
        st.divider()
        
        # Detailed information tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "💵 Ingresos",
            "🏠 Inmuebles", 
            "🚗 Vehículos",
            "💼 Sociedades",
            "💳 Deudas",
            "📊 Análisis"
        ])
        
        with tab1:
            st.markdown("#### 💰 Desglose de Ingresos")
            
            if total_salary > 0:
                st.success(f"**Total Anual:** {format_currency_full(total_salary)}")
                if irpf > 0:
                    st.info(f"**IRPF Pagado:** {format_currency_full(irpf)} ({tax_rate:.2f}%)")
            
            if salaries:
                for i, salary in enumerate(salaries[:10]):
                    if isinstance(salary, dict):
                        concepto = salary.get('concepto', f'Ingreso {i+1}')
                        amount = extract_currency_value(salary.get('euros'))
                        st.write(f"• **{concepto}:** {format_currency_full(amount)}")
            else:
                st.info("📭 No hay ingresos declarados")
        
        with tab2:
            st.markdown("#### 🏠 Bienes Inmuebles")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("🏢 Urbanos", urban_properties)
                urban = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos', '[]'))
                for i, prop in enumerate(urban[:5]):
                    if isinstance(prop, dict):
                        st.write(f"• Inmueble urbano #{i+1}")
            
            with col_b:
                st.metric("🌾 Rústicos", rustic_properties)
                rustic = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))
                for i, prop in enumerate(rustic[:5]):
                    if isinstance(prop, dict):
                        st.write(f"• Inmueble rústico #{i+1}")
            
            if urban_properties == 0 and rustic_properties == 0:
                st.info("📭 No hay inmuebles declarados")
        
        with tab3:
            st.markdown("#### 🚗 Vehículos")
            
            if vehicles:
                st.success(f"**Total vehículos:** {vehicles_count}")
                for i, vehicle in enumerate(vehicles[:10]):
                    if isinstance(vehicle, dict):
                        desc = vehicle.get('descripcion', f'Vehículo {i+1}')
                        fecha = vehicle.get('fecha_adquisicion', '')
                        if fecha and str(fecha).lower() != 'nan':
                            st.write(f"• **{desc}** (Adquirido: {fecha})")
                        else:
                            st.write(f"• **{desc}**")
            else:
                st.info("📭 No hay vehículos declarados")
        
        with tab4:
            st.markdown("#### 💼 Sociedades y Participaciones")
            
            sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', '[]'))
            if sociedades:
                st.success(f"**Sociedades no cotizadas:** {len(sociedades)}")
                for i, soc in enumerate(sociedades[:5]):
                    if isinstance(soc, dict):
                        st.write(f"• Sociedad #{i+1}")
            else:
                st.info("📭 No hay sociedades declaradas")
        
        with tab5:
            st.markdown("#### 💳 Deudas y Obligaciones")
            
            if debts:
                st.error(f"**Total pendiente:** {format_currency_full(total_debt)}")
                for i, debt in enumerate(debts[:5]):
                    if isinstance(debt, dict):
                        desc = debt.get('descripcion', f'Deuda {i+1}')
                        pending = extract_currency_value(debt.get('saldo_pendiente'))
                        st.write(f"• **{desc}:** {format_currency_full(pending)}")
            else:
                st.success("✅ No hay deudas declaradas")
        
        with tab6:
            st.markdown("#### 📊 Análisis Visual")
            
            if total_salary > 0 or total_properties > 0 or vehicles_count > 0:
                # Create donut chart
                fig = go.Figure(data=[go.Pie(
                    labels=['Ingresos', 'Propiedades (est.)', 'Vehículos (est.)'],
                    values=[
                        total_salary,
                        total_properties * 150000,
                        vehicles_count * 20000
                    ],
                    hole=.4,
                    marker_colors=['#1c83e1', '#28a745', '#ffc107']
                )])
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>%{value:,.0f}€<br>%{percent}<extra></extra>'
                )
                
                fig.update_layout(
                    title="Distribución Patrimonial Estimada",
                    showlegend=True,
                    height=400,
                    paper_bgcolor='#0E1117',
                    plot_bgcolor='#0E1117',
                    font=dict(color='#FAFAFA', size=14),
                    title_font_size=18
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Bar chart for income vs debt
                if total_salary > 0 or total_debt > 0:
                    fig2 = go.Figure(data=[
                        go.Bar(name='Ingresos', x=['Total'], y=[total_salary], marker_color='#28a745'),
                        go.Bar(name='Deudas', x=['Total'], y=[total_debt], marker_color='#dc3545')
                    ])
                    
                    fig2.update_layout(
                        title="Ingresos vs Deudas",
                        yaxis_title="Euros",
                        height=300,
                        paper_bgcolor='#0E1117',
                        plot_bgcolor='#0E1117',
                        font=dict(color='#FAFAFA'),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("📊 No hay suficientes datos para generar el análisis visual")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
