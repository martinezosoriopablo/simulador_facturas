# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:21:34 2025

@author: Pablo Martínez
"""
import streamlit as st
import datetime

# Configuración visual
st.set_page_config(layout="wide")
COLOR_PRINCIPAL = "#3498DB"
hoy = datetime.date.today()

# --- LÓGICA DE SINCRONIZACIÓN DE FECHAS (Uso de Session State) ---

# 1. Definimos las funciones que se ejecutarán cuando un widget cambie.
#    Estas funciones actualizan el valor del otro widget relacionado.

def actualizar_fecha_pago():
    """Se ejecuta cuando cambia el número de días o la fecha de giro."""
    st.session_state.fecha_pago = st.session_state.fecha_giro + datetime.timedelta(days=st.session_state.plazo_dias)

def actualizar_plazo_dias():
    """Se ejecuta cuando cambia la fecha de pago."""
    st.session_state.plazo_dias = (st.session_state.fecha_pago - st.session_state.fecha_giro).days

# 2. Inicializamos los valores en el st.session_state si es la primera vez que se ejecuta.
#    Esto evita que los valores se reseteen con cada interacción.
if 'plazo_dias' not in st.session_state:
    st.session_state.plazo_dias = 60
if 'fecha_giro' not in st.session_state:
    st.session_state.fecha_giro = hoy
if 'fecha_pago' not in st.session_state:
    st.session_state.fecha_pago = hoy + datetime.timedelta(days=st.session_state.plazo_dias)


# --- INTERFAZ DE USUARIO (SIDEBAR) ---

st.sidebar.header("Parámetros de la Factura")
monto_factura = st.sidebar.number_input("Monto de la factura", min_value=1000.0, value=40000.0)

producto = st.sidebar.selectbox("Producto", [
    "Arándanos", "Uvas", "Bananas", "Enlatados", "Aceite",
    "Aguacate", "Congelados", "Harina", "Polipropileno", "Cerezas", "Otros"
])

haircut_option = st.sidebar.radio(
    "Seleccionar tipo de Haircut",
    ('Por producto', 'Manual')
)

haircuts = {
    "Arándanos": 0.25, "Uvas": 0.25, "Bananas": 0.25, "Enlatados": 0.10, "Aceite": 0.15,
    "Aguacate": 0.20, "Congelados": 0.15, "Harina": 0.10, "Polipropileno": 0.10, "Cerezas": 0.40, "Otros": 0.30
}

if haircut_option == 'Por producto':
    haircut = haircuts[producto]
else:
    haircut_manual = st.sidebar.number_input("Haircut manual (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1, format="%.2f")
    haircut = haircut_manual / 100.0

riesgo = st.sidebar.selectbox("Clasificación de riesgo", ["A", "B", "C"])
tasas_mensuales = {"A": 0.009, "B": 0.012, "C": 0.017}
tasa_mensual = tasas_mensuales[riesgo]

# --- Widgets de Fecha Sincronizados ---
st.sidebar.subheader("Plazo del Financiamiento")
fecha_otorgamiento = st.sidebar.date_input("Fecha de otorgamiento", hoy)

# 3. Creamos los widgets y les asignamos una 'key' para acceder a ellos
#    desde el session_state y una función 'on_change' (callback).
st.sidebar.date_input(
    "Fecha de giro",
    key='fecha_giro',
    on_change=actualizar_fecha_pago
)
st.sidebar.number_input(
    "Plazo en días",
    min_value=1,
    step=1,
    key='plazo_dias',
    on_change=actualizar_fecha_pago
)
st.sidebar.date_input(
    "Fecha de pago",
    key='fecha_pago',
    on_change=actualizar_plazo_dias
)

# Otros parámetros
dias_atraso = st.sidebar.slider("Días de atraso", 0, 60, 0)
costo_administracion = st.sidebar.number_input("Costo administrativo (%)", 0.0, value=0.20) / 100
seguro_credito_rate = st.sidebar.number_input("Seguro de crédito (%)", 0.0, value=0.35) / 100
seguro_carga_rate = st.sidebar.number_input("Seguro de carga (%)", 0.0, value=0.10) / 100
iva = 0.19

# --- CÁLCULOS FINANCIEROS (Usando valores del session_state) ---
plazo_dias_calc = st.session_state.plazo_dias # Usamos el valor del estado
fecha_giro_calc = st.session_state.fecha_giro
fecha_pago_calc = st.session_state.fecha_pago

tasa_diaria = (1 + tasa_mensual)**(1/30) - 1
tasa_periodo = (1 + tasa_diaria)**plazo_dias_calc - 1
tasa_atraso_mensual = 0.025
tasa_atraso_diaria = (1 + tasa_atraso_mensual)**(1/30) - 1
interes_atraso = monto_factura * ((1 + tasa_atraso_diaria)**dias_atraso - 1) if dias_atraso > 0 else 0

monto_financiado = monto_factura * (1 - haircut)
monto_retenido = monto_factura * (haircut)
interes = monto_financiado * tasa_periodo
seguro_credito = monto_factura * seguro_credito_rate
seguro_carga = monto_factura * seguro_carga_rate
costo_admin_total = monto_financiado * costo_administracion
gastos_afectos_iva = costo_admin_total + seguro_credito + seguro_carga
iva_total = gastos_afectos_iva * iva
gastos_totales = interes + gastos_afectos_iva + iva_total
monto_a_girar = monto_financiado - gastos_totales
tir_efectiva = ((monto_financiado / monto_a_girar)**(360 / plazo_dias_calc)) - 1 if plazo_dias_calc > 0 and monto_a_girar > 0 else 0

# --- HTML de presentación ---
st.markdown("<h1 style='text-align:center; color:#2C3E50;'>Simulador de Cotización de Financiamiento</h1>", unsafe_allow_html=True)

html = f"""
<div style='max-width: 700px; margin: auto;'>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3> Monto de Factura 💰</h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_factura:,.2f}</div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Producto 📦</h3>
    <div style='font-size: 20px; font-weight: bold;'>{producto} <span style='font-size: 20px; font-weight: normal;'>(haircut: {haircut:.2%})</span></div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Fechas 🗓️</h3>
    <ul style='font-size: 16px; padding-left: 20px;'>
      <li>Otorgamiento: <strong>{fecha_otorgamiento.strftime('%d-%b-%Y')}</strong></li>
      <li>Giro del préstamo: <strong>{fecha_giro_calc.strftime('%d-%b-%Y')}</strong></li>
      <li>Pago esperado: <strong>{fecha_pago_calc.strftime('%d-%b-%Y')}</strong></li>
      <li>Días de financiamiento: <strong>{plazo_dias_calc} días</strong></li>
      <li>Días de atraso: <strong>{dias_atraso} días</strong></li>
    </ul>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Monto Financiado ✂️</h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_financiado:,.2f}</div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 20px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Descuentos 📄</h3>
    <ul style='font-size: 16px; padding-left: 20px;'>
      <li>Intereses ({tasa_mensual*100:.2f}% mensual): <strong>USD ${interes:,.2f}</strong></li>      
      <li>Costo Administrativo: <strong>USD ${costo_admin_total:,.2f}</strong></li>
      <li>Seguro de Crédito: <strong>USD ${seguro_credito:,.2f}</strong></li>
      <li>Seguro de Carga: <strong>USD ${seguro_carga:,.2f}</strong></li>
      <li>IVA (19% sobre costos y seguros): <strong>USD ${iva_total:,.2f}</strong></li>
    </ul>
    <hr>
    <h4 style="font-size: 20px;">Total Descuentos: <strong>USD ${gastos_totales:,.2f}</strong></h4>
  </div>

  <div style='
    background-color: {COLOR_PRINCIPAL};
    padding: 24px;
    border-radius: 15px;
    color: white;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
    <h3>Monto a Girar: </h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_a_girar:,.2f}</div>
    <h3>Intereses Mora: </h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${interes_atraso:,.2f}</div>
    <h3>Monto Retenido - Intereses Mora: </h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_retenido-interes_atraso:,.2f}</div>      
    <h3>TIR Efectiva:</h3>
    <div style='font-size: 24px; font-weight: bold;'> {tir_efectiva*100:.2f}% anual</div> 
    <p style='font-size: 14px;'>* Considerando intereses y costos cobrados por adelantado</p>
  </div>

</div>
"""


st.markdown(html, unsafe_allow_html=True)
