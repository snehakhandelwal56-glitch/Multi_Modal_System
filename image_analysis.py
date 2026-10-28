from google import genai
import pathlib

# Set API key
import os
os.environ["GEMINI_API_KEY"] = "AIzaSyBOqy8tOiiZQxdcsnZ9hvpypgLkvaO00PI"
client = genai.Client()

def ask_image(image_path, question):
    # ✅ Upload image
    uploaded_file = client.files.upload(file=image_path)

    # ✅ Use uploaded file
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            uploaded_file,
            question
        ]
    )

    return response.text


# --- Run ---
answer = ask_image("sample_image.png", "Explain this image")
print(answer)