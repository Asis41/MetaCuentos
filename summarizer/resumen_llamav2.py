import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token desde las variables de entorno
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Asegurarse de que el token fue cargado correctamente
if not HUGGINGFACEHUB_API_TOKEN:
    raise ValueError("El token de Hugging Face no se ha encontrado en las variables de entorno.")

# Definir el template del prompt con el nuevo contenido
template = """Basándote de la siguiente noticia, crea un resumen fácil de entender para un niño de entre 6 a 12 años.
El resumen debe ser claro y educativo. Asegúrate de cumplir estos aspectos en el resumen:

1. Usa lenguaje sencillo que los niños puedan entender.
2. Explica el tema de una manera que un niño pueda imaginar lo que está pasando.
3. Destaca por qué este tema es importante.
4. Incluye un dato interesante para que los niños puedan entender mejor el tema.
5. Evita repetir información innecesaria y asegúrate de que el resumen sea directo, sin complicar demasiado los hechos.

IMPORTANTE: Todos estos aspectos respondelos dentro del resumen de la noticia.

Noticia:
{text}

Resumen educativo para niños:
"""
prompt = PromptTemplate.from_template(template)

# Definir el modelo (meta-llama/Llama-3.2-3B-Instruct)
repo_id = "meta-llama/Llama-3.2-1B-Instruct"

# Configurar el endpoint de Hugging Face
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.1,
    top_p=0.95,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
)

# Crear la cadena (pipeline) LLM
llm_chain = prompt | llm

# Leer el contenido del archivo .txt
ruta_archivo = 'documents/resultadosscraping20241020_000223.txt'  # Reemplaza con la ruta real de tu archivo
with open(ruta_archivo, 'r', encoding='utf-8') as file:
    text_content = file.read()

# Ejecutar la cadena y obtener la respuesta
response = llm_chain.invoke({"text": text_content})

# Crear la carpeta 'stories' si no existe
ruta_carpeta = 'stories'
if not os.path.exists(ruta_carpeta):
    os.makedirs(ruta_carpeta)

# Obtener el nombre base del archivo original
nombre_archivo = os.path.basename(ruta_archivo)
nombre_base, extension = os.path.splitext(nombre_archivo)

# Definir la ruta del archivo de salida
ruta_salida = os.path.join(ruta_carpeta, f"{nombre_base}_resumen.txt")

# Guardar la respuesta en el archivo de salida
with open(ruta_salida, 'w', encoding='utf-8') as file:
    file.write(response)

print(f"El resumen se ha guardado en: {ruta_salida}")