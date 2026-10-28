


from openai import OpenAI
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader

# Use env variable (IMPORTANT)
client = OpenAI(api_key="sk-LI-QW-voerJ_V0kjtcXnLj8swgF2q_2I8qFbiCslljT3BlbkFJGxHGY8iOXoDL3K2PQPaHiy3aZElQFNXT9uf73cIvkA")



# -----------------------------
# Read PDF properly
# -----------------------------
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# -----------------------------
# Recursive Text Splitter
# -----------------------------
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)


# -----------------------------
# PDF → Speech
# -----------------------------
def file_to_speech(file_path, output_file="output.wav"):
    text = read_pdf(file_path)

    chunks = split_text(text)
    print(f"Total chunks: {len(chunks)}")

    with open(output_file, "wb") as out:
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")

            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=chunk
            )

            out.write(response.read())

    return output_file


# -----------------------------
# Example
# -----------------------------
audio_path = file_to_speech("Enterprise Supply Chain Performance Report 2025.pdf")
print("✅ Audio saved at:", audio_path)