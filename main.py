import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE ---
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# --- 3. STYLESHEET (CSS) ---
def apply_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --text-color: #e2e8f0;
        --text-color-muted: #a0aec0;
        --bg-color-dark: #0f0f23;
        --bg-color-light: #1a1a3e;
        --card-bg-color: #1a1f2e;
        --border-color: #3a415a;
        --accent-color: #ed64a6;
        --success-color: #48bb78;
        --danger-color: #f56565;
        --border-radius: 16px;
    }

    .stApp {
        background: linear-gradient(180deg, var(--bg-color-dark) 0%, var(--bg-color-light) 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu, footer, header { visibility: hidden; }

    .main > div { padding-top: 2rem; }

    h1, h2, h3, h4, h5, h6 { color: var(--text-color); }
    p, div, span, label { color: var(--text-color-muted); }
    strong { color: var(--text-color); }

    .main-header {
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem; color: var(--text-color-muted);
        text-align: center; margin-bottom: 2.5rem;
    }
    
    .disclaimer-container {
        background: rgba(26, 31, 46, 0.7);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: var(--border-radius);
        padding: 2rem 3rem; margin: 3rem auto; max-width: 800px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        animation: fadeInSlideUp 0.6s ease-out forwards;
    }
    .disclaimer-title {
        font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 1.5rem;
        background: linear-gradient(135deg, var(--danger-color) 0%, var(--accent-color) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .disclaimer-text { font-size: 1.1rem; color: #cbd5e1; line-height: 1.7; text-align: justify; }

    div[data-testid="metric-container"] {
        background-color: var(--card-bg-color);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
    }

    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border: none; color: var(--text-color-muted); padding: 10px; border-radius: 8px; }
    .stTabs [aria-selected="true"] { color: white; background-color: rgba(102, 126, 234, 0.15); border-bottom: 3px solid var(--accent-color); }
    
    .content-card {
        background-color: var(--card-bg-color);
        border: 1px solid var(--border-color); border-radius: 12px;
        padding: 1.2rem 1.5rem; margin-bottom: 1rem;
        height: 100%; /* For consistent card height in columns */
    }
    .content-card .card-title { font-size: 1.1rem; font-weight: 600; color: var(--text-color); margin-bottom: 0.8rem; }
    .content-card .card-detail { margin: 0.3rem 0; color: var(--text-color-muted); font-size: 0.95rem; }

    .stTextInput > div > input, .stSelectbox > div > div {
        border-radius: 10px !important; border: 1px solid var(--border-color) !important;
        background-color: transparent !important;
    }
    .stButton > button { border-radius: 12px !important; border: 1px solid var(--border-color) !important; }
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--success-color) 0%, #38a169 100%);
        border: none !important; font-size: 1.1rem; font-weight: 600;
    }
    
    div[data-testid="metric-container"], .content-card, .stSelectbox > div > div, .stTextInput > div > input, .stButton > button, .stTabs [data-baseweb="tab"] {
        transition: all 0.25s ease-in-out;
    }

    div[data-testid="metric-container"]:hover, .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        border-color: var(--primary-color);
    }

    .stTextInput > div > input:hover, .stSelectbox > div > div:hover { border-color: var(--primary-color) !important; }
    .stTextInput > div > input:focus, .stSelectbox > div > div[aria-expanded="true"] {
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 15px rgba(118, 75, 162, 0.5) !important;
    }
    
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover {
        background-color: rgba(102, 126, 234, 0.1);
        color: white;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        border-color: var(--primary-color) !important;
        background-color: rgba(102, 126, 234, 0.1);
    }
    .stButton > button:active { transform: translateY(-1px); }
    .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 0 20px rgba(72, 187, 120, 0.5);
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
    }

    @keyframes fadeInSlideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    
    div[data-testid="column"] { animation: fadeInSlideUp 0.6s ease-out forwards; }
    div[data-testid="column"]:nth-of-type(1) { animation-delay: 0.1s; }
    div[data-testid="column"]:nth-of-type(2) { animation-delay: 0.2s; }

    @media (max-width: 992px) { div[data-testid="column"] { flex-direction: column !important; } .main-header { font-size: 2.2rem; } }
    @media (max-width: 768px) { .disclaimer-container { padding: 1.5rem; margin: 1rem; } .disclaimer-title { font-size: 2rem; } .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA HANDLING FUNCTIONS ---
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
        st.error("⚠️ No se encontró el archivo 'deputies_full_dataset.csv'. Por favor, asegúrese de que el archivo esté en el mismo directorio que la aplicación.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

def parse_json_field(field_value):
    if pd.isna(field_value) or field_value in ('[]', ''): return []
    try:
        return json.loads(re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value)))
    except: return []

def format_currency(value):
    if not isinstance(value, (int, float)): return "0€"
    return f"{int(value):,}".replace(",", ".") + "€" if value == int(value) else f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "€"

def format_currency_full(value):
    if not isinstance(value, (int, float)): return "0,00 €"
    return f"{int(value):,}".replace(",", ".") + " €" if value == int(value) else f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

def extract_currency_value(value_str):
    if pd.isna(value_str) or value_str == '': return 0
    if isinstance(value_str, (int, float)): return float(value_str)
    numeric_part = re.search(r'[\d.,]+', str(value_str))
    if numeric_part:
        try: return float(numeric_part.group(0).replace('.', '').replace(',', '.'))
        except (ValueError, TypeError): return 0
    return 0

# --- 5. UI COMPONENT FUNCTIONS ---
def create_image_gallery(deputy_data):
    gallery_html = '<div style="display: flex; gap: 1.5rem; align-items: center; justify-content: center; margin-bottom: 2rem;">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and os.path.exists(str(photo_path)):
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" style="width: 200px; height: 250px; object-fit: cover; border-radius: 12px; border: 2px solid rgba(102, 126, 234, 0.3);">'
    else:
        gallery_html += '<div style="width: 200px; height: 250px; background: rgba(102, 126, 234, 0.1); display: flex; align-items: center; justify-content: center; color: #94a3b8; border-radius: 12px; border: 2px solid rgba(102, 126, 234, 0.3);">👤<br>Sin Foto</div>'
    gallery_html += '</div>'
    return gallery_html

def show_disclaimer():
    apply_css()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""<div class="disclaimer-container"><h1 class="disclaimer-title">⚖️ Aviso Importante</h1><div class="disclaimer-text"><p>Esta es una herramienta <strong>no oficial</strong> que visualiza datos públicos del Congreso de los Diputados. Su propósito es puramente informativo.</p><p>La información puede contener errores, omisiones o no estar actualizada. Para consultas oficiales, por favor, diríjase siempre a la web del Congreso.</p><p>Al continuar, usted acepta que el uso de esta aplicación es bajo su única y exclusiva responsabilidad.</p></div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        b_col1, b_col2, b_col3 = st.columns([2, 3, 2])
        with b_col2:
            if st.button("✅ Acepto y Entiendo", type="primary", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()

# --- 6. MAIN APPLICATION LOGIC ---
def main_app():
    apply_css()
    
    st.markdown('<h1 class="main-header">Registro de Bienes y Rentas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Congreso de los Diputados · Portal de Transparencia</p>', unsafe_allow_html=True)
    
    df = load_data()
    if df.empty: st.stop()

    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    search_term = st.text_input("🔍 Buscar Diputado por nombre...", placeholder="Escriba un nombre para filtrar la lista...")
    
    filtered_deputies = unique_deputies[unique_deputies['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)] if search_term else unique_deputies
    
    if len(filtered_deputies) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda.")
    else:
        deputy_names = sorted(filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist())
        selected_deputy_name = st.selectbox("Seleccione un Diputado de la lista:", deputy_names)
        
        deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
        deputy_data = deputy_declarations.iloc[0]
        if len(deputy_declarations) > 1:
            options = {idx: f"Declaración del {row.get('informacion_personal_fecha_presentacion_credencial', 'N/A')}" for idx, row in deputy_declarations.iterrows()}
            selected_idx = st.selectbox("Este diputado tiene varias declaraciones:", options.keys(), format_func=lambda x: options[x])
            deputy_data = deputy_declarations.loc[selected_idx]
        
        st.markdown("<hr style='border-color: #3a415a; margin: 2rem 0;'>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns([1.5, 2])
        
        with col_left:
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
        
        with col_right:
            st.markdown(f"## 👤 {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales']))
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            total_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])) + len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_rusticos']))
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in parse_json_field(deputy_data['deudas_y_obligaciones']))

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1: st.metric("Ingresos Anuales", format_currency(total_salary), f"{tax_rate:.1f}% IRPF")
            with m_col2: st.metric("Activos Declarados", f"{total_properties + vehicles_count}", f"{total_properties} Inmuebles")
            with m_col3: st.metric("Deuda Pendiente", format_currency(total_debt), f"{len(parse_json_field(deputy_data['deudas_y_obligaciones']))} Préstamos")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            tab_names = ["💵 Ingresos", "🏠 Inmuebles", "💼 Sociedades", "💰 Activos", "🚗 Vehículos", "💳 Deudas", "📊 Análisis", "📄 Otros"]
            tabs = st.tabs(tab_names)

            with tabs[0]:
                st.subheader("Fuentes de Ingresos")
                in_col1, in_col2 = st.columns(2)
                with in_col1:
                    st.markdown("#### Salarios")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for salary in salaries:
                            st.markdown(f"<div class='content-card'><p class='card-detail'><strong>Concepto:</strong> {salary.get('concepto', 'N/A')}</p><p class='card-detail'><strong>Importe:</strong> {format_currency_full(extract_currency_value(salary.get('euros')))}</p></div>", unsafe_allow_html=True)
                    else: st.info("No hay salarios declarados.")
                with in_col2:
                    st.markdown("#### Dividendos y Otros")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        for div in dividends:
                            st.markdown(f"<div class='content-card'><p class='card-detail'><strong>Concepto:</strong> {div.get('concepto', 'N/A')}</p><p class='card-detail'><strong>Rendimiento:</strong> {format_currency_full(extract_currency_value(div.get('euros')))}</p></div>", unsafe_allow_html=True)
                    else: st.info("No hay dividendos declarados.")

            with tabs[1]:
                st.subheader("Bienes Inmuebles Declarados")
                im_col1, im_col2 = st.columns(2)
                with im_col1:
                    st.markdown("#### 🏢 Urbanos")
                    urban_props = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban_props:
                        for i, prop in enumerate(urban_props):
                            details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in prop.items() if pd.notna(v)])
                            st.markdown(f'<div class="content-card"><p class="card-title">Inmueble Urbano #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                    else: st.info("No hay inmuebles urbanos declarados.")
                with im_col2:
                    st.markdown("#### 🌾 Rústicos")
                    rustic_props = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                    if rustic_props:
                        for i, prop in enumerate(rustic_props):
                            details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in prop.items() if pd.notna(v)])
                            st.markdown(f'<div class="content-card"><p class="card-title">Inmueble Rústico #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                    else: st.info("No hay inmuebles rústicos declarados.")

            with tabs[2]:
                st.subheader("Sociedades y Participaciones")
                so_col1, so_col2 = st.columns(2)
                with so_col1:
                    st.markdown("#### Sociedades no Cotizadas")
                    societies = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                    if societies:
                        for i, soc in enumerate(societies):
                            details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in soc.items() if pd.notna(v)])
                            st.markdown(f'<div class="content-card"><p class="card-title">Sociedad #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                    else: st.info("No hay sociedades no cotizadas declaradas.")
                with so_col2:
                    st.markdown("#### Participaciones > 5%")
                    participations = parse_json_field(deputy_data.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', ''))
                    if participations:
                        for i, part in enumerate(participations):
                            details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in part.items() if pd.notna(v)])
                            st.markdown(f'<div class="content-card"><p class="card-title">Participación #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                    else: st.info("No hay participaciones superiores al 5% declaradas.")

            with tabs[3]:
                st.subheader("Activos Financieros")
                ac_col1, ac_col2 = st.columns(2)
                with ac_col1:
                    st.markdown("#### Cuentas y Depósitos")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        total_accounts = sum(extract_currency_value(a.get('saldo', 0)) for a in accounts)
                        st.success(f"**Saldo Total en Cuentas: {format_currency_full(total_accounts)}**")
                        for acc in accounts:
                            st.markdown(f"<div class='content-card'><p class='card-title'>🏦 {acc.get('descripcion', 'Cuenta')}</p><p class='card-detail'><strong>Saldo:</strong> {format_currency_full(extract_currency_value(acc.get('saldo')))}</p></div>", unsafe_allow_html=True)
                    else: st.info("No hay cuentas declaradas.")
                with ac_col2:
                    st.markdown("#### Otros Activos (Acciones, Deuda, etc.)")
                    other_assets = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones', ''))
                    if other_assets:
                         for i, asset in enumerate(other_assets):
                            details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in asset.items() if pd.notna(v)])
                            st.markdown(f'<div class="content-card"><p class="card-title">Activo #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                    else: st.info("No hay otros activos financieros declarados.")
            
            with tabs[4]:
                st.subheader("Vehículos Declarados")
                vehicles = parse_json_field(deputy_data['vehiculos'])
                if vehicles:
                    v_cols = st.columns(min(len(vehicles), 3))
                    for i, vehicle in enumerate(vehicles):
                        with v_cols[i % 3]:
                            desc = vehicle.get('descripcion', f'Vehículo #{i+1}')
                            fecha = vehicle.get('fecha_adquisicion', 'N/A')
                            st.markdown(f'<div class="content-card"><p class="card-title">🚗 {desc}</p><p class="card-detail"><strong>Adquirido:</strong> {fecha}</p></div>', unsafe_allow_html=True)
                else: st.info("No hay vehículos declarados.")
            
            with tabs[5]:
                st.subheader("Deudas y Obligaciones")
                debts_list = parse_json_field(deputy_data['deudas_y_obligaciones'])
                if debts_list:
                    for debt in debts_list:
                        desc = debt.get('descripcion', 'Deuda')
                        original = extract_currency_value(debt.get('importe_concedido'))
                        pending = extract_currency_value(debt.get('saldo_pendiente'))
                        paid_pct = max(0, ((original - pending) / original) * 100) if original > 0 else 0
                        st.markdown(f'<div class="content-card"><p class="card-title">📄 {desc}</p>'
                                    f'<p class="card-detail"><strong>Importe Original:</strong> {format_currency_full(original)}</p>'
                                    f'<p class="card-detail"><strong>Saldo Pendiente:</strong> {format_currency_full(pending)}</p></div>', unsafe_allow_html=True)
                        st.progress(int(paid_pct), text=f"Amortizado al {paid_pct:.1f}%")
                else: st.success("✅ No se han declarado deudas.")

            with tabs[6]:
                st.subheader("Análisis Financiero (Estimado)")
                an_col1, an_col2 = st.columns(2)
                with an_col1:
                    accounts_total = sum(extract_currency_value(a.get('saldo', 0)) for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']))
                    patrimony_data = {'Activo': ['Depósitos', 'Inmuebles (est.)', 'Vehículos (est.)'], 'Valor': [accounts_total, total_properties * 150000, vehicles_count * 15000]}
                    df_patrimony = pd.DataFrame(patrimony_data).query('Valor > 0')
                    if not df_patrimony.empty:
                        fig = px.pie(df_patrimony, values='Valor', names='Activo', title='Distribución de Patrimonio', hole=.4, color_discrete_sequence=px.colors.sequential.Purples_r)
                        fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                        st.plotly_chart(fig, use_container_width=True)
                with an_col2:
                    fig2 = go.Figure(go.Indicator(mode="gauge+number", value=tax_rate, number={'suffix': "%", 'valueformat': ".2f"}, title={'text': "Tipo Impositivo Efectivo (IRPF)"}, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [None, 50]}, 'bar': {'color': "#667eea"}}))
                    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=400)
                    st.plotly_chart(fig2, use_container_width=True)

            with tabs[7]:
                st.subheader("Otros Bienes y Derechos")
                other_goods = parse_json_field(deputy_data.get('otros_bienes_no_declarados_anteriormente', ''))
                if other_goods:
                    for i, good in enumerate(other_goods):
                        details = "".join([f'<p class="card-detail"><strong>{k.replace("_", " ").title()}:</strong> {v}</p>' for k,v in good.items() if pd.notna(v)])
                        st.markdown(f'<div class="content-card"><p class="card-title">Otro Bien #{i+1}</p>{details}</div>', unsafe_allow_html=True)
                else: st.info("No se han declarado otros bienes o derechos.")

# --- 7. SCRIPT EXECUTION ---
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
