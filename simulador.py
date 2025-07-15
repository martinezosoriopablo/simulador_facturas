import streamlit as st

# Configuración
st.set_page_config(layout="wide")
COLOR_PRINCIPAL = "#3498DB"

# Sidebar
st.sidebar.header("Parámetros de la Factura")
monto_factura = st.sidebar.number_input("Monto de la factura", min_value=1000.0, value=40000.0)
producto = st.sidebar.selectbox("Producto", [
    "Arándanos", "Uvas", "Bananas", "Enlatados", "Aceite", 
    "Aguacate", "Congelados", "Harina", "Polipropileno", "Cerezas"
])
haircuts = {
    "Arándanos": 0.25, "Uvas": 0.25, "Bananas": 0.25, "Enlatados": 0.10, "Aceite": 0.15,
    "Aguacate": 0.20, "Congelados": 0.15, "Harina": 0.10, "Polipropileno": 0.10, "Cerezas": 0.25
}
haircut = haircuts[producto]
riesgo = st.sidebar.selectbox("Clasificación de riesgo", ["A", "B", "C"])
tasas_mensuales = {"A": 0.009, "B": 0.012, "C": 0.015}
tasa_mensual = tasas_mensuales[riesgo]
plazo_dias = st.sidebar.slider("Plazo en días", 30, 180, 60)
dias_atraso = st.sidebar.slider("Días de atraso", 0, 60, 0)
costo_administracion = st.sidebar.number_input("Costo administrativo ($)", 0.0, value=0.20) / 100
seguro_credito_rate = st.sidebar.number_input("Seguro de crédito (%)", 0.0, value=0.35) / 100
seguro_carga_rate = st.sidebar.number_input("Seguro de carga (%)", 0.0, value=0.10) / 100
iva = 0.19

# Cálculos
tasa_diaria = (1 + tasa_mensual)**(1/30) - 1
tasa_periodo = (1 + tasa_diaria)**plazo_dias - 1
tasa_atraso_mensual = 0.025
tasa_atraso_diaria = (1 + tasa_atraso_mensual)**(1/30) - 1
interes_atraso = monto_factura * ((1 + tasa_atraso_diaria)**dias_atraso - 1) if dias_atraso > 0 else 0
monto_financiado = monto_factura * (1 - haircut)
interes = monto_financiado * tasa_periodo
seguro_credito = monto_factura * seguro_credito_rate
seguro_carga = monto_factura * seguro_carga_rate
costo_administrativo = monto_financiado*costo_administracion
gastos_afectos_iva = costo_administrativo + seguro_credito + seguro_carga
iva_total = gastos_afectos_iva * iva
gastos_totales = interes + interes_atraso + gastos_afectos_iva + iva_total
monto_a_girar = monto_financiado - gastos_totales
tir_efectiva = ((monto_financiado / monto_a_girar)**(360 / plazo_dias)) - 1

# Mostrar resultado
st.markdown("<h1 style='text-align:center; color:#2C3E50;'>Simulador de Cotización de Financiamiento</h1>", unsafe_allow_html=True)

html = f"""
<div style='max-width: 700px; margin: auto;'>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3> Monto de Factura 💰</h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_factura:,.2f}</div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Producto 📦</h3>
    <div style='font-size: 20px; font-weight: bold;'>{producto} <span style='font-size: 20px; font-weight: normal;'>(haircut: {haircut:.0%})</span></div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Monto Financiado ✂️</h3>
    <div style='font-size: 24px; font-weight: bold;'>USD ${monto_financiado:,.2f}</div>
  </div>

  <div style="border: 2px solid {COLOR_PRINCIPAL}; padding: 20px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3>Descuentos 📄</h3>
    <ul style='font-size: 16px; padding-left: 20px;'>
    <li>Intereses ({tasa_mensual*100:.2f}% mensual): <strong>USD ${interes:,.2f}</strong></li>
    <li>Intereses por atraso (2.50% mensual): <strong>USD ${interes_atraso:,.2f}</strong></li>
    <li>Costo Administrativo: <strong>USD ${costo_administrativo:,.2f}</strong></li>
    <li>Seguro de Crédito: <strong>USD ${seguro_credito:,.2f}</strong></li>
    <li>Seguro de Carga: <strong>USD ${seguro_carga:,.2f}</strong></li>
    <li>IVA (19% sobre costos y seguros): <strong>USD ${iva_total:,.2f}</strong></li>
    </ul>
    <hr>
    <h4 style="font-size: 20px;">Total Descuentos: <strong>USD ${gastos_totales:,.2f}</strong></h4>
  </div>

  <div style='
    background-color: {COLOR_PRINCIPAL};
    padding: 30px;
    border-radius: 15px;
    color: white;
    text-align: left;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
    <h2>Monto a Girar:USD ${monto_a_girar:,.2f}</h2>
    <h3>TIR Efectiva: {tir_efectiva*100:.2f}% anual</h3>
    <p style='font-size: 14px;'>* Considerando intereses y costos cobrados por adelantado</p>
  </div>

</div>
"""




st.markdown(html, unsafe_allow_html=True)
