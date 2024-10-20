import os
import time
import requests
from PIL import Image
import io
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token desde las variables de entorno
HUGGINGFACEHUB_API_TOKEN = ""

# Asegurarse de que el token fue cargado correctamente
if not HUGGINGFACEHUB_API_TOKEN:
    raise ValueError("El token de Hugging Face no se ha encontrado en las variables de entorno.")

# Configuración del endpoint y las cabeceras para la generación de imágenes
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
HF_HEADERS = {"Authorization": "Bearer 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"}

def get_user_theme():
    return input("Por favor, ingresa el tema para tu historia: ")

def generate_text(prompt, max_length=512, temperature=0.7, top_p=0.9):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": True,
            "return_full_text": False
        }
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct",
        headers={"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"},
        json=payload
    )
    if response.status_code == 200:
        data = response.json()
        return data[0]['generated_text'].strip()
    else:
        raise Exception(f"Error en la generación de texto: {response.status_code} - {response.text}")

def translate_to_english(text):
    prompt = f"Traduce el siguiente texto al inglés, manteniendo su estructura y formato:\n\n{text}"
    try:
        translated_text = generate_text(prompt)
        return translated_text
    except Exception as e:
        print(f"Error en la traducción: {e}")
        return text

def generate_story_and_scenes(theme):
    prompt = f"""
    Genera una historia corta en español sobre '{theme}' con las siguientes especificaciones:
    1. La historia debe tener un personaje principal claramente definido y personajes secundarios.
    2. Divide la historia en 5 escenas principales.
    3. Cada escena debe ser un párrafo corto pero muy descriptivo y visual.
    4. La historia completa debe tener al menos 10 párrafos detallados.
    5. Evita temas sensibles o contenido para adultos.
    6. Asegúrate de que el personaje principal esté presente en cada escena.
    7. Mantén la consistencia en personajes, escenarios y elementos de la trama en todas las escenas.
    8. La historia debe tener un comienzo claro, desarrollo y conclusión.

    Formato de salida:
    Historia completa:
    [Historia completa aquí, con al menos 10 párrafos]

    Escenas:
    1. [Primera escena aquí]
    2. [Segunda escena aquí]
    ...
    10. [Décima escena aquí]
    """
    try:
        response_text = generate_text(prompt)
        if "Escenas:" in response_text:
            parts = response_text.split("Escenas:")
            story = parts[0].replace("Historia completa:", "").strip()
            scenes_text = parts[1].strip()
            scenes = [line.strip() for line in scenes_text.split('\n') if line.strip()]
            return story, scenes[:5]
        else:
            print("La respuesta no contiene escenas. Generando historia predeterminada.")
            return generate_default_story(theme)
    except Exception as e:
        print(f"Error al generar la historia: {e}")
        return generate_default_story(theme)

def generate_default_story(theme):
    story = f"""
    En un mundo inspirado en {theme}, un héroe inesperado surge de entre la multitud.
    Este protagonista descubre un poder oculto que cambia su destino y lo lanza a una aventura extraordinaria.
    A lo largo de su viaje, enfrenta desafíos épicos que ponen a prueba sus nuevas habilidades y su determinación.
    Con cada obstáculo superado, nuestro héroe crece y se transforma, inspirando a otros a su alrededor.
    Aliados inesperados se unen a su causa, cada uno aportando habilidades únicas que complementan las del protagonista.
    Juntos, forman un equipo imparable, superando obstáculos que parecían insuperables.
    A medida que avanzan, descubren secretos antiguos que cambian su comprensión del mundo que los rodea.
    Estos descubrimientos los llevan a cuestionar todo lo que creían saber, enfrentándolos a dilemas morales complejos.
    En un giro inesperado, se encuentran cara a cara con el verdadero antagonista, cuyas motivaciones resultan ser más complejas de lo que imaginaban.
    Finalmente, la aventura culmina en un emocionante clímax que no solo transforma a nuestro protagonista y sus aliados, sino que cambia para siempre el mundo de {theme}.
    """
    scenes = [
        f"Un héroe inesperado descubre su destino en el mundo de {theme}.",
        "El protagonista se embarca en una aventura, enfrentando su primer desafío.",
        "Nuevos aliados se unen a la causa, formando un equipo diverso.",
        "El equipo supera un obstáculo aparentemente imposible, fortaleciendo sus lazos.",
        "Un antiguo secreto es revelado, cambiando la perspectiva de nuestros héroes.",
        "El grupo enfrenta un dilema moral que pone a prueba sus valores.",
        "Una traición inesperada sacude al equipo, forzándolos a replantearse su misión.",
        "Los héroes descubren la verdadera naturaleza de su enemigo.",
        "En una batalla épica, el protagonista utiliza todo lo aprendido para enfrentar al antagonista.",
        f"La victoria trae consigo cambios profundos, transformando el mundo de {theme} para siempre."
    ]
    return story, scenes

def extract_characters_and_settings(story):
    prompt = f"""
    Basándote en la siguiente historia, proporciona una lista de personajes principales y secundarios, y una lista de escenarios y elementos clave de la trama:

    {story}

    Formato de salida:
    Personajes:
    - Personaje 1
    - Personaje 2
    ...

    Escenarios y elementos clave:
    - Escenario/Elemento 1
    - Escenario/Elemento 2
    ...
    """
    try:
        response_text = generate_text(prompt)
        return response_text
    except Exception as e:
        print(f"Error al extraer personajes y escenarios: {e}")
        return ""

def enhance_scene_description(scene, theme, characters, settings):
    prompt = f"""
    Mejora esta escena para generar una imagen coherente con el tema '{theme}', enfocándote en detalles visuales y ambientales vívidos.
    La descripción debe ser muy detallada y específica, incluyendo:
    - Descripción del entorno (colores, texturas, iluminación)
    - Posición y acción de los personajes
    - Expresiones faciales y lenguaje corporal
    - Objetos o elementos importantes en la escena
    - Atmósfera general y estado de ánimo

    Mantén la descripción breve (máximo 100 palabras) y muy visual. Asegúrate de incluir al personaje principal y los personajes secundarios relevantes: {characters}
    Mantén la consistencia con los siguientes escenarios y elementos: {settings}

    Escena original: '{scene}'

    Proporciona la descripción mejorada en formato de párrafo único, sin viñetas ni numeración.
    """
    try:
        enhanced_description = generate_text(prompt)
        return enhanced_description
    except Exception as e:
        print(f"Error al mejorar la descripción: {e}")
        return scene

def generate_image(prompt, style_prompt):
    full_prompt = f"{prompt} {style_prompt}"
    payload = {
        "inputs": full_prompt,
        "parameters": {"width": 1280, "height": 720}
    }
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        raise Exception(f"Error en la generación de imagen: {response.status_code} - {response.text}")

def main():
    theme = get_user_theme()
    story, scenes = generate_story_and_scenes(theme)

    print("Historia completa:")
    print(story)
    print("\nEscenas principales:")

    characters_and_settings = extract_characters_and_settings(story)
    print("Personajes y escenarios extraídos:")
    print(characters_and_settings)

    style_prompt = f"Estilo: Ilustración detallada y realista. Incluye los personajes y escenarios en cada escena según corresponda. Mantén una paleta de colores y técnica artística coherentes. Tamaño de imagen: 1280x720 píxeles."

    image_files = []

    for i, scene in enumerate(scenes, 1):
        print(f"\nEscena {i}:")
        print(f"Original: {scene}")

        enhanced_description = enhance_scene_description(scene, theme, characters_and_settings, characters_and_settings)
        print(f"Descripción mejorada: {enhanced_description}")

        english_description = translate_to_english(enhanced_description)

        try:
            image = generate_image(english_description, style_prompt)
            image_filename = f"escena_{i}.png"
            image.save(image_filename)
            image_files.append(image_filename)
            print(f"Imagen generada y guardada como {image_filename}")
        except Exception as e:
            print(f"Error al generar la imagen para la escena {i}: {e}")

        time.sleep(2)  # Pausa para evitar sobrecargar las APIs

    print(f"Proceso completado. Se han generado {len(image_files)} imágenes.")

if __name__ == "__main__":
    main()
