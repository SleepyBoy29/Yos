import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

os.makedirs("result", exist_ok=True)

with open("prompt.txt", encoding="utf-8") as f:
    prompts = [x.strip() for x in f if x.strip()]

for no, prompt in enumerate(prompts, start=1):

    try:

        print(f"Generate: {prompt}")

        response = client.models.generate_images(
            model=MODEL_NAME,
            prompt=prompt
        )

        image_bytes = response.generated_images[0].image.image_bytes

        output_file = f"result/{no}.png"

        with open(output_file, "wb") as img:
            img.write(image_bytes)

        print(f"SUCCESS : {output_file}")

    except Exception as e:

        print(f"FAILED : {prompt}")
        print(e)