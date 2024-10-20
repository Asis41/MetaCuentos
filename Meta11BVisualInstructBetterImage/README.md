### ES
# Descripción del Código

Este código implementa el modelo Llama 3.2 11B Vision-Instruct, que se caracteriza por su capacidad para interpretar imágenes y convertirlas a texto. A continuación, se describen los pasos que sigue el código:

* Lectura de Imágenes: El código comienza leyendo todas las imágenes almacenadas en una carpeta específica, diseñada para guardar las imágenes generadas por Flux.

* Generación de Prompts: Para cada imagen leída, se genera un prompt correspondiente que se almacena para su uso posterior.

* Análisis de Prompts: Una vez generados todos los prompts, estos se envían al modelo Llama junto con el prompt original utilizado para crear las imágenes en Flux.

* Selección de la Imagen: El modelo Llama recibe la instrucción de analizar los prompts generados y determinar cuál de ellos se asemeja más al prompt original de Flux. Como resultado, el modelo devuelve únicamente el número de la imagen seleccionada para su uso.
