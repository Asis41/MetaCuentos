import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os

def limpiar_texto(texto):
    # Eliminar espacios en blanco extra y saltos de línea
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def extraer_texto_de_url(url):
    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()
        
        # Forzar la codificación a UTF-8
        response.encoding = 'utf-8'

        # Crear objeto BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        if url.startswith('https://elpais.com/'):
            texto = extraer_texto_elpais(soup)
        elif url.startswith('https://www.nationalgeographicla.com/'):
            texto = extraer_texto_natgeo(soup)
        else:
            texto = extraer_texto_generico(soup)

        # Limpiar el texto
        texto_limpio = limpiar_texto(texto)

        return texto_limpio

    except requests.RequestException as e:
        return f"Error al procesar {url}: {str(e)}"

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
            else:
                texto += 'No se encontró el título principal (h1).\n\n'
            
            if h2:
                texto += h2.get_text(separator=' ', strip=True) + '\n\n'
            else:
                texto += 'No se encontró el subtítulo (h2).\n\n'
        else:
            texto += 'No se encontró el elemento <header>.\n\n'

        div_cuerpo = article.find('div', attrs={'data-dtm-region': 'articulo_cuerpo'})
        if div_cuerpo:
            for elemento in div_cuerpo.find_all(['p', 'h3']):
                texto += elemento.get_text(separator=' ', strip=True) + '\n\n'
        else:
            texto += 'No se encontró el cuerpo del artículo.\n\n'
    else:
        texto = 'No se encontró el elemento <article>.'
    return texto

def extraer_texto_natgeo(soup):
    texto = ''
    # Buscar el título principal
    titulo = soup.select_one('h1.css-1lncn9l')
    if titulo:
        texto += titulo.get_text(separator=' ', strip=True) + '\n\n'
    else:
        texto += 'No se encontró el título principal.\n\n'

    # Buscar y extraer contenido de los elementos con la clase específica
    parrafos = soup.select('div.paragraph.css-1vtiyti')
    if parrafos:
        for parrafo in parrafos:
            # Extraer texto solo una vez de cada párrafo
            texto_parrafo = parrafo.get_text(separator=' ', strip=True)
            if texto_parrafo:
                texto += texto_parrafo + '\n\n'
    else:
        texto += 'No se encontraron párrafos con la clase especificada.\n\n'
    
    return texto

def extraer_texto_generico(soup):
    # Eliminar scripts y estilos
    for script in soup(["script", "style"]):
        script.decompose()
    # Obtener el texto completo de la página
    return soup.get_text()

def procesar_urls(urls):
    resultados = {}
    for url in urls:
        texto = extraer_texto_de_url(url)
        resultados[url] = texto
    return resultados

def guardar_resultados_en_archivo(resultados):
    carpeta = 'documents'
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"resultadosscraping{timestamp}.txt"

    ruta_completa = os.path.join(carpeta, nombre_archivo)

    with open(ruta_completa, 'w', encoding='utf-8') as file:
        for url, texto in resultados.items():
            file.write(f"Texto extraído de {url}:\n")
            file.write(texto)
            file.write("\n\n" + "="*50 + "\n\n")

    return ruta_completa

# Ejemplo de uso
if __name__ == "__main__":
    urls = [
        "https://elpais.com/clima-y-medio-ambiente/2024-09-26/no-hay-tiempo-que-perder-en-la-lucha-contra-la-deforestacion.html"
    ]

    resultados = procesar_urls(urls)
    ruta_archivo = guardar_resultados_en_archivo(resultados)

    print(f"Los resultados se han guardado en el archivo: {ruta_archivo}")