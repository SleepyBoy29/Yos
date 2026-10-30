import requests
import os

API_TOKEN = "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"

MODEL_URL = (
    "https://api-inference.huggingface.co/models/"
    "black-forest-labs/FLUX.1-schnell"
)

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

os.makedirs("result", exist_ok=True)

with open("prompt.txt", encoding="utf-8") as f:
    prompts = [x.strip() for x in f if x.strip()]

for no, prompt in enumerate(prompts, start=1):

    print(f"Generate: {prompt}")

    response = requests.post(
        MODEL_URL,
        headers=headers,
        json={"inputs": prompt},
        timeout=300
    )

    if response.status_code == 200:

        with open(f"result/{no}.png", "wb") as img:
            img.write(response.content)

        print(f"SUCCESS result/{no}.png")

    else:

        print(response.status_code)
        print(response.text)