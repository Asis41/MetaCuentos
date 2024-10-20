import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_huggingface import HuggingFaceEndpoint
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document

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
    # model_kwargs={"max_length": 4096},
    temperature=0.1,
    top_p=0.95,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
)

def clean_text(text):
    # Implementa la lógica de limpieza de texto aquí
    return text.strip()

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return clean_text(text)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return clean_text(file.read())

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=512,
        separators=["\n\n", "\n", " ", ""]
    )
    return [Document(page_content=t) for t in text_splitter.split_text(text)]

def create_story(docs):
    map_prompt_template = """
Proporciona un resumen claro y sencillo del siguiente fragmento de texto. Asegúrate de:
1. Extraer los datos más importantes sobre el contenido.
2. No omitir ninguna información relevante sobre el contenido.

Texto a resumir:
{text}

Resumen claro y conciso:
"""
    
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

    combine_prompt_template = """
Basándote en la siguiente información, crea un resumen fácil de entender para un niño de entre 6-12 años.
El resumen debe ser claro y educativo. Asegúrate de seguir estas instrucciones:

1. Usa lenguaje sencillo que los niños puedan entender.
2. Explica el tema de una manera que un niño pueda visualizar lo que está pasando, usando ejemplos o comparaciones sencillas si es necesario.
3. Destaca por qué este tema es importante.
4. Incluye un dato interesante o algo que los niños puedan hacer para ayudar o entender mejor el tema.
5. Evita repetir información innecesaria y asegúrate de que el resumen sea directo, sin complicar demasiado los hechos.

Información:
{text}

Resumen educativo para niños:
"""

    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        verbose=True
    )
                                                                                                                              
    return chain.invoke({"input_documents": docs})

def process_documents(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files_processed = False

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        if filename.endswith('.pdf'):
            text = read_pdf(file_path)
        elif filename.endswith('.txt'):
            text = read_txt(file_path)
        else:
            continue

        docs = split_text(text)
        story = create_story(docs)

        output_filename = f"resumen_{os.path.splitext(filename)[0]}.txt"
        output_path = os.path.join(output_folder, output_filename)

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(story['output_text'])

        print(f"Cuento guardado: {output_path}")
        files_processed = True

    if not files_processed:
        print("No se encontraron archivos PDF o TXT para procesar.")

if __name__ == "__main__":
    input_folder = "documents"
    output_folder = "stories"
    process_documents(input_folder, output_folder)