# Clonación de Voz con CoquiTTS

Este proyecto utiliza la tecnología de CoquiTTS para la clonación de voz, aprovechando sus capacidades de síntesis de voz. A continuación se describen los pasos necesarios para ejecutar el código en un entorno de desarrollo como Google Colab o Jupyter Notebook.

## Instalación de Dependencias

Primero, es necesario instalar las bibliotecas requeridas. Puedes hacerlo ejecutando los siguientes comandos:

```
!pip install TTS -qqq
!pip install pydub -qqq
```

- **TTS**: Esta biblioteca se usa junto con CoquiTTS para convertir texto en audio, es decir, generar una síntesis de voz a partir de un texto proporcionado.
- **pydub**: Se utiliza para manipular archivos de audio, como grabar segmentos de audio por separado y luego unirlos en un solo archivo.

## Importación de Bibliotecas

El siguiente bloque de código importa las bibliotecas necesarias:

```python
from TTS.api import TTS
from IPython.display import Audio
from pydub import AudioSegment
import os
```

- **IPython.display**: Nos permite mostrar el audio generado en el entorno de desarrollo.
- **pydub**: Se utiliza para procesar y manipular los archivos de audio.
- **os**: Nos permite gestionar variables del sistema operativo, útil para manejar rutas de archivos.

## Inicialización del Modelo

A continuación, cargamos el modelo de síntesis de voz preentrenado XTTS2:

```python
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
```

Este es un modelo preentrenado disponible en CoquiTTS que genera una síntesis de voz bastante natural y realista. Solo requiere un archivo de audio limpio, sin ruido de fondo y con una voz clara para realizar la semiclonación de voz.

## Código Principal

El siguiente código se encarga de leer un archivo JSON, extraer el texto a sintetizar, generar los segmentos de audio, combinarlos y limpiar los archivos temporales.

```python
import os
import json
from pydub import AudioSegment

def read_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_segments_from_json(data):
    historia = data.get("historia", "")
    sentences = historia.split('.')
    segments = [sentence.strip() + '.' for sentence in sentences if sentence.strip()]
    return segments

def synthesize_segments(segments, speaker_wav, language, output_prefix):
    file_paths = []
    for i, segment in enumerate(segments):
        file_path = f"{output_prefix}_part_{i}.wav"
        tts.tts_to_file(text=segment, file_path=file_path, speaker_wav=speaker_wav, language=language)
        file_paths.append(file_path)
    return file_paths

def combine_audio(file_paths, final_output):
    combined = AudioSegment.empty()
    for file_path in file_paths:
        audio = AudioSegment.from_wav(file_path)
        combined += audio
    combined.export(final_output, format="wav")

def clean_up(file_paths):
    for file_path in file_paths:
        os.remove(file_path)

# Uso del código
file_path = '/content/historia_20241020_110010.json'
speaker_wav = "/content/fer.wav"
language = "es"
output_prefix = "output"
final_output = "output.wav"

data = read_json_from_file(file_path)
segments = extract_segments_from_json(data)
file_paths = synthesize_segments(segments, speaker_wav, language, output_prefix)
combine_audio(file_paths, final_output)
clean_up(file_paths)
```

## Explicación del Código

1. **Lectura del archivo JSON**: El código comienza leyendo el archivo JSON que contiene el texto que se va a sintetizar.
2. **División en segmentos**: A continuación, el texto se divide en oraciones, ya que no es posible procesar grandes bloques de texto de una sola vez.
3. **Síntesis de voz**: Se crea un archivo de audio para cada segmento de texto utilizando el modelo preentrenado de CoquiTTS.
4. **Unión de archivos de audio**: Los segmentos de audio se combinan en un único archivo de salida.
5. **Limpieza de archivos temporales**: Finalmente, se eliminan los archivos de audio temporales para mantener el espacio de trabajo limpio.
