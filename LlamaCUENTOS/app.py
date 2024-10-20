from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging  # Para agregar registros en consola
import json

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()

# Obtener el token de Hugging Face
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACEHUB_API_TOKEN:
    raise ValueError("El token de Hugging Face no se ha encontrado en las variables de entorno.")

# Configurar el modelo de lenguaje de Hugging Face
repo_id = "meta-llama/Llama-3.2-3B-Instruct"
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    temperature=0.7,
    top_p=0.95,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
)

# Función para extraer el texto de una URL
# Función para limpiar el texto
def limpiar_texto(texto):
    # Eliminar espacios en blanco extra y saltos de línea
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Función para extraer el texto de una URL específica
def extraer_texto_de_url(url):
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # Crear objeto BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Determinar el tipo de URL y aplicar la función adecuada
        if url.startswith('https://elpais.com/'):
            texto = extraer_texto_elpais(soup)
        elif url.startswith('https://www.nationalgeographicla.com/'):
            texto = extraer_texto_natgeo(soup)
        else:
            texto = extraer_texto_generico(soup)

        # Limpiar el texto extraído
        texto_limpio = limpiar_texto(texto)
        return texto_limpio

    except requests.RequestException as e:
        return f"Error al procesar {url}: {str(e)}"

# Funciones para extraer el contenido de El País y National Geographic
def extraer_texto_elpais(soup):
    texto = ''
    article = soup.find('article')
    if article:
        header = article.select_one('header')
        if header:
            h1 = header.select_one('h1')
            h2 = header.select_one('h2')
            if h1:
                texto += h1.get_text(separator=' ', strip=True) + '\n\n'
            if h2:
                texto += h2.get_text(separator=' ', strip=True) + '\n\n'
        div_cuerpo = article.find('div', attrs={'data-dtm-region': 'articulo_cuerpo'})
        if div_cuerpo:
            for elemento in div_cuerpo.find_all(['p', 'h3']):
                texto += elemento.get_text(separator=' ', strip=True) + '\n\n'
    else:
        texto = 'No se encontró el artículo.'
    return texto

def extraer_texto_natgeo(soup):
    texto = ''
    titulo = soup.select_one('h1.css-1lncn9l')
    if titulo:
        texto += titulo.get_text(separator=' ', strip=True) + '\n\n'
    parrafos = soup.select('div.paragraph.css-1vtiyti')
    if parrafos:
        for parrafo in parrafos:
            texto_parrafo = parrafo.get_text(separator=' ', strip=True)
            if texto_parrafo:
                texto += texto_parrafo + '\n\n'
    else:
        texto += 'No se encontraron párrafos.\n\n'
    return texto

# Para otras URLs
def extraer_texto_generico(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()

# Función para guardar los resultados del scraping en un archivo
def guardar_resultados_en_archivo(url, texto):
    carpeta = 'documents'
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Usamos un nombre fijo para el archivo
    nombre_archivo = "resultado_scraping.txt"
    ruta_completa = os.path.join(carpeta, nombre_archivo)

    with open(ruta_completa, 'w', encoding='utf-8') as file:
        file.write(f"Texto extraído de {url}:\n")
        file.write(texto)
        file.write("\n\n" + "="*50 + "\n\n")

    logging.info(f'Archivo guardado en: {ruta_completa}')
    return ruta_completa

# Función para generar el resumen
def create_summary(text):
# Definir el template del prompt con el nuevo contenido
    template = """Basándote en la siguiente información, crea un resumen en 60 palabras, fácil de entender para un niño de entre 6 a 12 años.
    El resumen debe ser claro y educativo. Asegúrate de cumplir estos aspectos en el resumen:

    1. Usa lenguaje sencillo que los niños puedan entender.
    2. Explica el tema de una manera que un niño pueda visualizar lo que está pasando.
    3. Destaca por qué este tema es importante.
    4. Incluye un dato interesante para que los niños puedan entender mejor el tema, a manera de SABIAS QUE... solo una vez.
    5. Evita repetir información innecesaria y asegúrate de que el resumen sea directo, sin complicar demasiado los hechos.

    Información:
    {text}

    Resumen educativo para niños:
    """

    prompt = PromptTemplate.from_template(template)

    # Definir el modelo de Hugging Face
    repo_id = "meta-llama/Llama-3.2-3B-Instruct"
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        temperature=0.1,  # Baja temperatura para respuestas más concisas
        top_p=0.95,
        max_length=50,  # Limita el tamaño de la respuesta
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

    # Crear la cadena (pipeline) LLM
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Ejecutar la cadena y obtener la respuesta
    response = llm_chain.invoke({"text": text})

    if 'text' in response:
        return response['text']
    else:
        logging.error(f"Respuesta de la API no contiene 'text': {response}")
        return "Error: No se pudo generar el resumen correctamente."

# Ruta para hacer scraping y guardar en archivo
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')

    if url:
        # Realizamos el scraping
        logging.info(f'Scraping la URL: {url}')
        texto = extraer_texto_de_url(url)

        # Guardamos el resultado en un archivo con nombre fijo
        ruta_archivo = guardar_resultados_en_archivo(url, texto)

        logging.info(f'Archivo generado en: {ruta_archivo}')
        return jsonify({'archivo_txt': ruta_archivo}), 200
    else:
        return jsonify({'error': 'URL no proporcionada'}), 400

# Nueva ruta para leer el archivo generado por scrape y crear resumen
@app.route('/resumen', methods=['POST'])
def resumen():
    # Usamos la ruta fija del archivo generado por /scrape
    archivo_txt = 'documents/resultado_scraping.txt'

    logging.info(f'Archivo solicitado para resumen: {archivo_txt}')

    if not archivo_txt or not os.path.exists(archivo_txt):
        logging.error(f'Archivo no encontrado: {archivo_txt}')
        return jsonify({'error': 'Archivo .txt no encontrado'}), 400

    # Leer el contenido del archivo .txt
    with open(archivo_txt, 'r', encoding='utf-8') as file:
        texto = file.read()

    logging.info(f'Contenido del archivo leído correctamente: {archivo_txt}')

    # Procesar el texto y generar el resumen
    resultado = create_summary(texto)

    logging.info('Resumen generado correctamente')

    # Devolver solo el resumen generado
    return jsonify({'resumen': resultado}), 200


# Nueva ruta para generar villanos basados en el resumen
@app.route('/villanos', methods=['POST'])
def villanos():
    # Recibir el resumen generado desde el frontend
    resumen = request.json.get('resumen')

    if not resumen:
        return jsonify({'error': 'Resumen no proporcionado'}), 400

    # Definir el prompt para generar los villanos
    template = """
    Eres un generador de villanos para cuentos infantiles enfocados en ecología, adecuados para niños de entre 6 y 12 años, y no debes generarles pesadillas.

    Dado el siguiente resumen:

    {resumen}

    Genera cinco posibles villanos causantes del problema descrito en el contexto.

    IMPORTANTE: La respuesta debes darla UNICAMENTE con cinco posibles nombres de personajes causantes del problema, siguiendo la estructura:

    1) **Nombre del Personaje 1**: (Habilidades del personaje en relación con la causa del problema)
    2) **Nombre del Personaje 2**: (Habilidades del personaje en relación con la causa del problema, diferentes a las de Personaje 1)
    3) **Nombre del Personaje 3**: (Habilidades del personaje en relación con la causa del problema, diferentes a las de Personajes 1 y 2)
    4) **Nombre del Personaje 4**: (Habilidades del personaje en relación con la causa del problema, diferentes a las de Personajes 1, 2 y 3)
    5) **Nombre del Personaje 5**: (Habilidades del personaje en relación con la causa del problema, diferentes a las de Personajes 1, 2, 3 y 4)

    Recuerda que los personajes deben ser apropiados para niños y no causarles miedo.

    Respuesta:
    """

    # Crear el template del prompt
    prompt = PromptTemplate.from_template(template)

    # Configurar el modelo de Hugging Face
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.2-3B-Instruct",
        temperature=0.7,
        top_p=0.9,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

    # Crear la cadena (pipeline) LLM
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Ejecutar la cadena para generar los villanos
    response = llm_chain.invoke({"resumen": resumen})

    # Verificar si la respuesta contiene 'text'
    if 'text' in response:
        return jsonify({'villanos': response['text']}), 200
    else:
        logging.error(f"Error al generar villanos: {response}")
        return jsonify({'error': 'No se pudo generar villanos correctamente.'}), 500
    
    
# Nueva ruta para generar héroes basados en el resumen y el villano seleccionado
@app.route('/heroes', methods=['POST'])
def heroes():
    # Recibir el resumen y el villano seleccionado desde el frontend
    data = request.json
    resumen = data.get('resumen')
    villano = data.get('villano')

    if not resumen or not villano:
        return jsonify({'error': 'Resumen o villano no proporcionados'}), 400

    # Definir el prompt para generar héroes
    template = """
    Eres un generador de héroes para cuentos infantiles enfocados en ecología, adecuados para niños de entre 6 y 12 años.

    Dado el siguiente resumen del problema:

    {resumen}

    Y el villano seleccionado:

    {villano}

    Genera cinco posibles héroes que podrían enfrentar al villano. Cada héroe debe tener habilidades únicas, relacionadas con la causa del problema. Sigue la estructura:

    1) **Nombre del Héroe 1**: (Habilidades del héroe en relación con el villano y la causa del problema)
    2) **Nombre del Héroe 2**: (Habilidades del héroe en relación con el villano y la causa del problema, diferentes a las de Héroe 1)
    3) **Nombre del Héroe 3**: (Habilidades del héroe en relación con el villano y la causa del problema, diferentes a las de Héroes 1 y 2)
    4) **Nombre del Héroe 4**: (Habilidades del héroe en relación con el villano y la causa del problema, diferentes a las de Héroes 1, 2 y 3)
    5) **Nombre del Héroe 5**: (Habilidades del héroe en relación con el villano y la causa del problema, diferentes a las de Héroes 1, 2, 3 y 4)

    Recuerda que los héroes deben ser apropiados para niños y describelos en 20 palabras o menos.

    Respuesta:
    """

    # Crear el template del prompt
    prompt = PromptTemplate.from_template(template)

    # Configurar el modelo de Hugging Face
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.2-3B-Instruct",
        temperature=0.7,
        top_p=0.9,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

    # Crear la cadena (pipeline) LLM
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Ejecutar la cadena para generar los héroes
    response = llm_chain.invoke({"resumen": resumen, "villano": villano})

    # Verificar si la respuesta contiene 'text'
    if 'text' in response:
        return jsonify({'heroes': response['text']}), 200
    else:
        logging.error(f"Error al generar héroes: {response}")
        return jsonify({'error': 'No se pudo generar héroes correctamente.'}), 500


# Función para generar una historia basada en el resumen, villano y héroe seleccionados
@app.route('/historia', methods=['POST'])
def generar_historia():
    data = request.json
    resumen = data.get('resumen')
    villano = data.get('villano')
    heroe = data.get('heroe')

    if not resumen or not villano or not heroe:
        return jsonify({'error': 'Resumen, villano o héroe no proporcionados'}), 400

    # Definir el prompt para generar la historia
    template = """
    Genera una historia corta sobre esta información:
    '{resumen}'
    La historia debe contar con las siguientes especificaciones:
        1. La historia debe tener como personaje principal: {heroe}
        2. La historia debe tener como villano: {villano}
        3. Divide la historia en 5 escenas principales.
        4. Cada escena debe ser un párrafo corto pero muy descriptivo y visual.
        5. La historia completa debe tener al menos 10 párrafos detallados.
        6. Evita temas sensibles o contenido para adultos.
        7. Asegúrate de que el personaje principal esté presente en cada escena.
        8. Mantén la consistencia en personajes y crea los escenarios que consideres para la historia y elementos de la trama en todas las escenas.
        9. La historia debe tener un comienzo claro, desarrollo y conclusión.
    Formato de salida:
    La RESPUESTA debe ser únicamente la historia completa:
    [Historia completa aquí, con al menos 10 párrafos]

    Historia:
    """

    prompt = PromptTemplate.from_template(template)

    # Configurar el modelo de Hugging Face
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.2-3B-Instruct",
        model_kwargs={"max_length": 1024},  # Aumentar max_length para historias más largas
        temperature=0.7,  # Ajustar temperatura para mayor creatividad
        top_p=0.9,
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
    )

    # Crear la cadena (pipeline) LLM
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    # Ejecutar la cadena para generar la historia
    response = llm_chain.invoke({
        "resumen": resumen,
        "villano": villano,
        "heroe": heroe
    })

       # Verificar si la respuesta contiene 'text'
    if 'text' in response:
        historia_generada = response['text']

        # Guardar solo la historia en un archivo JSON
        carpeta = 'historias'
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        nombre_archivo = f"historia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ruta_completa = os.path.join(carpeta, nombre_archivo)

        # Guardar solo la historia en el archivo JSON
        with open(ruta_completa, 'w', encoding='utf-8') as archivo_json:
            json.dump({
                "historia": historia_generada
            }, archivo_json, ensure_ascii=False, indent=4)

        logging.info(f'Historia guardada en: {ruta_completa}')

        # Retornar solo la historia generada en el JSON de la respuesta
        return jsonify({'historia': historia_generada}), 200
    else:
        logging.error(f"Error al generar la historia: {response}")
        return jsonify({'error': 'No se pudo generar la historia correctamente.'}), 500



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inter')
def inter():
    return render_template('inter.html')

if __name__ == '__main__':
    app.run(debug=True)
