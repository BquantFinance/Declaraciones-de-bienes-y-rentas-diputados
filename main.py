import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode CSS - simplified
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    
    .hero-title {
        color: white;
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1rem;
    }
    
    .individual-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .photo-container {
        max-width: 150px;
        margin: 0 auto;
    }
    
    .deputy-photo {
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        width: 100%;
        height: auto;
    }
    
    .party-logo {
        max-width: 80px;
        height: auto;
    }
    
    h1, h2, h3 {
        color: white !important;
    }
    
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Helper functions
def parse_money_value(value):
    """Convert string money values to float"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    value_str = str(value).replace('€', '').replace('.', '').replace(',', '.')
    value_str = value_str.strip()
    try:
        return float(value_str)
    except:
        return 0

def get_deputy_photo(deputy_index):
    """Get the actual deputy photo"""
    photo_path = f"deputy_photos/deputy_{deputy_index:03d}.jpg"
    if os.path.exists(photo_path):
        return photo_path
    return None

def get_party_logo(party_name):
    """Get party logo from fotos_diputados folder"""
    party_mapping = {
        'PP': 'fotos_diputados/pp_logo.png',
        'PSOE': 'fotos_diputados/psoe_logo.png', 
        'VOX': 'fotos_diputados/vox_logo.png',
        'SUMAR': 'fotos_diputados/sumar_logo.png'
    }
    
    # Try to determine party from position or other fields
    for party, path in party_mapping.items():
        if party in party_name.upper():
            if os.path.exists(path):
                return path
    return None

def get_hemiciclo_seat(deputy_index):
    """Get hemiciclo seat visualization"""
    # Pattern: hemi_XXXX_YYYY.gif where XXXX is deputy number, YYYY is seat
    import glob
    pattern = f"hemiciclo/hemi_{deputy_index:04d}_*.gif"
    files = glob.glob(pattern)
    if files:
        return files[0]
    return None

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
                
                # Calculate totals
                total_income = 0
                rentas = data.get('rentas_percibidas', {})
                
                for salary in rentas.get('percepciones_salariales', []):
                    total_income += parse_money_value(salary.get('euros', 0))
                for dividend in rentas.get('dividendos_y_participaciones', []):
                    total_income += parse_money_value(dividend.get('euros', 0))
                for interest in rentas.get('intereses_financieros', []):
                    total_income += parse_money_value(interest.get('euros', 0))
                for other in rentas.get('otras_rentas', []):
                    total_income += parse_money_value(other.get('euros', 0))
                
                # Liquid assets
                liquid_assets = 0
                accounts = data.get('depositos_y_cuentas', {}).get('cuentas', [])
                for account in accounts:
                    liquid_assets += parse_money_value(account.get('saldo', 0))
                
                # Debt
                total_debt = 0
                debts = data.get('deudas_y_obligaciones', [])
                for debt in debts:
                    total_debt += parse_money_value(debt.get('saldo_pendiente', 0))
                
                # Properties
                urban_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', []))
                rustic_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                vehicles_count = len(data.get('vehiculos', []))
                
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
                    'Vehículos': vehicles_count,
                })
        
        return pd.DataFrame(processed_data)
        
    except FileNotFoundError:
        st.error("No se encuentra el archivo 'all_deputies_merged.json'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        return pd.DataFrame()

# Disclaimer
if not st.session_state.disclaimer_accepted:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
        <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("""
    ⚠️ **Descargo de Responsabilidad**
    
    Esta aplicación es una herramienta independiente de visualización de información pública.
    No tiene vinculación con el Congreso de los Diputados. Los datos pueden contener errores.
    Para información oficial, consulte el portal del Congreso de los Diputados.
    """)
    
    if st.button("✅ Aceptar y Continuar", type="primary"):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    
    st.stop()

# Main App
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
    <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
</div>
""", unsafe_allow_html=True)

# Load data
df = load_json_data()

if not df.empty:
    # Tabs for navigation
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos"])
    
    with tab1:
        st.markdown("### Consulta Individual de Parlamentarios")
        
        # Search
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Buscar por nombre:", placeholder="Introduzca el nombre del parlamentario...")
        
        # Filter names based on search
        if search_term:
            filtered_df = df[df['Nombre'].str.contains(search_term, case=False, na=False)]
            names = sorted(filtered_df['Nombre'].unique())
        else:
            names = sorted(df['Nombre'].unique())
        
        if names:
            selected_name = st.selectbox("Seleccione parlamentario:", names)
            
            if selected_name:
                person_data = df[df['Nombre'] == selected_name].iloc[0]
                
                # Layout with photos
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
                with col1:
                    # Deputy photo
                    photo_path = get_deputy_photo(person_data['deputy_index'])
                    if photo_path:
                        st.markdown('<div class="photo-container">', unsafe_allow_html=True)
                        st.image(photo_path, caption="Foto", use_column_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("📷 Sin foto")
                
                with col2:
                    # Personal information
                    st.markdown(f"""
                    <div class="individual-card">
                        <h3>{person_data['Nombre']}</h3>
                        <p>📍 {person_data['Circunscripción']} | 🏛️ {person_data['Cargo']}</p>
                        <p>👤 {person_data['Estado Civil']} | {person_data['Régimen Económico']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    # Party logo
                    party_logo = get_party_logo(person_data.get('Partido', ''))
                    if party_logo:
                        st.markdown('<div class="party-logo">', unsafe_allow_html=True)
                        st.image(party_logo, caption="Partido")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    # Hemiciclo seat
                    seat_path = get_hemiciclo_seat(person_data['deputy_index'])
                    if seat_path:
                        st.image(seat_path, caption="Escaño", use_column_width=True)
                
                # Financial data in columns
                st.markdown("---")
                st.markdown("#### 💰 Información Financiera")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ingresos Declarados", f"€{person_data['Ingresos Declarados']:,.0f}")
                with col2:
                    st.metric("Activos Líquidos", f"€{person_data['Activos Líquidos']:,.0f}")
                with col3:
                    st.metric("Deudas", f"€{person_data['Deudas']:,.0f}")
                with col4:
                    st.metric("Posición Neta", f"€{person_data['Posición Neta']:,.0f}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("IRPF Pagado", f"€{person_data['IRPF Pagado']:,.0f}")
                with col2:
                    st.metric("Propiedades Urbanas", f"{int(person_data['Propiedades Urbanas'])}")
                with col3:
                    st.metric("Propiedades Rústicas", f"{int(person_data['Propiedades Rústicas'])}")
                with col4:
                    st.metric("Vehículos", f"{int(person_data['Vehículos'])}")
        else:
            st.warning("No se encontraron resultados")
    
    with tab2:
        st.markdown("### Tabla de Datos Completa")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Income filter
            min_income = st.number_input("Ingresos mínimos (€):", min_value=0, value=0, step=10000)
        
        with col2:
            # Constituency filter
            constituencies = ['Todas'] + sorted(df['Circunscripción'].unique().tolist())
            selected_constituency = st.selectbox("Circunscripción:", constituencies)
        
        with col3:
            # Property filter
            min_properties = st.number_input("Mínimo propiedades:", min_value=0, value=0, step=1)
        
        # Apply filters
        filtered_df = df.copy()
        
        if min_income > 0:
            filtered_df = filtered_df[filtered_df['Ingresos Declarados'] >= min_income]
        
        if selected_constituency != 'Todas':
            filtered_df = filtered_df[filtered_df['Circunscripción'] == selected_constituency]
        
        if min_properties > 0:
            filtered_df = filtered_df[(filtered_df['Propiedades Urbanas'] + filtered_df['Propiedades Rústicas']) >= min_properties]
        
        # Show results count
        st.info(f"Mostrando {len(filtered_df)} de {len(df)} parlamentarios")
        
        # Format columns for display
        display_df = filtered_df.copy()
        money_cols = ['Ingresos Declarados', 'Activos Líquidos', 'Deudas', 'Posición Neta', 'IRPF Pagado']
        for col in money_cols:
            display_df[col] = display_df[col].apply(lambda x: f'€{x:,.0f}')
        
        # Remove deputy_index from display
        display_df = display_df.drop(columns=['deputy_index'])
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Export button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar datos filtrados (CSV)",
            data=csv,
            file_name='declaraciones_filtradas.csv',
            mime='text/csv'
        )

else:
    st.error("Error al cargar los datos. Verifique que existe el archivo 'all_deputies_merged.json'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 20px;'>
    <p>Datos públicos del Congreso de los Diputados</p>
</div>
""", unsafe_allow_html=True)
