import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors, pagesizes
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ----------------------------
# CONFIGURAZIONE PAGINA
# ----------------------------
st.set_page_config(
    page_title="Analizzatore Parametri Clinici",
    page_icon="🩺",
    layout="wide"
)

# ----------------------------
# STILE MODERNO DARK MEDICAL
# ----------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.metric-card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
}
h1, h2, h3, h4, h5, h6, p, div {
    color: white !important;
}
.stDataFrame {
    background-color: #1e293b;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# TITOLO
# ----------------------------
st.title("🩺 Analizzatore Parametri Clinici")
st.markdown("Sistema di analisi parametri clinici con riferimento a range standard internazionali.")

# ----------------------------
# DISCLAIMER
# ----------------------------
st.warning("""
⚠️ Questo software ha esclusivamente scopo informativo ed educativo.
Non sostituisce una valutazione medica professionale.
Consultare sempre un medico per interpretazioni cliniche ufficiali.
""")

# ----------------------------
# INPUT PAZIENTE
# ----------------------------
st.sidebar.header("Dati Paziente")

eta = st.sidebar.number_input("Età", 0, 120, 30)
sesso = st.sidebar.selectbox("Sesso", ["Maschio", "Femmina"])
peso = st.sidebar.number_input("Peso (kg)", 30.0, 250.0, 70.0)
altezza = st.sidebar.number_input("Altezza (cm)", 100.0, 220.0, 170.0)
pressione_sistolica = st.sidebar.number_input("Pressione Sistolica (mmHg)", 80, 250, 120)
pressione_diastolica = st.sidebar.number_input("Pressione Diastolica (mmHg)", 40, 150, 80)
frequenza_cardiaca = st.sidebar.number_input("Frequenza Cardiaca (bpm)", 30, 200, 70)
temperatura = st.sidebar.number_input("Temperatura Corporea (°C)", 34.0, 42.0, 36.5)

# ----------------------------
# CALCOLI BMI
# ----------------------------
altezza_m = altezza / 100
bmi = peso / (altezza_m ** 2)

def classifica_bmi(val):
    if val < 18.5:
        return "Sottopeso"
    elif 18.5 <= val < 25:
        return "Normopeso"
    elif 25 <= val < 30:
        return "Sovrappeso"
    else:
        return "Obesità"

categoria_bmi = classifica_bmi(bmi)

# ----------------------------
# METRICHE PRINCIPALI
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("BMI", f"{bmi:.2f}", categoria_bmi)

with col2:
    st.metric("Pressione", f"{pressione_sistolica}/{pressione_diastolica} mmHg")

with col3:
    st.metric("Frequenza Cardiaca", f"{frequenza_cardiaca} bpm")

# ----------------------------
# VALUTAZIONE RANGE
# ----------------------------
st.subheader("Valutazione Parametri")

def valuta_range(val, min_val, max_val):
    if val < min_val:
        return "Basso"
    elif val > max_val:
        return "Alto"
    else:
        return "Normale"

valutazioni = {
    "BMI": categoria_bmi,
    "Pressione Sistolica": valuta_range(pressione_sistolica, 90, 120),
    "Pressione Diastolica": valuta_range(pressione_diastolica, 60, 80),
    "Frequenza Cardiaca": valuta_range(frequenza_cardiaca, 60, 100),
    "Temperatura": valuta_range(temperatura, 36.1, 37.2),
}

df_valutazioni = pd.DataFrame(valutazioni.items(), columns=["Parametro", "Valutazione"])
st.dataframe(df_valutazioni, use_container_width=True)

# ----------------------------
# GRAFICO BMI GAUGE
# ----------------------------
st.subheader("Distribuzione BMI")

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=bmi,
    title={'text': "BMI"},
    gauge={
        'axis': {'range': [0, 40]},
        'steps': [
            {'range': [0, 18.5], 'color': "#60a5fa"},
            {'range': [18.5, 25], 'color': "#22c55e"},
            {'range': [25, 30], 'color': "#facc15"},
            {'range': [30, 40], 'color': "#ef4444"},
        ],
    }
))

fig.update_layout(
    paper_bgcolor="#0f172a",
    font={'color': "white"}
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# INTERPRETAZIONE
# ----------------------------
st.subheader("Interpretazione Informativa")

st.markdown(f"""
- **BMI:** {bmi:.2f} → {categoria_bmi}  
- **Pressione Arteriosa:** {pressione_sistolica}/{pressione_diastolica} mmHg  
- **Frequenza Cardiaca:** {frequenza_cardiaca} bpm  
- **Temperatura:** {temperatura} °C  

I valori sono confrontati con range clinici generali utilizzati nella pratica medica internazionale.
Eventuali anomalie devono essere valutate da un professionista sanitario qualificato.
""")

# ----------------------------
# FUNZIONE PDF
# ----------------------------
def genera_pdf_report():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(
        temp_file.name,
        pagesize=pagesizes.A4,
        title="Analizzatore Parametri Clinici",
        author="Gabriele Boscarello"
    )

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Analizzatore Parametri Clinici", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Autore: Gabriele Boscarello", styles["Normal"]))
    elements.append(Paragraph(f"Data generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    dati_tabella = [
        ["Parametro", "Valore"],
        ["Età", eta],
        ["Sesso", sesso],
        ["Peso (kg)", peso],
        ["Altezza (cm)", altezza],
        ["BMI", f"{bmi:.2f} ({categoria_bmi})"],
        ["Pressione", f"{pressione_sistolica}/{pressione_diastolica} mmHg"],
        ["Frequenza Cardiaca", f"{frequenza_cardiaca} bpm"],
        ["Temperatura", f"{temperatura} °C"]
    ]

    tabella = Table(dati_tabella)
    tabella.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(tabella)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(
        "Disclaimer: Documento generato a scopo informativo. Non sostituisce valutazione medica professionale.",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("© 2026 Gabriele Boscarello - Clinical Metrics Analyzer", styles["Normal"]))

    doc.build(elements)

    return temp_file.name

# ----------------------------
# ESPORTAZIONE PDF
# ----------------------------
st.subheader("Esporta Report PDF")

if st.button("Genera PDF Report"):
    file_pdf = genera_pdf_report()
    with open(file_pdf, "rb") as f:
        st.download_button(
            label="Scarica Report PDF",
            data=f,
            file_name="clinical_report.pdf",
            mime="application/pdf"
        )