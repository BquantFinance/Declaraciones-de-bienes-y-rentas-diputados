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

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# --- THE NEW, SIMPLIFIED, AND ROBUST CSS FUNCTION ---
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* --- CORE APP STYLING --- */
        .stApp {
            background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* --- ROBUST WIDGET STYLING --- */
        /* This simplified approach uses semi-transparent backgrounds instead of a fragile blur filter. */

        /* Text Input & Select Box Styling */
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: rgba(42, 43, 74, 0.5) !important; /* A semi-transparent dark blue/purple */
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            transition: all 0.3s ease !important;
        }
        
        /* Hover & Focus Effects for Inputs */
        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border-color: rgba(102, 126, 234, 0.7) !important;
            background-color: rgba(42, 43, 74, 0.7) !important;
        }
        
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div[aria-expanded="true"] {
            border-color: rgba(102, 126, 234, 0.9) !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.4) !important;
        }

        /* Dropdown menu for Selectbox */
        div[data-baseweb="popover"] ul {
            background-color: #1a1a3e !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
        }
        div[data-baseweb="popover"] ul li:hover {
            background-color: rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: rgba(102, 126, 234, 0.15) !important;
            border: 1px solid rgba(102, 126, 234, 0.5) !important;
            color: white !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover {
            background-color: rgba(102, 126, 234, 0.25) !important;
            border-color: rgba(102, 126, 234, 0.8) !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            border: none !important;
        }

        /* Alert Styling */
        div[data-testid="stAlert"] {
            background-color: rgba(42, 43, 74, 0.3) !important;
            border-radius: 12px !important;
            border-left-width: 5px !important;
            border-top: none !important; border-right: none !important; border-bottom: none !important;
        }
        div[data-testid="stAlert"][data-baseweb="alert-success"] { border-left-color: #10b981 !important; }
        div[data-testid="stAlert"][data-baseweb="alert-warning"] { border-left-color: #f59e0b !important; }
        div[data-testid="stAlert"][data-baseweb="alert-error"] { border-left-color: #ef4444 !important; }
        div[data-testid="stAlert"][data-baseweb="alert-info"] { border-left-color: #3b82f6 !important; }

        /* --- SIMPLIFIED GENERAL STYLES --- */
        .main .block-container { padding-top: 1rem; max-width: 1600px; }
        h1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700 !important; font-size: 2.5rem !important; }
        h2 { color: #ffffff !important; font-weight: 600 !important; font-size: 1.8rem !important; }
        h3 { color: #e2e8f0 !important; font-weight: 500 !important; }
        
        /* Your Custom Classes */
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.2rem; margin: 1.5rem 0; }
        .info-item { background: rgba(42, 43, 74, 0.3); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); }
        .social-pills { display: flex; gap: 1rem; margin-top: 1rem; }
        .social-pill { background: rgba(102, 126, 234, 0.1); border: 1px solid rgba(102, 126, 234, 0.3); width: 50px; height: 50px; border-radius: 50%; font-size: 1.5rem; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: all 0.3s ease; }
        .social-pill:hover { background: rgba(102, 126, 234, 0.2); transform: scale(1.1); }
        
        /* Clean up default Streamlit elements */
        div[data-testid="metric-container"] { background-color: rgba(42, 43, 74, 0.3); border: 1px solid rgba(255, 255, 255, 0.1); padding: 1.2rem; border-radius: 16px; }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom: 2px solid rgba(255, 255, 255, 0.1); }
        div[data-testid="stTabs"] [aria-selected="true"] { border-bottom: 2px solid #667eea; }
        #MainMenu, footer, header { visibility: hidden; }
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

def show_disclaimer():
    """Show the legal disclaimer page"""
    apply_css()
    
    # Center the disclaimer
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="disclaimer-container">
            <h1 class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD</h1>
            <div class="disclaimer-text">
                <p>Esta aplicación recopila y organiza información pública disponible en la página web del Congreso de los Diputados, incluyendo documentos en formato PDF. La aplicación no pertenece ni está vinculada de ninguna manera al Congreso de los Diputados, ni cuenta con su aval, autorización o patrocinio.</p>
                
                <p>El contenido mostrado se ofrece únicamente con fines informativos y de acceso público. Aunque se procura garantizar la precisión y actualización de los datos, <strong>la aplicación puede contener errores, inexactitudes u omisiones, así como información incompleta o desactualizada</strong>. Para la consulta oficial, íntegra y auténtica de los documentos, se recomienda acudir directamente a la página web del Congreso de los Diputados.</p>
                
                <p>El uso de esta aplicación es responsabilidad exclusiva del usuario.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Accept button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()

def main_app():
    """Main application"""
    apply_css()
    
    st.markdown('<h1 style="text-align: center;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # Get unique deputies by name (they might have multiple declarations)
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Search bar
    col1, col2 = st.columns([4, 1])
    with col1:
        search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado por nombre...")
    
    # Filter unique deputies
    filtered_deputies = unique_deputies.copy()
    if search_term:
        filtered_deputies = filtered_deputies[filtered_deputies['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
    
    with col2:
        st.metric("Diputados", len(filtered_deputies))
    
    st.markdown("---")
    
    if len(filtered_deputies) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
    else:
        # Deputy selector
        deputy_names = filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy_name = st.selectbox(
            "Seleccionar Diputado:",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        # Get all declarations for selected deputy
        deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
        
        # Declaration selector (if multiple)
        if len(deputy_declarations) > 1:
            st.info(f"📋 Este diputado tiene **{len(deputy_declarations)} declaraciones** disponibles")
            
            # Create options for declarations
            declaration_options = []
            for idx, row in deputy_declarations.iterrows():
                fecha_eleccion = row.get('informacion_personal_fecha_eleccion', '')
                fecha_presentacion = row.get('informacion_personal_fecha_presentacion_credencial', '')
                
                # Create a clean label without showing the actual filename
                declaration_number = idx - deputy_declarations.index[0] + 1
                label = f"📄 Declaración {declaration_number}"
                
                if fecha_eleccion and str(fecha_eleccion).lower() != 'nan':
                    label += f" - Elección: {fecha_eleccion}"
                if fecha_presentacion and str(fecha_presentacion).lower() != 'nan':
                    label += f" - Presentación: {fecha_presentacion}"
                    
                declaration_options.append((idx, label))
            
            selected_idx = st.selectbox(
                "Seleccionar Declaración:",
                [opt[0] for opt in declaration_options],
                format_func=lambda x: next(opt[1] for opt in declaration_options if opt[0] == x)
            )
            
            deputy_data = deputy_declarations.loc[selected_idx]
        else:
            deputy_data = deputy_declarations.iloc[0]
        
        st.markdown("---")
        
        # Layout
        col_left, col_right = st.columns([1.5, 2])
        
        with col_left:
            # Image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info
            st.markdown("### 📋 Información Personal")
            
            info_html = '<div class="info-grid">'
            
            # Personal information fields
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
                    if not value and default:
                        value = default
                    info_html += f'''
                    <div class="info-item">
                        <div class="info-label">{label}</div>
                        <div class="info-value">{value}</div>
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
            
            # Observaciones if exists
            observaciones = deputy_data.get('observaciones', '')
            if observaciones and str(observaciones).lower() != 'nan':
                st.markdown("### 📝 Observaciones")
                st.info(observaciones)
        
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
            
            # Count all properties
            urban_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            rustic_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_rusticos']))
            total_properties = urban_properties + rustic_properties
            
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
                st.markdown(f"# {total_properties + vehicles_count}")
                st.markdown(f"Inmuebles: **{total_properties}**")
                st.markdown(f"Vehículos: **{vehicles_count}**")
            
            with col3:
                st.markdown("**💳 Deudas**")
                st.markdown(f"# {format_currency(total_debt)}")
                if total_debt > 0:
                    st.markdown(f"Activas: **{len(debts)}**")
                else:
                    st.markdown("*Sin deudas*")
            
            st.markdown("---")
            
            # Tabs with all information
            tabs = st.tabs([
                "💵 Ingresos", 
                "🏠 Inmuebles", 
                "💼 Sociedades",
                "💰 Activos",
                "🚗 Vehículos",
                "💳 Deudas",
                "📊 Análisis",
                "📄 Otros"
            ])
            
            # TAB 1: INGRESOS
            with tabs[0]:
                st.markdown("#### 💵 Todas las Fuentes de Ingresos")
                
                if total_salary > 0:
                    st.success(f"💰 **Total Anual: {format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"📋 **IRPF: {format_currency_full(irpf)}** ({tax_rate:.2f}%)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 💼 Salarios")
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
                    
                    st.markdown("##### 💸 Otras Rentas")
                    otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', ''))
                    if otras:
                        for item in otras:
                            if isinstance(item, dict):
                                concepto = item.get('concepto', 'Otra renta')
                                importe = extract_currency_value(item.get('euros', 0))
                                if importe > 0:
                                    st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                    else:
                        st.info("Sin otras rentas")
                
                with col2:
                    st.markdown("##### 📈 Dividendos y Participaciones")
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
                        st.info("Sin dividendos")
                    
                    st.markdown("##### 🏦 Intereses Financieros")
                    intereses = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', ''))
                    if intereses:
                        for item in intereses:
                            if isinstance(item, dict):
                                concepto = item.get('concepto', 'Interés')
                                importe = extract_currency_value(item.get('euros', 0))
                                if importe > 0:
                                    st.markdown(f"**{concepto}**: {format_currency_full(importe)}")
                    else:
                        st.info("Sin intereses financieros")
            
            # TAB 2: INMUEBLES
            with tabs[1]:
                st.markdown("#### 🏠 Bienes Inmuebles")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏢 Inmuebles Urbanos")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                st.markdown(f"**📍 Inmueble Urbano #{i+1}**")
                                
                                for key, value in prop.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                
                                st.markdown("")
                    else:
                        st.info("Sin inmuebles urbanos")
                
                with col2:
                    st.markdown("##### 🌾 Inmuebles Rústicos")
                    rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                    if rusticos:
                        for i, prop in enumerate(rusticos):
                            if isinstance(prop, dict):
                                st.markdown(f"**🚜 Inmueble Rústico #{i+1}**")
                                
                                for key, value in prop.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                
                                st.markdown("")
                    else:
                        st.info("Sin inmuebles rústicos")
            
            # TAB 3: SOCIEDADES
            with tabs[2]:
                st.markdown("#### 💼 Sociedades y Participaciones")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏢 Sociedades No Cotizadas")
                    sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                    if sociedades:
                        for i, soc in enumerate(sociedades):
                            if isinstance(soc, dict):
                                st.markdown(f"**🏭 Sociedad #{i+1}**")
                                for key, value in soc.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                st.markdown("")
                    else:
                        st.info("Sin sociedades no cotizadas")
                
                with col2:
                    st.markdown("##### 📊 Participaciones >5%")
                    participaciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                    if participaciones:
                        for i, part in enumerate(participaciones):
                            if isinstance(part, dict):
                                st.markdown(f"**📈 Participación #{i+1}**")
                                for key, value in part.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                                st.markdown("")
                    else:
                        st.info("Sin participaciones superiores al 5%")
            
            # TAB 4: ACTIVOS FINANCIEROS
            with tabs[3]:
                st.markdown("#### 💰 Activos Financieros")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 🏦 Cuentas y Depósitos")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts if isinstance(a, dict))
                        if total_accounts > 0:
                            st.success(f"💰 **Total: {format_currency_full(total_accounts)}**")
                        
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
                        st.info("Sin cuentas declaradas")
                    
                    st.markdown("##### 📈 Acciones y Participaciones")
                    acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                    if acciones:
                        for i, accion in enumerate(acciones):
                            if isinstance(accion, dict):
                                st.markdown(f"**📊 Acción/Participación #{i+1}**")
                                for key, value in accion.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.info("Sin acciones declaradas")
                
                with col2:
                    st.markdown("##### 📜 Deuda Pública y Valores")
                    deuda_publica = parse_json_field(deputy_data.get('otros_bienes_y_derechos_deuda_publica_y_valores', ''))
                    if deuda_publica:
                        for i, item in enumerate(deuda_publica):
                            if isinstance(item, dict):
                                st.markdown(f"**💼 Valor #{i+1}**")
                                for key, value in item.items():
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.info("Sin deuda pública o valores")
            
            # TAB 5: VEHÍCULOS
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
                                if str(desc).lower() == 'nan':
                                    desc = f'Vehículo #{i+1}'
                                st.markdown(f"**🚗 {desc}**")
                                
                                fecha = vehicle.get('fecha_adquisicion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Adquirido: {fecha}")
                                st.markdown("")
                else:
                    st.info("Sin vehículos declarados")
            
            # TAB 6: DEUDAS
            with tabs[5]:
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
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if original > 0:
                                    st.markdown(f"Original: **{format_currency_full(original)}**")
                                fecha = debt.get('fecha_concesion', '')
                                if fecha and str(fecha).lower() != 'nan':
                                    st.markdown(f"Fecha: {fecha}")
                            
                            with col2:
                                if pending > 0:
                                    st.markdown(f"Pendiente: **{format_currency_full(pending)}**")
                                if original > 0 and pending > 0:
                                    paid_pct = ((original - pending) / original) * 100
                                    if paid_pct > 50:
                                        st.success(f"✅ Pagado: {paid_pct:.1f}%")
                                    else:
                                        st.warning(f"⏳ Pagado: {paid_pct:.1f}%")
                            
                            st.markdown("---")
                else:
                    st.success("✅ No se han declarado deudas")
            
            # TAB 7: ANÁLISIS
            with tabs[6]:
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
                            total_properties * 150000,
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
            
            # TAB 8: OTROS
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
                                    if value and str(value).lower() != 'nan':
                                        key_formatted = key.replace('_', ' ').title()
                                        st.markdown(f"• {key_formatted}: {value}")
                    else:
                        st.write(otros_bienes)
                else:
                    st.info("No hay otros bienes declarados")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
