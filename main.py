import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="📋 Deputies Financial Disclosure Explorer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .info-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .section-header {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.3rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .deputy-name {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .property-item {
        background: #f0fdf4;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #10b981;
    }
    .debt-item {
        background: #fef2f2;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #ef4444;
    }
    .income-item {
        background: #fefce8;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #eab308;
    }
    .account-item {
        background: #eff6ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #3b82f6;
    }
    .vehicle-item {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #6b7280;
    }
    .stock-item {
        background: #faf5ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 4px solid #a855f7;
    }
    .item-counter {
        background: #667eea;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the deputies data"""
    df = pd.read_csv('all_deputies_transformed.csv')
    
    # Clean up names
    df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].str.strip()
    
    # Clean up circunscripcion (standardize case)
    if 'informacion_personal_circunscripcion' in df.columns:
        df['informacion_personal_circunscripcion'] = df['informacion_personal_circunscripcion'].fillna('NO ESPECIFICADO')
        df['informacion_personal_circunscripcion'] = df['informacion_personal_circunscripcion'].str.upper()
    
    return df

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value == '[]' or field_value == '' or field_value is None:
        return []
    try:
        result = json.loads(field_value)
        return result if isinstance(result, list) else [result]
    except:
        return []

def format_currency(value):
    """Format currency values"""
    if pd.isna(value):
        return "No declarado"
    try:
        if isinstance(value, str):
            # Remove currency symbols and convert
            value = value.replace('€', '').replace(',', '.').strip()
            value = float(value)
        return f"€{value:,.2f}"
    except:
        return str(value)

def display_personal_info(row):
    """Display personal information section"""
    st.markdown('<div class="section-header">👤 Información Personal Completa</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Datos Básicos")
        data_items = [
            ("📍 **Circunscripción:**", row.get('informacion_personal_circunscripcion', 'No especificado')),
            ("💼 **Cargo:**", row.get('informacion_personal_cargo', 'Diputado')),
            ("💑 **Estado Civil:**", row.get('informacion_personal_estado_civil', 'No declarado')),
            ("📄 **Régimen Matrimonial:**", row.get('informacion_personal_regimen_economico_matrimonial', 'No aplica')),
        ]
        for label, value in data_items:
            if value and value != 'No aplica':
                st.markdown(f"{label} {value}")
    
    with col2:
        st.markdown("### 📅 Fechas Importantes")
        st.markdown(f"**Fecha de Elección:** {row.get('informacion_personal_fecha_eleccion', 'No especificado')}")
        st.markdown(f"**Presentación de Credencial:** {row.get('informacion_personal_fecha_presentacion_credencial', 'No especificado')}")
        
        # Source file info
        if 'source_file' in row and row['source_file']:
            st.markdown(f"**📁 Archivo fuente:** `{row['source_file']}`")

def display_all_income(row):
    """Display ALL income information comprehensively"""
    st.markdown('<div class="section-header">💰 Todas las Rentas e Ingresos Declarados</div>', unsafe_allow_html=True)
    
    total_items = 0
    
    # 1. SALARIOS
    salarios = parse_json_field(row.get('rentas_percibidas_percepciones_salariales', '[]'))
    if salarios:
        st.markdown(f"### 💼 Percepciones Salariales <span class='item-counter'>{len(salarios)} items</span>", unsafe_allow_html=True)
        for i, sal in enumerate(salarios, 1):
            st.markdown(f'<div class="income-item">', unsafe_allow_html=True)
            concepto = sal.get('concepto', 'Concepto no especificado')
            euros = sal.get('euros', 'Cantidad no declarada')
            st.markdown(f"**Item {i}:** {concepto}")
            st.markdown(f"**💵 Importe:** {euros}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_items += len(salarios)
    else:
        st.info("💼 No hay percepciones salariales declaradas")
    
    # 2. DIVIDENDOS
    dividendos = parse_json_field(row.get('rentas_percibidas_dividendos_y_participaciones', '[]'))
    if dividendos:
        st.markdown(f"### 📈 Dividendos y Participaciones <span class='item-counter'>{len(dividendos)} items</span>", unsafe_allow_html=True)
        for i, div in enumerate(dividendos, 1):
            st.markdown(f'<div class="income-item">', unsafe_allow_html=True)
            if isinstance(div, dict):
                for key, value in div.items():
                    st.markdown(f"**{key}:** {value}")
            else:
                st.markdown(f"**Item {i}:** {div}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_items += len(dividendos)
    else:
        st.info("📈 No hay dividendos declarados")
    
    # 3. INTERESES FINANCIEROS
    intereses = parse_json_field(row.get('rentas_percibidas_intereses_financieros', '[]'))
    if intereses:
        st.markdown(f"### 🏦 Intereses Financieros <span class='item-counter'>{len(intereses)} items</span>", unsafe_allow_html=True)
        for i, interes in enumerate(intereses, 1):
            st.markdown(f'<div class="income-item">', unsafe_allow_html=True)
            if isinstance(interes, dict):
                for key, value in interes.items():
                    st.markdown(f"**{key}:** {value}")
            else:
                st.markdown(f"**Item {i}:** {interes}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_items += len(intereses)
    else:
        st.info("🏦 No hay intereses financieros declarados")
    
    # 4. OTRAS RENTAS
    otras = parse_json_field(row.get('rentas_percibidas_otras_rentas', '[]'))
    if otras:
        st.markdown(f"### 📊 Otras Rentas <span class='item-counter'>{len(otras)} items</span>", unsafe_allow_html=True)
        for i, otra in enumerate(otras, 1):
            st.markdown(f'<div class="income-item">', unsafe_allow_html=True)
            if isinstance(otra, dict):
                for key, value in otra.items():
                    st.markdown(f"**{key}:** {value}")
            else:
                st.markdown(f"**Item {i}:** {otra}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_items += len(otras)
    else:
        st.info("📊 No hay otras rentas declaradas")
    
    # 5. IRPF
    st.markdown("### 🏛️ IRPF Pagado")
    col1, col2, col3 = st.columns(3)
    with col1:
        irpf = format_currency(row.get('irpf_cantidad_pagada'))
        st.metric("Cantidad pagada de IRPF", irpf)
    with col2:
        st.metric("Total items de ingresos", total_items)

def display_all_properties(row):
    """Display ALL property information"""
    st.markdown('<div class="section-header">🏠 Todos los Bienes Patrimoniales</div>', unsafe_allow_html=True)
    
    total_properties = 0
    
    # 1. INMUEBLES URBANOS
    urbanos = parse_json_field(row.get('bienes_patrimoniales_inmuebles_urbanos', '[]'))
    if urbanos:
        st.markdown(f"### 🏢 Inmuebles Urbanos <span class='item-counter'>{len(urbanos)} propiedades</span>", unsafe_allow_html=True)
        for i, prop in enumerate(urbanos, 1):
            st.markdown(f'<div class="property-item">', unsafe_allow_html=True)
            st.markdown(f"**🏠 Propiedad Urbana #{i}**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tipo:** {prop.get('clase_y_caracteristicas', 'No especificado')}")
                st.markdown(f"**📍 Ubicación:** {prop.get('situacion', 'No especificado')}")
                st.markdown(f"**📅 Fecha Adquisición:** {prop.get('fecha_adquisicion', 'No especificado')}")
            with col2:
                st.markdown(f"**📜 Título:** {prop.get('titulo_adquisicion', 'No especificado')}")
                st.markdown(f"**✅ Derecho:** {prop.get('derecho_sobre_el_bien', 'No especificado')}")
                # Check for any additional fields
                for key, value in prop.items():
                    if key not in ['clase_y_caracteristicas', 'situacion', 'fecha_adquisicion', 'titulo_adquisicion', 'derecho_sobre_el_bien']:
                        st.markdown(f"**{key}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_properties += len(urbanos)
    else:
        st.info("🏢 No hay inmuebles urbanos declarados")
    
    # 2. INMUEBLES RÚSTICOS
    rusticos = parse_json_field(row.get('bienes_patrimoniales_inmuebles_rusticos', '[]'))
    if rusticos:
        st.markdown(f"### 🌾 Inmuebles Rústicos <span class='item-counter'>{len(rusticos)} propiedades</span>", unsafe_allow_html=True)
        for i, prop in enumerate(rusticos, 1):
            st.markdown(f'<div class="property-item">', unsafe_allow_html=True)
            st.markdown(f"**🌾 Propiedad Rústica #{i}**")
            if isinstance(prop, dict):
                for key, value in prop.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{prop}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_properties += len(rusticos)
    else:
        st.info("🌾 No hay inmuebles rústicos declarados")
    
    # 3. BIENES EN SOCIEDADES NO COTIZADAS
    sociedades = parse_json_field(row.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', '[]'))
    if sociedades:
        st.markdown(f"### 🏭 Bienes en Sociedades No Cotizadas <span class='item-counter'>{len(sociedades)} items</span>", unsafe_allow_html=True)
        for i, soc in enumerate(sociedades, 1):
            st.markdown(f'<div class="property-item">', unsafe_allow_html=True)
            st.markdown(f"**🏭 Sociedad #{i}**")
            if isinstance(soc, dict):
                for key, value in soc.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{soc}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_properties += len(sociedades)
    else:
        st.info("🏭 No hay bienes en sociedades no cotizadas")
    
    st.metric("Total de propiedades", total_properties)

def display_all_vehicles(row):
    """Display ALL vehicle information"""
    vehiculos = parse_json_field(row.get('vehiculos', '[]'))
    
    st.markdown(f'<div class="section-header">🚗 Todos los Vehículos <span class="item-counter">{len(vehiculos)} vehículos</span></div>', unsafe_allow_html=True)
    
    if vehiculos:
        for i, vehicle in enumerate(vehiculos, 1):
            st.markdown(f'<div class="vehicle-item">', unsafe_allow_html=True)
            st.markdown(f"**🚗 Vehículo #{i}**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Descripción:** {vehicle.get('descripcion', 'Vehículo no especificado')}")
            with col2:
                st.markdown(f"**📅 Fecha Adquisición:** {vehicle.get('fecha_adquisicion', 'No especificado')}")
            # Check for additional fields
            for key, value in vehicle.items():
                if key not in ['descripcion', 'fecha_adquisicion']:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🚗 No hay vehículos declarados")

def display_all_financial_assets(row):
    """Display ALL financial assets comprehensively"""
    st.markdown('<div class="section-header">💳 Todos los Activos Financieros y Valores</div>', unsafe_allow_html=True)
    
    total_financial_items = 0
    
    # 1. CUENTAS BANCARIAS
    cuentas = parse_json_field(row.get('depositos_y_cuentas_cuentas', '[]'))
    if cuentas:
        st.markdown(f"### 🏦 Depósitos y Cuentas Bancarias <span class='item-counter'>{len(cuentas)} cuentas</span>", unsafe_allow_html=True)
        for i, cuenta in enumerate(cuentas, 1):
            st.markdown(f'<div class="account-item">', unsafe_allow_html=True)
            st.markdown(f"**💳 Cuenta #{i}**")
            st.markdown(f"**Descripción:** {cuenta.get('descripcion', 'Cuenta no especificada')}")
            st.markdown(f"**💰 Saldo:** {cuenta.get('saldo', 'No declarado')}")
            # Check for additional fields
            for key, value in cuenta.items():
                if key not in ['descripcion', 'saldo']:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_financial_items += len(cuentas)
    else:
        st.info("🏦 No hay cuentas bancarias declaradas")
    
    # 2. DEUDA PÚBLICA Y VALORES
    valores = parse_json_field(row.get('otros_bienes_y_derechos_deuda_publica_y_valores', '[]'))
    if valores:
        st.markdown(f"### 📊 Deuda Pública y Valores <span class='item-counter'>{len(valores)} items</span>", unsafe_allow_html=True)
        for i, valor in enumerate(valores, 1):
            st.markdown(f'<div class="stock-item">', unsafe_allow_html=True)
            st.markdown(f"**📈 Valor #{i}**")
            if isinstance(valor, dict):
                st.markdown(f"**Descripción:** {valor.get('descripcion', 'No especificado')}")
                st.markdown(f"**💵 Valor:** {valor.get('valor', 'No declarado')}")
                # Additional fields
                for key, value in valor.items():
                    if key not in ['descripcion', 'valor']:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{valor}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_financial_items += len(valores)
    else:
        st.info("📊 No hay valores o deuda pública declarada")
    
    # 3. ACCIONES Y PARTICIPACIONES
    acciones = parse_json_field(row.get('otros_bienes_y_derechos_acciones_y_participaciones', '[]'))
    if acciones:
        st.markdown(f"### 📈 Acciones y Participaciones <span class='item-counter'>{len(acciones)} items</span>", unsafe_allow_html=True)
        for i, accion in enumerate(acciones, 1):
            st.markdown(f'<div class="stock-item">', unsafe_allow_html=True)
            st.markdown(f"**📈 Acción/Participación #{i}**")
            if isinstance(accion, dict):
                for key, value in accion.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{accion}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_financial_items += len(acciones)
    else:
        st.info("📈 No hay acciones o participaciones declaradas")
    
    # 4. SOCIEDADES PARTICIPADAS MÁS DEL 5%
    sociedades_5 = parse_json_field(row.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', '[]'))
    if sociedades_5:
        st.markdown(f"### 🏢 Sociedades Participadas (>5%) <span class='item-counter'>{len(sociedades_5)} sociedades</span>", unsafe_allow_html=True)
        for i, soc in enumerate(sociedades_5, 1):
            st.markdown(f'<div class="stock-item">', unsafe_allow_html=True)
            st.markdown(f"**🏢 Sociedad #{i}**")
            if isinstance(soc, dict):
                for key, value in soc.items():
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{soc}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_financial_items += len(sociedades_5)
    else:
        st.info("🏢 No hay sociedades participadas más del 5%")
    
    # 5. OTROS BIENES NO DECLARADOS ANTERIORMENTE
    otros = parse_json_field(row.get('otros_bienes_no_declarados_anteriormente', '[]'))
    if otros:
        st.markdown(f"### 📦 Otros Bienes <span class='item-counter'>{len(otros)} items</span>", unsafe_allow_html=True)
        for i, otro in enumerate(otros, 1):
            st.markdown(f'<div class="stock-item">', unsafe_allow_html=True)
            st.markdown(f"**📦 Bien #{i}**")
            if isinstance(otro, dict):
                st.markdown(f"**Descripción:** {otro.get('descripcion', 'No especificado')}")
                st.markdown(f"**💵 Valor:** {otro.get('valor', 'No declarado')}")
                for key, value in otro.items():
                    if key not in ['descripcion', 'valor']:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                st.markdown(f"{otro}")
            st.markdown('</div>', unsafe_allow_html=True)
        total_financial_items += len(otros)
    else:
        st.info("📦 No hay otros bienes declarados")
    
    st.metric("Total de activos financieros", total_financial_items)

def display_all_debts(row):
    """Display ALL debts and obligations"""
    deudas = parse_json_field(row.get('deudas_y_obligaciones', '[]'))
    
    st.markdown(f'<div class="section-header">💳 Todas las Deudas y Obligaciones <span class="item-counter">{len(deudas)} deudas</span></div>', unsafe_allow_html=True)
    
    if deudas:
        total_deuda = 0
        for i, deuda in enumerate(deudas, 1):
            st.markdown(f'<div class="debt-item">', unsafe_allow_html=True)
            st.markdown(f"**💳 Deuda #{i}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tipo:** {deuda.get('descripcion', 'Préstamo no especificado')}")
                st.markdown(f"**📅 Fecha Concesión:** {deuda.get('fecha_concesion', 'No especificado')}")
                st.markdown(f"**💰 Importe Concedido:** {deuda.get('importe_concedido', 'No declarado')}")
            with col2:
                saldo = deuda.get('saldo_pendiente', 'No declarado')
                st.markdown(f"**⚠️ Saldo Pendiente:** **{saldo}**")
                
                # Try to calculate total debt
                try:
                    if isinstance(saldo, str):
                        saldo_num = float(saldo.replace('€', '').replace(',', '.').replace(' ', ''))
                        total_deuda += saldo_num
                except:
                    pass
                
                # Check for additional fields
                for key, value in deuda.items():
                    if key not in ['descripcion', 'fecha_concesion', 'importe_concedido', 'saldo_pendiente']:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if total_deuda > 0:
            st.error(f"**💸 Deuda Total Pendiente Estimada: €{total_deuda:,.2f}**")
    else:
        st.success("✅ No hay deudas u obligaciones declaradas")

def display_observations(row):
    """Display observations if any"""
    obs = row.get('observaciones')
    if obs and not pd.isna(obs) and obs.strip():
        st.markdown('<div class="section-header">📝 Observaciones Adicionales</div>', unsafe_allow_html=True)
        st.info(obs)

def display_complete_summary(row):
    """Create a complete summary with all counts"""
    st.markdown('<div class="section-header">📊 Resumen Completo del Patrimonio</div>', unsafe_allow_html=True)
    
    # Calculate all totals
    num_salarios = len(parse_json_field(row.get('rentas_percibidas_percepciones_salariales', '[]')))
    num_dividendos = len(parse_json_field(row.get('rentas_percibidas_dividendos_y_participaciones', '[]')))
    num_intereses = len(parse_json_field(row.get('rentas_percibidas_intereses_financieros', '[]')))
    num_otras_rentas = len(parse_json_field(row.get('rentas_percibidas_otras_rentas', '[]')))
    
    num_urbanos = len(parse_json_field(row.get('bienes_patrimoniales_inmuebles_urbanos', '[]')))
    num_rusticos = len(parse_json_field(row.get('bienes_patrimoniales_inmuebles_rusticos', '[]')))
    num_sociedades = len(parse_json_field(row.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', '[]')))
    
    num_vehicles = len(parse_json_field(row.get('vehiculos', '[]')))
    num_cuentas = len(parse_json_field(row.get('depositos_y_cuentas_cuentas', '[]')))
    num_valores = len(parse_json_field(row.get('otros_bienes_y_derechos_deuda_publica_y_valores', '[]')))
    num_acciones = len(parse_json_field(row.get('otros_bienes_y_derechos_acciones_y_participaciones', '[]')))
    num_sociedades_5 = len(parse_json_field(row.get('otros_bienes_y_derechos_sociedades_participadas_mas_5_por_ciento', '[]')))
    num_otros = len(parse_json_field(row.get('otros_bienes_no_declarados_anteriormente', '[]')))
    num_deudas = len(parse_json_field(row.get('deudas_y_obligaciones', '[]')))
    
    # Display metrics in organized sections
    st.markdown("### 💰 Resumen de Ingresos")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💼 Salarios", num_salarios)
    with col2:
        st.metric("📈 Dividendos", num_dividendos)
    with col3:
        st.metric("🏦 Intereses", num_intereses)
    with col4:
        st.metric("📊 Otras Rentas", num_otras_rentas)
    
    st.markdown("### 🏠 Resumen de Propiedades")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Inmuebles Urbanos", num_urbanos)
    with col2:
        st.metric("🌾 Inmuebles Rústicos", num_rusticos)
    with col3:
        st.metric("🏭 Sociedades No Cotizadas", num_sociedades)
    with col4:
        st.metric("🚗 Vehículos", num_vehicles)
    
    st.markdown("### 💳 Resumen Financiero")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🏦 Cuentas", num_cuentas)
    with col2:
        st.metric("📊 Valores", num_valores)
    with col3:
        st.metric("📈 Acciones", num_acciones)
    with col4:
        st.metric("🏢 Sociedades >5%", num_sociedades_5)
    with col5:
        st.metric("💸 Deudas", num_deudas, delta_color="inverse")
    
    # Total items
    total_items = (num_salarios + num_dividendos + num_intereses + num_otras_rentas +
                  num_urbanos + num_rusticos + num_sociedades + num_vehicles +
                  num_cuentas + num_valores + num_acciones + num_sociedades_5 + 
                  num_otros + num_deudas)
    
    st.markdown("---")
    st.metric("📋 **TOTAL DE ITEMS DECLARADOS**", total_items)
    
    # Create visualization
    if total_items > 0:
        st.markdown("### 📈 Distribución Visual del Patrimonio")
        
        categories = []
        values = []
        colors = []
        
        if num_salarios > 0:
            categories.append(f'Salarios ({num_salarios})')
            values.append(num_salarios)
            colors.append('#eab308')
        
        total_properties = num_urbanos + num_rusticos + num_sociedades
        if total_properties > 0:
            categories.append(f'Propiedades ({total_properties})')
            values.append(total_properties)
            colors.append('#10b981')
        
        if num_vehicles > 0:
            categories.append(f'Vehículos ({num_vehicles})')
            values.append(num_vehicles)
            colors.append('#6b7280')
        
        total_financial = num_cuentas + num_valores + num_acciones + num_sociedades_5
        if total_financial > 0:
            categories.append(f'Activos Financieros ({total_financial})')
            values.append(total_financial)
            colors.append('#3b82f6')
        
        if num_otros > 0:
            categories.append(f'Otros Bienes ({num_otros})')
            values.append(num_otros)
            colors.append('#a855f7')
        
        if num_deudas > 0:
            categories.append(f'Deudas ({num_deudas})')
            values.append(num_deudas)
            colors.append('#ef4444')
        
        if categories:
            fig = go.Figure(data=[go.Pie(
                labels=categories,
                values=values,
                hole=.3,
                marker_colors=colors
            )])
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Items: %{value}<br>Porcentaje: %{percent}<extra></extra>'
            )
            fig.update_layout(
                height=500,
                showlegend=True,
                title="Distribución de Items Declarados"
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏛️ Explorador Completo de Declaraciones Patrimoniales</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Sistema integral para consultar TODA la información patrimonial de los diputados españoles</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filtros de Búsqueda")
        
        # Search by name
        search_name = st.text_input("🔎 Buscar por nombre", placeholder="Escribe el nombre del diputado...")
        
        # Filter by circumscription
        circunscripciones = ['Todas'] + sorted(df['informacion_personal_circunscripcion'].dropna().unique().tolist())
        selected_circ = st.selectbox("📍 Filtrar por circunscripción", circunscripciones)
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_name:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_name, case=False, na=False)]
        
        if selected_circ != 'Todas':
            filtered_df = filtered_df[filtered_df['informacion_personal_circunscripcion'] == selected_circ]
        
        st.markdown("---")
        st.markdown(f"### 📊 Estadísticas Generales")
        st.metric("Total de diputados", len(df))
        st.metric("Diputados filtrados", len(filtered_df))
        
        # Average IRPF
        avg_irpf = df['irpf_cantidad_pagada'].mean()
        if not pd.isna(avg_irpf):
            st.metric("IRPF medio", format_currency(avg_irpf))
        
        # Show info about data completeness
        st.markdown("### ℹ️ Información")
        st.info("Este sistema muestra TODA la información disponible de cada diputado, incluyendo múltiples propiedades, cuentas, deudas, etc.")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("No se encontraron diputados con los filtros seleccionados.")
    else:
        # Deputy selector
        st.markdown("### 👤 Selecciona un Diputado")
        
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "Elige un diputado para ver TODA su información patrimonial:",
            deputy_names,
            format_func=lambda x: f"{x} - {filtered_df[filtered_df['informacion_personal_nombre_y_apellidos']==x]['informacion_personal_circunscripcion'].values[0]}"
        )
        
        if selected_deputy:
            # Get deputy data
            deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
            
            st.markdown("---")
            
            # Display deputy name prominently
            st.markdown(f'<div class="deputy-name">{selected_deputy}</div>', unsafe_allow_html=True)
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                "📋 Personal", 
                "💰 Ingresos", 
                "🏠 Propiedades", 
                "🚗 Vehículos",
                "💳 Activos Financieros", 
                "💸 Deudas",
                "📝 Observaciones",
                "📊 Resumen Total"
            ])
            
            with tab1:
                display_personal_info(deputy_data)
            
            with tab2:
                display_all_income(deputy_data)
            
            with tab3:
                display_all_properties(deputy_data)
            
            with tab4:
                display_all_vehicles(deputy_data)
            
            with tab5:
                display_all_financial_assets(deputy_data)
            
            with tab6:
                display_all_debts(deputy_data)
            
            with tab7:
                display_observations(deputy_data)
                if not (deputy_data.get('observaciones') and not pd.isna(deputy_data.get('observaciones'))):
                    st.info("📝 No hay observaciones adicionales para este diputado")
            
            with tab8:
                display_complete_summary(deputy_data)
                
                # Export option
                st.markdown("---")
                st.markdown("### 💾 Exportar Información")
                if st.button("📄 Generar informe completo en texto"):
                    report = f"""
INFORME COMPLETO DE DECLARACIÓN PATRIMONIAL
==========================================
Nombre: {selected_deputy}
Circunscripción: {deputy_data.get('informacion_personal_circunscripcion', 'No especificado')}
Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATOS COMPLETOS EN JSON:
{deputy_data.to_json(indent=2)}
                    """
                    st.text_area("Informe completo:", report, height=400)

if __name__ == "__main__":
    main()
