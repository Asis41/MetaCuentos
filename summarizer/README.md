## Generador de Resúmenes Educativos para Niños

Este código utiliza Llama 3.2 3B Instruct alojado en Hugging Face para generar resúmenes claros y educativos a partir de noticias. Los resúmenes están adaptados para niños de entre 6 y 12 años, destacando los puntos importantes de manera sencilla y comprensible.

### Características:
Lenguaje simple y claro: Asegura que los resúmenes sean comprensibles para niños.
Resumen educativo: Presenta los temas de manera que un niño pueda imaginar lo que está sucediendo y por qué es importante.
Dato interesante: Incluye un hecho curioso para captar mejor la atención de los niños.
Automatización: Toma noticias desde un archivo .txt, genera el resumen y lo guarda en una carpeta designada.

### Uso:

- Clona el repositorio.
- Crea un archivo .env con tu token de Hugging Face:

HUGGINGFACEHUB_API_TOKEN=tu_token_aqui

El archivo .txt con la noticia se genera en base al codigo de web scrapping.