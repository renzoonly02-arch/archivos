import os
import streamlit as st
import mammoth
import zipfile
import io
import pdfplumber

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SISTEMA DE DOCUMENTOS - PLANTA",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ZIP_DOCUMENTOS = os.path.join(CARPETA_ACTUAL, "DOCUMENTOS.zip")

# --- ESTILOS CSS REFORZADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1b2a !important; color: #ffffff !important; }
    [data-testid="stSidebar"] { background-color: #1b263b !important; border-right: 1px solid #415a77; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label { color: #ffffff !important; }
    .stButton > button {
        background-color: #1e293b !important; color: #e2e8f0 !important;
        border: 1px solid #415a77 !important; text-align: left !important;
        display: block !important; width: 100% !important; padding: 10px !important;
        font-size: 13px !important; white-space: normal !important;
        word-wrap: break-word !important; border-radius: 6px !important;
    }
    .stButton > button:hover { border-color: #38bdf8 !important; background-color: #0f172a !important; color: #38bdf8 !important; }
    .banner-principal { background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 25px; border-radius: 15px; margin-bottom: 25px; }
    .contenedor-vista-previa {
        background-color: #ffffff !important; color: #1e293b !important;
        padding: 30px; border-radius: 10px; border: 3px solid #3b82f6;
        min-height: 500px; font-family: 'Segoe UI', sans-serif; margin-top: 15px;
    }
    .contenedor-vista-previa h1, .contenedor-vista-previa h2, .contenedor-vista-previa h3 { color: #0f172a !important; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; }
    .contenedor-vista-previa p, .contenedor-vista-previa li, .contenedor-vista-previa td, .contenedor-vista-previa tr { font-size: 16px !important; line-height: 1.6 !important; color: #1e293b !important; }
    .contenedor-vista-previa table { border-collapse: collapse; width: 100%; margin-top: 15px; }
    .contenedor-vista-previa th, .contenedor-vista-previa td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
    </style>
""", unsafe_allow_html=True)

if "archivo_activo_zip" not in st.session_state:
    st.session_state.archivo_activo_zip = None

# --- ESCANEO AUTOMÁTICO DE WORD Y PDF DENTRO DEL ZIP ---
diccionario_archivos = {}
subcarpetas_detectadas = ["Todas"]

if os.path.exists(ZIP_DOCUMENTOS):
    try:
        with zipfile.ZipFile(ZIP_DOCUMENTOS, 'r') as archive:
            for zfile in archive.namelist():
                es_valido = zfile.lower().endswith(('.docx', '.pdf'))
                if es_valido and not os.path.basename(zfile).startswith('.') and not os.path.basename(zfile).startswith('~$'):
                    partes = zfile.split('/')
                    if len(partes) > 2:
                        nombre_carpeta = partes[-2]
                    else:
                        nombre_carpeta = "Raíz (Archivos Sueltos)"
                    
                    if nombre_carpeta not in subcarpetas_detectadas:
                        subcarpetas_detectadas.append(nombre_carpeta)
                        
                    if nombre_carpeta not in diccionario_archivos:
                        diccionario_archivos[nombre_carpeta] = []
                        
                    diccionario_archivos[nombre_carpeta].append({
                        "nombre": os.path.basename(zfile),
                        "ruta_zip": zfile
                    })
    except Exception as e:
        st.sidebar.error(f"Error al abrir el paquete ZIP: {str(e)}")

# --- 1. PANEL LATERAL IZQUIERDO ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; margin-bottom:0;'>SISTEMA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#94a3b8; text-align:center; margin-top:0;'>ÍNDICE GENERAL DE DOCUMENTOS</p>", unsafe_allow_html=True)
    st.write("---")
    
    st.markdown("### 📂 SELECCIONAR CARPETA INTERNA")
    carpeta_seleccionada = st.selectbox("Filtrar por carpeta:", subcarpetas_detectadas, label_visibility="collapsed")
    st.write("---")
    
    buscar = st.text_input("🔍 Buscar por palabra clave:", placeholder="Escribe aquí...")
    st.write("---")
    
    archivos_mostrar = []
    for carp, lista_arch in diccionario_archivos.items():
        if carpeta_seleccionada == "Todas" or carpeta_seleccionada == carp:
            for item in lista_arch:
                if not buscar or buscar.strip().lower() in item["nombre"].lower():
                    archivos_mostrar.append(item)
                    
    archivos_mostrar.sort(key=lambda x: x["nombre"])

    st.markdown(f"### 📄 DOCUMENTOS ENCONTRADOS ({len(archivos_mostrar)})")
    for item in archivos_mostrar:
        icono = "📕 " if item["nombre"].lower().endswith('.pdf') else "📄 "
        marca = "▶️ " if st.session_state.archivo_activo_zip == item["ruta_zip"] else icono
        if st.button(f"{marca}{item['nombre']}", key=f"btn_zip_{item['ruta_zip']}", use_container_width=True):
            st.session_state.archivo_activo_zip = item["ruta_zip"]
            st.rerun()

# --- 2. ÁREA PRINCIPAL ---
st.markdown("""
    <div class="banner-principal">
        <span style="background-color:#ffffff; color:#1e3a8a; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold;">📌 GESTIÓN DE ARCHIVOS</span>
        <h1 style="color:white; margin-top:10px; margin-bottom:0; font-size:32px;">Buscador y Visor Integrado de Documentos</h1>
        <p style="color:#e0e1dd; margin-top:5px; font-size:14px;">Explora las subcarpetas de forma automatizada desde el panel lateral.</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.archivo_activo_zip and os.path.exists(ZIP_DOCUMENTOS):
    ruta_interna = st.session_state.archivo_activo_zip
    nombre_archivo = os.path.basename(ruta_interna)
    
    st.markdown(f"<h3 style='color: #38bdf8;'>👁️ Vista Previa de: <span style='color: white;'>{nombre_archivo}</span></h3>", unsafe_allow_html=True)
    
    try:
        with zipfile.ZipFile(ZIP_DOCUMENTOS, 'r') as archive:
            with archive.open(ruta_interna) as file_data:
                contenido_binario = file_data.read()
                
                # --- VISTA PREVIA PARA WORD (.DOCX) ---
                if ruta_interna.lower().endswith('.docx'):
                    bytes_io = io.BytesIO(contenido_binario)
                    resultado = mammoth.convert_to_html(bytes_io, ignore_empty_paragraphs=True)
                    html_contenido = resultado.value
                    html_contenido = html_contenido.replace("<li>1. ", "<li style='list-style-type: none; margin-left: -15px;'>🔹 <b>")
                    
                    st.markdown(f"""
                        <div class="contenedor-vista-previa">
                            {html_contenido}
                        </div>
                    """, unsafe_allow_html=True)
                
                # --- VISTA PREVIA PARA PDF (.PDF) PROCESADA EN LÍNEA DE FORMA NATIVA ---
                elif ruta_interna.lower().endswith('.pdf'):
                    bytes_io = io.BytesIO(contenido_binario)
                    
                    with pdfplumber.open(bytes_io) as pdf:
                        texto_pdf = ""
                        for num_pag, pagina in enumerate(pdf.pages):
                            texto_pdf += f"📝 --- PÁGINA {num_pag + 1} ---\n\n"
                            texto_pdf += (pagina.extract_text() or "[Esta página contiene una imagen o escaneo plano]") + "\n\n"
                    
                    st.markdown(f"""
                        <div class="contenedor-vista-previa" style="white-space: pre-wrap; overflow-y: auto; max-height: 700px; font-family: 'Segoe UI', sans-serif;">
                            {texto_pdf}
                        </div>
                    """, unsafe_allow_html=True)
                    
    except Exception as err_lectura:
        st.error(f"No se pudo cargar la vista previa: {str(err_lectura)}")
else:
    st.info("👈 Selecciona cualquier documento (Word o PDF) de la lista de la izquierda para iniciar la vista previa en pantalla.")
