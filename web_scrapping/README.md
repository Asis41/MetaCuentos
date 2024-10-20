# Extractor de Texto Web

Este proyecto permite extraer y guardar texto desde páginas web específicas utilizando técnicas de web scraping. El script está diseñado para trabajar con sitios web como El País y National Geographic Latinoamérica, pero también puede extraer contenido de sitios genéricos.

### Características:

Extracción de texto personalizado: Soporta la extracción de páginas de El País y National Geographic Latinoamérica, con funciones dedicadas para cada sitio.
Procesamiento genérico: Si el sitio web no coincide con los específicos mencionados, extrae el contenido de manera genérica, omitiendo scripts y estilos.
Limpieza de texto: Elimina espacios en blanco innecesarios y formatea el contenido para mejorar su legibilidad.
Resultados guardados en archivo: Los textos extraídos se guardan en un archivo .txt dentro de la carpeta documents, con un nombre generado automáticamente basado en la fecha y hora.

### Uso:

En el archivo principal, especifica las URLs de las que deseas extraer texto dentro de la lista urls.
Ejecuta el script, el cual guardará los resultados en un archivo .txt en la carpeta documents.

### Requisitos:
Librerías: requests, beautifulsoup4

### Ejemplo:

urls = [
    "cambia_por_una_noticia"
]

**Nota: A futuro se plantea implementar mas secciones de noticieros, articulos, etc. en relacion con el Medio Ambiente**