import streamlit as st
import pandas as pd
import json
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Congreso de los Diputados - Análisis Patrimonial",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ASTONISHINGLY BEAUTIFUL CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* --- General Theme & Body --- */
    body {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background-color: #0d1117;
        background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0);
        background-size: 25px 25px;
    }

    /* --- Main Header --- */
    .deputy-header {
        background: rgba(30, 36, 53, 0.5);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    .deputy-name {
        font-size: 2.8em;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        text-shadow: 0 0 15px rgba(102, 126, 234, 0.6);
    }
    .deputy-title {
        font-size: 1.2em;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 10px;
        font-weight: 300;
    }

    /* --- Section Headers --- */
    .section-header {
        font-size: 1.6em;
        font-weight: 600;
        color: #a9b7ff;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid;
        border-image-slice: 1;
        border-image-source: linear-gradient(to right, #667eea, rgba(118, 75, 162, 0.5));
    }

    /* --- Information Cards & Items --- */
    .info-card {
        background: rgba(30, 36, 53, 0.6);
        border-radius: 16px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.5);
    }
    .info-item {
        margin: 10px 0;
        padding: 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .info-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .info-value {
        color: #e0e0e0;
        font-size: 1.1em;
        font-weight: 400;
        word-wrap: break-word;
    }

    /* --- Social Media & Misc --- */
    .social-button {
        display: inline-block; padding: 8px 16px; margin: 5px; border-radius: 20px;
        text-decoration: none !important; color: white !important; font-weight: 500;
        transition: all 0.3s ease; border: 1px solid transparent;
    }
    .social-facebook { background: #3b5998; }
    .social-twitter { background: #1DA1F2; }
    .social-instagram { background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); }
    .social-website { background: #6a737d; }
    .social-button:hover {
        transform: scale(1.1); box-shadow: 0 4px 15px rgba(0,0,0,0.2); filter: brightness(1.2);
    }
    .no-data {
        color: rgba(255, 255, 255, 0.4); font-style: italic; padding: 20px;
        background: rgba(255, 255, 255, 0.02); border-radius: 8px; text-align: center;
        border: 1px dashed rgba(255, 255, 255, 0.1);
    }
    
    /* --- Sidebar & Metrics --- */
    .css-1d391kg {
        background: #0d1117; border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="metric-container"] {
        background: rgba(30, 36, 53, 0.6); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricValue"] { color: #667eea; font-size: 2.2em !important; }
    [data-testid="stMetricLabel"] { color: rgba(255, 255, 255, 0.6) !important; }

    /* --- Tabs --- */
    button[data-baseweb="tab"] {
        background-color: transparent; color: rgba(255, 255, 255, 0.6);
        transition: all 0.3s ease; font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(102, 126, 234, 0.1); color: #FFFFFF;
        border-bottom: 3px solid #667eea; border-radius: 8px 8px 0 0;
    }

    /* --- Scrollbar --- */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #2c334b; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #667eea; }

</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def parse_json_field(field_value):
    """Safely parse JSON string fields, returning an empty list on failure."""
    if pd.isna(field_value) or field_value in ["", "[]"]:
        return []
    try:
        # The data is sometimes a list of dicts, sometimes just a dict. Standardize to list.
        data = json.loads(field_value)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, TypeError):
        return []

def parse_currency_value(value):
    """Convert varied currency string formats to a float."""
    if value is None or pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s_value = str(value).strip().replace('€', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(s_value)
    except (ValueError, TypeError):
        return 0.0

def format_currency(value):
    """Format a number as currency."""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "No declarado"
    return f"{value:,.2f} €"

def display_social_media(row):
    """Display social media links as styled buttons."""
    links = {
        "facebook": (row.get('facebook'), "social-facebook", "📘 Facebook"),
        "twitter": (row.get('twitter'), "social-twitter", "🐦 Twitter"),
        "instagram": (row.get('instagram'), "social-instagram", "📷 Instagram"),
        "website": (row.get('website'), "social-website", "🌐 Website")
    }
    social_html = "".join([
        f'<a href="{url}" target="_blank" class="social-button {css_class}">{text}</a>'
        for url, css_class, text in links.values() if pd.notna(url) and url
    ])
    if social_html:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">{social_html}</div>', unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    df = pd.read_csv('deputies_full_dataset.csv')
    # Keep only the latest declaration for each deputy_id
    df['declaration_date'] = pd.to_datetime(df['source_file'].str.extract(r'(\d{8})\.json$'), errors='coerce')
    df = df.sort_values('declaration_date', ascending=False).drop_duplicates('deputy_id', keep='first')
    df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].fillna("Nombre no disponible")
    return df.sort_values('informacion_personal_nombre_y_apellidos')

# --- MAIN APP ---
def main():
    df = load_data()

    # --- SIDEBAR ---
    st.sidebar.markdown("# 🏛️ **Panel de Diputados**")
    st.sidebar.markdown("---")

    search = st.sidebar.text_input("🔍 **Buscar por nombre**", "")
    constituencies = ["Todas"] + sorted(df['informacion_personal_circunscripcion'].dropna().unique().tolist())
    selected_constituency = st.sidebar.selectbox("📍 **Filtrar por circunscripción**", constituencies)

    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search, case=False, na=False)]
    if selected_constituency != "Todas":
        filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_constituency]

    if filtered_df.empty:
        st.error("No se encontraron diputados con los criterios seleccionados.")
        return

    selected_deputy = st.sidebar.selectbox(
        "👤 **Seleccionar Diputado/a**",
        filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 **Estadísticas Generales**")
    st.sidebar.metric("Total de Diputados en el Dataset", len(df['deputy_id'].unique()))
    st.sidebar.metric("Resultados de la Búsqueda", len(filtered_df))

    # --- DEPUTY DATA ---
    deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]

    # --- HEADER & SUMMARY ---
    st.markdown(f"""
        <div class="deputy-header">
            <p class="deputy-name">{deputy_data['informacion_personal_nombre_y_apellidos']}</p>
            <p class="deputy-title">{deputy_data.get('informacion_personal_cargo', 'Cargo no especificado')} - {deputy_data.get('informacion_personal_circunscripcion', 'N/A')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    display_social_media(deputy_data)

    # Calculate summary metrics
    total_rentas = sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales', [])))
    otras_rentas = (
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones', []))) +
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', []))) +
        sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', [])))
    )
    total_deudas = sum(parse_currency_value(d.get('saldo_pendiente')) for d in parse_json_field(deputy_data.get('deudas_y_obligaciones', [])))
    irpf_pagado = parse_currency_value(deputy_data.get('irpf_cantidad_pagada'))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Salariales", format_currency(total_rentas))
    col2.metric("Otras Rentas", format_currency(otras_rentas))
    col3.metric("Deuda Pendiente", format_currency(total_deudas))
    col4.metric("IRPF Pagado", format_currency(irpf_pagado))

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 **Personal**", "💰 **Rentas**", "🏠 **Patrimonio**", "💳 **Activos Financieros**", "📝 **Deudas y Otros**"])

    with tab1:
        st.markdown('<div class="section-header">Información Personal</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1.container(border=False):
            st.markdown(f"""
            <div class="info-card">
                <div class="info-item"><div class="info-label">Estado Civil</div><div class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</div></div>
                <div class="info-item"><div class="info-label">Fecha de Elección</div><div class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</div></div>
            </div>
            """, unsafe_allow_html=True)
        with col2.container(border=False):
            st.markdown(f"""
            <div class="info-card">
                <div class="info-item"><div class="info-label">Régimen Económico</div><div class="info-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial') or 'No aplica'}</div></div>
                <div class="info-item"><div class="info-label">Presentación de Credencial</div><div class="info-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</div></div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-header">Rentas Percibidas (Declaración 2022)</div>', unsafe_allow_html=True)
        rentas_data = {
            "💼 Percepciones Salariales": parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales')),
            "📈 Dividendos y Participaciones": parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones')),
            "🏦 Intereses Financieros": parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros')),
            "📑 Otras Rentas": parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas')),
        }
        for title, data in rentas_data.items():
            if data:
                with st.expander(title, expanded=True):
                    for item in data:
                        concepto = item.get('concepto') or "No especificado"
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"- **{concepto}**: {euros}")

    with tab3:
        st.markdown('<div class="section-header">Bienes Patrimoniales</div>', unsafe_allow_html=True)
        
        bienes_data = {
            "🏢 Inmuebles Urbanos": parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos')),
            "🌳 Inmuebles Rústicos": parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos')),
            "🚗 Vehículos": parse_json_field(deputy_data.get('vehiculos')),
        }

        for title, data in bienes_data.items():
            if data:
                with st.expander(title, expanded=True):
                    for item in data:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        details = [f"**{k.replace('_', ' ').capitalize()}:** {v}" for k, v in item.items() if v]
                        st.markdown(" • ".join(details))
                        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-header">Cuentas y Activos Financieros</div>', unsafe_allow_html=True)

        with st.expander("🏦 Cuentas y Depósitos", expanded=True):
            cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
            if cuentas:
                for item in cuentas:
                    desc = item.get('descripcion') or item.get('tipo') or "Cuenta"
                    saldo = format_currency(parse_currency_value(item.get('saldo')))
                    st.markdown(f"- **{desc}**: {saldo}")
            else:
                st.markdown('<p class="no-data">No declarado</p>', unsafe_allow_html=True)

        with st.expander("📈 Acciones y Participaciones", expanded=True):
            acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones'))
            if acciones:
                 for item in acciones:
                    desc = item.get('descripcion', 'N/A')
                    valor = format_currency(parse_currency_value(item.get('valor')))
                    st.markdown(f"- **{desc}**: {valor}")
            else:
                st.markdown('<p class="no-data">No declarado</p>', unsafe_allow_html=True)
        
        with st.expander("🏢 Sociedades no cotizadas", expanded=True):
            sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas'))
            if sociedades:
                for item in sociedades:
                    st.markdown(f"- **Descripción:** {item.get('clase_y_caracteristicas', 'N/A')}, **Situación:** {item.get('situacion', 'N/A')}")
            else:
                st.markdown('<p class="no-data">No declarado</p>', unsafe_allow_html=True)


    with tab5:
        st.markdown('<div class="section-header">Deudas y Obligaciones</div>', unsafe_allow_html=True)
        deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
        if deudas:
            for deuda in deudas:
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                desc = deuda.get('descripcion') or deuda.get('prestamo') or "Deuda"
                st.markdown(f"**{desc}**")
                cols = st.columns(3)
                cols[0].metric("Fecha Concesión", str(deuda.get('fecha_concesion', 'N/A')))
                cols[1].metric("Importe Concedido", format_currency(parse_currency_value(deuda.get('importe_concedido'))))
                cols[2].metric("Saldo Pendiente", format_currency(parse_currency_value(deuda.get('saldo_pendiente'))))
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No hay deudas declaradas</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Otros Bienes, Rentas y Derechos</div>', unsafe_allow_html=True)
        otros = parse_json_field(deputy_data.get('otros_bienes_no_declarados_anteriormente'))
        if otros:
            for item in otros:
                desc = item.get('descripcion', 'N/A')
                valor = format_currency(parse_currency_value(item.get('valor')))
                st.markdown(f"- **{desc}**: {valor}")
        else:
            st.markdown('<p class="no-data">No declarado</p>', unsafe_allow_html=True)

        if pd.notna(deputy_data.get('observaciones')) and deputy_data.get('observaciones'):
            st.markdown('<div class="section-header">Observaciones</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card info-value">{deputy_data["observaciones"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
