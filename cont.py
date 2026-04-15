import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

st.set_page_config(page_title="Generador UDAL", layout="wide")

st.title("📄 Generador de Contratos UDAL 2026")

# Diccionario con los datos fijos de cada plantel
PLANTELES = {
    "UDAL Online": {
        "nombre": "UNIVERSIDAD DE AMÉRICA LATINA, UDAL ONLINE",
        "domicilio": "17 Poniente 309, Col. El Carmen, Puebla, Pue. (Modalidad a Distancia)"
    },
    "UDAL Puebla": {
        "nombre": "UNIVERSIDAD DE AMÉRICA LATINA, UDAL PUEBLA",
        "domicilio": "17 Poniente 309, Col. El Carmen, Puebla, Pue."
    },
    "UDAL Teziutlán": {
        "nombre": "UDAL PLANTEL TEZIUTLAN O UNIVERSIDAD DE AMÉRICA LATINA PLANTEL TEZIUTLAN",
        "domicilio": "Calle Guerrero No. 401 o Díaz Miron No. 533 Col. Centro Teziutlán, Puebla"
    },
    "UDAL Xalapa": {
        "nombre": "UDAL PLANTEL XALAPA O UNIVERSIDAD DE AMÉRICA LATINA PLANTEL XALAPA",
        "domicilio": "C. Salvador Díaz Mirón 37, Zona Centro, Lomas del Estadio, 91000 Xalapa-Enríquez, Ver."
    }
}

with st.sidebar:
    st.header("Configuración")
    plantel_sel = st.selectbox("Plantel", list(PLANTELES.keys()))
    tipo_contrato = st.radio("Tipo", ["Carga Académica", "Otras Actividades"])
    f_inicio = st.date_input("Fecha Inicio", datetime(2026, 1, 1))
    f_fin = st.date_input("Fecha Fin", datetime(2026, 6, 30))

st.subheader("Datos de Docentes")
archivo = st.file_uploader("Subir CSV", type=["csv"])

lista_maestros = []
if archivo:
    df = pd.read_csv(archivo)
    st.dataframe(df)
    lista_maestros = df.to_dict('records')
else:
    st.info("💡 Generando contrato en blanco (sin datos de maestros).")
    lista_maestros = [{
        "Nombre": "______________________________________",
        "RFC": "___________________",
        "CURP": "___________________",
        "Materias": "______________________________________",
        "Monto": "___________"
    }]

if st.button("🚀 GENERAR DOCUMENTOS"):
    # Selección de plantilla física
    nombre_archivo = "plantilla_carga.docx" if tipo_contrato == "Carga Académica" else "plantilla_otras.docx"
    
    try:
        for m in lista_maestros:
            doc = DocxTemplate(nombre_archivo)
            contexto = {
                "PLANTEL": PLANTELES[plantel_sel]["nombre"],
                "DOMICILIO": PLANTELES[plantel_sel]["domicilio"],
                "NOMBRE_PRESTADOR": m.get("Nombre", "________________"),
                "RFC_PRESTADOR": m.get("RFC", "________________"),
                "CURP_PRESTADOR": m.get("CURP", "________________"),
                "FECHA_INICIO": f_inicio.strftime("%d/%m/%Y"),
                "FECHA_FIN": f_fin.strftime("%d/%m/%Y"),
                "MATERIAS": m.get("Materias", "________________"),
                "MONTO": m.get("Monto", "___________")
            }
            doc.render(contexto)
            output = io.BytesIO()
            doc.save(output)
            
            st.download_button(
                label=f"⬇️ Descargar: {m.get('Nombre')[:15]}",
                data=output.getvalue(),
                file_name=f"Contrato_{plantel_sel}_{m.get('Nombre')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    except Exception as e:
        st.error(f"Error: Asegúrate de que el archivo '{nombre_archivo}' esté en tu GitHub. {e}")
