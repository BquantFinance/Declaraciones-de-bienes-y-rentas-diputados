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

# Spectacular dark mode CSS with glassmorphism and gradients
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
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }
    
    /* Data tables with glassmorphism */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Tabs with animations */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Buttons with gradient */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Select boxes and inputs */
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

# Load JSON data
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
    except Exception as e:
        st.error(f"Error al procesar el archivo 'all_deputies_merged.json': {e}")
        return pd.DataFrame()

# Show full disclaimer if not accepted
if not st.session_state.disclaimer_accepted:
    st.markdown('<div class="hero-section"><h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1><p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("## ⚠️ **Descargo de Responsabilidad Legal**")
        st.markdown("---")
        st.markdown("### 📋 Naturaleza de la Aplicación")
        st.info("**Esta aplicación constituye una herramienta independiente de análisis y visualización de información pública** disponible en el portal oficial del Congreso de los Diputados. No mantiene vinculación institucional alguna con el Congreso de los Diputados, sus órganos de gobierno, ni cuenta con aval, autorización o respaldo oficial de dicha institución.")
        st.markdown("### 📊 Origen y Precisión de los Datos")
        st.warning("**Los datos presentados provienen de fuentes públicas oficiales y, si bien se ha procurado garantizar su exactitud mediante procesos automatizados de extracción y estructuración, **la aplicación podría contener errores, inexactitudes, omisiones o información desactualizada** derivados del procesamiento de los documentos originales. Para consultas oficiales y verificación de la información, se recomienda acudir directamente a los documentos originales publicados en el portal web del Congreso de los Diputados.")
        st.markdown("### ⚖️ Responsabilidad del Usuario")
        st.write("El uso de esta herramienta es responsabilidad exclusiva del usuario, quien deberá ejercer su propio criterio en la interpretación y utilización de los datos aquí presentados.")
        st.markdown("---")
        st.markdown('<div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 20px; padding: 25px; margin: 20px 0; border: 2px solid rgba(102, 126, 234, 0.3);"><p style="text-align: center; color: white; font-size: 1.1rem; margin: 0;">✅ Al hacer clic en <strong>"Aceptar y Continuar"</strong>, usted reconoce haber leído y comprendido este descargo de responsabilidad, y acepta que el uso de esta aplicación es bajo su propio riesgo y responsabilidad.</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ **Aceptar y Continuar**", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    st.markdown("---")
    st.markdown("<div style='text-align: center; padding: 20px;'><p style='color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;'>Desarrollado con 💜 por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none; font-weight: 600;'>@Gsnchez</a></p></div>", unsafe_allow_html=True)
    st.stop()

# Main App UI
st.markdown('<div class="hero-section"><h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1><p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p><a href="https://twitter.com/Gsnchez" target="_blank" style="display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; color: white; font-weight: 600; text-decoration: none; transition: all 0.3s ease; position: relative; z-index: 1;">Desarrollado por @Gsnchez ✨</a></div>', unsafe_allow_html=True)
st.markdown('<div style="background: rgba(102, 126, 234, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 20px; padding: 30px; margin: 20px 0; color: white;"><h3 style="color: #667eea; margin-top: 0; text-align: center;">📚 Motivación del Proyecto</h3><p style="line-height: 1.8; text-align: justify;">Este proyecto surge con el propósito fundamental de <strong>democratizar el acceso a la información pública</strong> relativa a las declaraciones de bienes y rentas de los parlamentarios españoles.</p><ul style="line-height: 1.8;"><li><strong>Transparencia:</strong> Facilitar el escrutinio público de la información patrimonial de los representantes electos.</li><li><strong>Accesibilidad:</strong> Eliminar las barreras técnicas que dificultan el acceso a estos datos.</li><li><strong>Estructuración:</strong> Organizar sistemáticamente la información dispersa en múltiples documentos PDF.</li></ul></div>', unsafe_allow_html=True)

df = load_json_data()

if not df.empty:
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos Completa"])
    
    with tab1:
        search_term = st.text_input("🔎 Buscar por nombre:", placeholder="Introduzca el nombre del parlamentario...")
        filtered_names = sorted(df[df['Nombre'].str.contains(search_term, case=False, na=False)]['Nombre'].unique()) if search_term else sorted(df['Nombre'].unique())
        
        if filtered_names:
            selected_name = st.selectbox("Seleccione parlamentario:", filtered_names)
            person_data = df[df['Nombre'] == selected_name].iloc[0]

            st.header(person_data['Nombre'])
            st.divider()

            # --- Main Deputy Info Card (Compact Layout) ---
            left_col, right_col = st.columns([1, 3])

            with left_col:
                photo_path = f"fotos_diputados/deputy_{person_data['deputy_index']:03d}.jpg"
                if os.path.exists(photo_path):
                    # MODIFICATION: Set a fixed width for the image
                    st.image(photo_path, width=124)
                else:
                    # MODIFICATION: Adjust placeholder to match the fixed size
                    st.markdown("<div style='width: 124px; height: 165px; display: flex; align-items: center; justify-content: center; font-size: 3rem; border: 1px solid #444; border-radius: 10px;'>👤</div>", unsafe_allow_html=True)
                
                st.divider()
                st.caption("PARTIDO POLÍTICO")
                logo_path = f"deputy_photos/deputy_{person_data['deputy_index']:04d}.jpg"
                if os.path.exists(logo_path):
                    st.image(logo_path, width=80)

            with right_col:
                st.markdown(f"📍 **Circunscripción:** {person_data['Circunscripción']}")
                st.markdown(f"🏛️ **Cargo:** {person_data['Cargo']}")
                regimen = person_data['Régimen Económico']
                estado_civil = person_data['Estado Civil']
                if regimen and regimen.lower() not in ['no procede', '']:
                    estado_civil += f" ({regimen})"
                st.markdown(f"💑 **Estado Civil:** {estado_civil}")

                st.divider()
                seat_gif = get_hemiciclo_seat(person_data['deputy_index'])
                if seat_gif:
                    st.caption("ESCAÑO EN EL HEMICICLO")
                    st.image(seat_gif, width=150)
            
            st.divider()
            # --- Financial Details Below the Card ---
            st.subheader("Información Financiera y Patrimonio")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            net_position = person_data['Posición Neta']
            m_col1.metric("Ingresos", f"€{person_data['Ingresos Declarados']:,.0f}")
            m_col2.metric("Activos", f"€{person_data['Activos Líquidos']:,.0f}")
            m_col3.metric("Deudas", f"€{person_data['Deudas']:,.0f}")
            m_col4.metric("Posición Neta", f"€{net_position:,.0f}", delta_color="normal" if net_position >= 0 else "inverse")
            
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

        filtered_df = df[ (df['Ingresos Declarados'] >= min_income) & (df['Deudas'] <= max_debt) & ((df['Circunscripción'] == selected_constituency) | (selected_constituency == 'Todas')) ].sort_values(sort_by, ascending=(sort_order == 'Ascendente'))
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
st.markdown("<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'><p>🏛️ Datos públicos del Congreso de los Diputados</p><p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p></div>", unsafe_allow_html=True)
