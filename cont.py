import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

st.set_page_config(page_title="UDAL - Generador de Contratos", layout="centered")

st.title("📄 Generador de Contratos UDAL 2026")
st.markdown("Genera contratos de forma individual o masiva con base en las plantillas oficiales.")

# --- CONFIGURACIÓN DE PLANTEL ---
DATOS_PLANTELES = {
    "UDAL Online": {
        "denominacion": "UNIVERSIDAD DE AMÉRICA LATINA, UDAL ONLINE",
        "domicilio": "17 Poniente 309, Col. El Carmen, Puebla, Pue. (Modalidad a Distancia)"
    },
    "UDAL Puebla": {
        "denominacion": "UNIVERSIDAD DE AMÉRICA LATINA, UDAL PUEBLA",
        "domicilio": "17 Poniente 309, Col. El Carmen, Puebla, Pue."
    },
    "UDAL Teziutlán": {
        "denominacion": "UDAL PLANTEL TEZIUTLAN O UNIVERSIDAD DE AMÉRICA LATINA PLANTEL TEZIUTLAN",
        "domicilio": "Calle Guerrero No. 401 o Díaz Miron No. 533 Col. Centro Teziutlán, Puebla"
    },
    "UDAL Xalapa": {
        "denominacion": "UDAL PLANTEL XALAPA O UNIVERSIDAD DE AMÉRICA LATINA PLANTEL XALAPA",
        "domicilio": "C. Salvador Díaz Mirón 37, Zona Centro, Lomas del Estadio, 91000 Xalapa-Enríquez, Ver."
    }
}

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("Configuración")
    plantel_sel = st.selectbox("Seleccionar Plantel", list(DATOS_PLANTELES.keys()))
    tipo_doc = st.radio("Tipo de Contrato", ["Carga Académica", "Otras Actividades"])
    fecha_ini = st.date_input("Fecha Inicio", datetime(2026, 1, 1))
    fecha_fin = st.date_input("Fecha Fin", datetime(2026, 6, 30))

st.subheader("Entrada de Datos")
tab1, tab2 = st.tabs(["Carga Masiva (CSV)", "Entrada Manual"])

lista_docentes = []

with tab1:
    archivo_csv = st.file_uploader("Subir CSV de Docentes (Columnas: Nombre, RFC, CURP, Materias, Monto)", type=["csv"])
    if archivo_csv:
        df = pd.read_csv(archivo_csv)
        st.dataframe(df)
        lista_docentes = df.to_dict('records')

with tab2:
    if not lista_docentes:
        with st.form("manual_form"):
            col1, col2 = st.columns(2)
            nombre = col1.text_input("Nombre Completo")
            rfc = col2.text_input("RFC")
            curp = col1.text_input("CURP")
            monto = col2.text_input("Monto/Honorarios")
            materias = st.text_area("Materias / Actividades")
            if st.form_submit_button("Añadir Docente"):
                lista_docentes.append({
                    "Nombre": nombre, "RFC": rfc, "CURP": curp, 
                    "Materias": materias, "Monto": monto
                })

# --- GENERACIÓN ---
if st.button("🚀 Generar y Descargar Contratos"):
    if not lista_docentes:
        st.warning("No hay datos de docentes para procesar.")
    else:
        # Aquí cargarías el archivo .docx que descargaste de Drive
        template_name = "plantilla_carga.docx" if tipo_doc == "Carga Académica" else "plantilla_otras.docx"
        
        for docen in lista_docentes:
            doc = DocxTemplate(template_name)
            context = {
                "PLANTEL": DATOS_PLANTELES[plantel_sel]["denominacion"],
                "DOMICILIO": DATOS_PLANTELES[plantel_sel]["domicilio"],
                "NOMBRE_PRESTADOR": docen.get("Nombre", "________________"),
                "RFC_PRESTADOR": docen.get("RFC", "________________"),
                "CURP_PRESTADOR": docen.get("CURP", "________________"),
                "FECHA_INICIO": fecha_ini.strftime("%d/%m/%Y"),
                "FECHA_FIN": fecha_fin.strftime("%d/%m/%Y"),
                "MATERIAS": docen.get("Materias", ""),
                "MONTO": docen.get("Monto", "")
            }
            doc.render(context)
            
            output = io.BytesIO()
            doc.save(output)
            st.download_button(
                label=f"⬇️ Descargar Contrato - {docen.get('Nombre')}",
                data=output.getvalue(),
                file_name=f"Contrato_{plantel_sel}_{docen.get('Nombre')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )