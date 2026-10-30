import pandas as pd
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "models/imagen-4.0-generate-001"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

os.makedirs("result", exist_ok=True)

df = pd.read_csv("prompt.csv")

for _, row in df.iterrows():

    prompt = str(row["prompt"]).strip()
    file_id = row["id"]

    try:

        print(f"Generate: {prompt}")

        response = client.models.generate_images(
            model=MODEL_NAME,
            prompt=prompt
        )

        image_bytes = response.generated_images[0].image.image_bytes

        output_file = f"result/{file_id}.png"

        with open(output_file, "wb") as f:
            f.write(image_bytes)

        print(f"SUCCESS : {output_file}")

    except Exception as e:

        print(f"FAILED : {file_id}")
        print(e)