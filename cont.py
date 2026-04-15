import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

st.set_page_config(page_title="UDAL - Generador de Contratos", layout="wide")

st.title("📄 Generador de Contratos UDAL 2026")

# Configuración de los datos fijos por plantel
DATOS_PLANTELES = {
    "UDAL Online": {"file": "PLANTILLA_ONLINE.docx"},
    "UDAL Puebla": {"file": "PLANTILLA_PUEBLA.docx"},
    "UDAL Teziutlán": {"file": "PLANTILLA_TEZIUTLAN.docx"},
    "UDAL Xalapa": {"file": "PLANTILLA_XALAPA.docx"}
}

with st.sidebar:
    st.header("1. Configuración")
    plantel_sel = st.selectbox("Seleccionar Plantel", list(DATOS_PLANTELES.keys()))
    fecha_ini = st.date_input("Fecha Inicio", datetime(2026, 1, 1))
    fecha_fin = st.date_input("Fecha Fin", datetime(2026, 6, 30))

st.subheader("2. Entrada de Datos")
tab1, tab2 = st.tabs(["Carga Masiva (CSV)", "Entrada Manual"])

lista_docentes = []

with tab1:
    archivo_csv = st.file_uploader("Subir CSV (Nombre, RFC, CURP, Materias, Monto)", type=["csv"])
    if archivo_csv:
        df = pd.read_csv(archivo_csv)
        st.write("Vista previa de datos cargados:")
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
            materias = st.text_area("Materias o Actividades")
            if st.form_submit_button("Añadir a la lista"):
                lista_docentes.append({"Nombre": nombre, "RFC": rfc, "CURP": curp, "Materias": materias, "Monto": monto})

st.divider()

# SI LA LISTA ESTÁ VACÍA, CREAMOS UN DOCENTE "EN BLANCO" PARA QUE EL BOTÓN FUNCIONE
if not lista_docentes:
    st.info("💡 No has ingresado datos. Al hacer clic en el botón, se generará un contrato con espacios en blanco para llenar a mano.")
    docente_en_blanco = {
        "Nombre": "______________________________________",
        "RFC": "___________________",
        "CURP": "___________________",
        "Materias": "______________________________________",
        "Monto": "___________"
    }
    lista_para_procesar = [docente_en_blanco]
else:
    lista_para_procesar = lista_docentes

if st.button("🚀 GENERAR CONTRATOS"):
    template_path = DATOS_PLANTELES[plantel_sel]["file"]
    
    try:
        for d in lista_para_procesar:
            doc = DocxTemplate(template_path)
            context = {
                "NOMBRE_PRESTADOR": d.get("Nombre") or "________________",
                "RFC_PRESTADOR": d.get("RFC") or "________________",
                "CURP_PRESTADOR": d.get("CURP") or "________________",
                "FECHA_INICIO": fecha_ini.strftime("%d/%m/%Y"),
                "FECHA_FIN": fecha_fin.strftime("%d/%m/%Y"),
                "MATERIAS": d.get("Materias") or "________________",
                "MONTO": d.get("Monto") or "___________"
            }
            doc.render(context)
            
            output = io.BytesIO()
            doc.save(output)
            
            st.download_button(
                label=f"⬇️ Descargar Contrato: {d.get('Nombre')[:20]}...",
                data=output.getvalue(),
                file_name=f"Contrato_{plantel_sel}_{d.get('Nombre')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        st.success("¡Documentos generados!")
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo '{template_path}'. Asegúrate de haberlo subido a tu GitHub con ese nombre exacto.")
