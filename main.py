import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import glob

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Dark mode base */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 40px;
        border-radius: 30px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    
    .hero-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 25px;
    }
    
    /* Data tables */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px;
    }
    
    /* Section headers */
    h1, h2, h3, h4 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Inputs */
    .stSelectbox > div > div, .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False

# Helper functions
def parse_money_value(value):
    if value is None or value == '': return 0
    if isinstance(value, (int, float)): return float(value)
    value_str = str(value).replace('€', '').replace('.', '').replace(',', '.').strip()
    try: return float(value_str)
    except: return 0

def get_hemiciclo_seat(deputy_index):
    files = glob.glob(f"hemiciclo/hemi_{deputy_index:04d}_*.gif")
    return files[0] if files else None

# Load data
@st.cache_data
def load_json_data():
    try:
        with open('all_deputies_merged.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        processed_data = []
        for idx, entry in enumerate(json_data, 1):
            if 'data' in entry and entry['data']:
                data = entry['data']
                personal_info = data.get('informacion_personal', {})
                rentas = data.get('rentas_percibidas', {})
                
                total_income = sum(parse_money_value(item.get('euros', 0)) for category in rentas.values() if isinstance(category, list) for item in category)
                liquid_assets = sum(parse_money_value(acc.get('saldo', 0)) for acc in data.get('depositos_y_cuentas', {}).get('cuentas', []))
                total_debt = sum(parse_money_value(debt.get('saldo_pendiente', 0)) for debt in data.get('deudas_y_obligaciones', []))
                
                urban_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', []))
                rustic_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                
                processed_data.append({
                    'deputy_index': idx,
                    'Nombre': personal_info.get('nombre_y_apellidos', '').upper(),
                    'Cargo': personal_info.get('cargo', 'Diputado'),
                    'Circunscripción': personal_info.get('circunscripcion', ''),
                    'Estado Civil': personal_info.get('estado_civil', ''),
                    'Régimen Económico': personal_info.get('regimen_economico_matrimonial', ''),
                    'Ingresos Declarados': total_income,
                    'Activos Líquidos': liquid_assets,
                    'Deudas': total_debt,
                    'Posición Neta': liquid_assets - total_debt,
                    'IRPF Pagado': parse_money_value(data.get('irpf', {}).get('cantidad_pagada', 0)),
                    'Propiedades Urbanas': urban_properties,
                    'Propiedades Rústicas': rustic_properties,
                    'Total Propiedades': urban_properties + rustic_properties,
                    'Vehículos': len(data.get('vehiculos', [])),
                })
        return pd.DataFrame(processed_data)
    except Exception:
        return pd.DataFrame()

# Disclaimer Screen
if not st.session_state.disclaimer_accepted:
    st.markdown('<div class="hero-section"><h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1><p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.error("⚠️ **Descargo de Responsabilidad Legal**")
        st.info("**Naturaleza de la Aplicación:** Esta es una herramienta independiente de análisis y visualización de información pública y no tiene vinculación oficial con el Congreso de los Diputados.")
        st.warning("**Precisión de los Datos:** Los datos provienen de fuentes públicas. Pueden existir errores o inexactitudes derivados del procesamiento automatizado. Verifique siempre con las fuentes oficiales.")
    if st.button("✅ **Aceptar y Continuar**", use_container_width=True, type="primary"):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    st.stop()

# Main App UI
st.markdown('<div class="hero-section"><h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1><p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p></div>', unsafe_allow_html=True)

df = load_json_data()

if not df.empty:
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos Completa"])
    
    with tab1:
        st.header("Análisis Individual de Parlamentarios")
        search_term = st.text_input("🔎 Buscar por nombre:", placeholder="Introduzca el nombre del parlamentario...")
        
        filtered_names = sorted(df[df['Nombre'].str.contains(search_term, case=False, na=False)]['Nombre'].unique()) if search_term else sorted(df['Nombre'].unique())
        
        if filtered_names:
            selected_name = st.selectbox("Seleccione parlamentario:", filtered_names, key="single_select")
            person_data = df[df['Nombre'] == selected_name].iloc[0]

            # --- Main Deputy Info Card ---
            with st.container(border=True):
                left_col, right_col = st.columns([1, 2.5])

                with left_col:
                    photo_path = f"fotos_diputados/deputy_{person_data['deputy_index']:03d}.jpg"
                    if os.path.exists(photo_path):
                        st.image(photo_path, use_container_width=True)
                    else:
                        st.markdown("<div style='height: 250px; display: flex; align-items: center; justify-content: center; font-size: 4rem; border: 1px solid #444; border-radius: 10px;'>👤</div>", unsafe_allow_html=True)
                        st.caption("Foto no disponible")
                    
                    st.markdown("---")
                    st.caption("PARTIDO POLÍTICO")
                    logo_path = f"deputy_photos/deputy_{person_data['deputy_index']:04d}.jpg"
                    if os.path.exists(logo_path):
                        st.image(logo_path, width=100)
                    else:
                        st.caption("Logo no disponible")

                with right_col:
                    st.title(person_data['Nombre'])
                    
                    info_text = f"""
                    <p>📍 <b>Circunscripción:</b> {person_data['Circunscripción']}</p>
                    <p>🏛️ <b>Cargo:</b> {person_data['Cargo']}</p>
                    """
                    regimen = person_data['Régimen Económico']
                    estado_civil = person_data['Estado Civil']
                    if regimen and regimen.lower() not in ['no procede', '']:
                        estado_civil += f" ({regimen})"
                    info_text += f"<p>💑 <b>Estado Civil:</b> {estado_civil}</p>"
                    st.markdown(info_text, unsafe_allow_html=True)

                    st.divider()
                    seat_gif = get_hemiciclo_seat(person_data['deputy_index'])
                    if seat_gif:
                        st.caption("ESCAÑO EN EL HEMICICLO")
                        st.image(seat_gif, width=200)

            # --- Financial Details Below the Card ---
            st.subheader("Información Financiera y Patrimonio")
            with st.container(border=True):
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                net_position = person_data['Posición Neta']
                m_col1.metric("Ingresos Declarados", f"€{person_data['Ingresos Declarados']:,.0f}")
                m_col2.metric("Activos Líquidos", f"€{person_data['Activos Líquidos']:,.0f}")
                m_col3.metric("Deudas", f"€{person_data['Deudas']:,.0f}")
                m_col4.metric("Posición Neta", f"€{net_position:,.0f}", delta_color="normal" if net_position >= 0 else "inverse")
                
                st.markdown("---")
                
                p_col1, p_col2, p_col3, p_col4 = st.columns(4)
                p_col1.metric("IRPF Pagado", f"€{person_data['IRPF Pagado']:,.0f}")
                p_col2.metric("Prop. Urbanas", int(person_data['Propiedades Urbanas']))
                p_col3.metric("Prop. Rústicas", int(person_data['Propiedades Rústicas']))
                p_col4.metric("Vehículos", int(person_data['Vehículos']))

    with tab2:
        st.header("Tabla de Datos Completa")
        with st.expander("🔧 Filtros Avanzados", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            min_income = col1.number_input("Ingresos mínimos (€):", min_value=0, value=0, step=10000)
            max_debt = col2.number_input("Deuda máxima (€):", min_value=0, value=10000000, step=10000)
            constituencies = ['Todas'] + sorted(df['Circunscripción'].dropna().unique().tolist())
            selected_constituency = col3.selectbox("Circunscripción:", constituencies)
            sort_by = col4.selectbox("Ordenar por:", ['Ingresos Declarados', 'Activos Líquidos', 'Posición Neta', 'Deudas'])
            sort_order = col4.radio("Orden:", ['Descendente', 'Ascendente'], horizontal=True)

        # Apply filters
        filtered_df = df[
            (df['Ingresos Declarados'] >= min_income) &
            (df['Deudas'] <= max_debt) &
            ((df['Circunscripción'] == selected_constituency) | (selected_constituency == 'Todas'))
        ].sort_values(sort_by, ascending=(sort_order == 'Ascendente'))
        
        st.markdown(f"<div class='info-card'>📊 Mostrando <b>{len(filtered_df)}</b> de <b>{len(df)}</b> parlamentarios</div>", unsafe_allow_html=True)
        
        display_df = filtered_df.drop(columns=['deputy_index'])
        money_cols = ['Ingresos Declarados', 'Activos Líquidos', 'Deudas', 'Posición Neta', 'IRPF Pagado']
        for col in money_cols:
            display_df[col] = display_df[col].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)
        
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar datos (CSV)", csv, "declaraciones_filtradas.csv", "text/csv")

else:
    st.error("Error al cargar los datos. Verifique que el archivo 'all_deputies_merged.json' existe y tiene el formato correcto.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: rgba(255, 255, 255, 0.5);'><p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p></div>", unsafe_allow_html=True)
