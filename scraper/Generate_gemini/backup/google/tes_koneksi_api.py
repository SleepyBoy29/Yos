import os
from dotenv import load_dotenv

print("Current Directory :", os.getcwd())
print("File .env ada?    :", os.path.exists(".env"))

load_dotenv()

print("API KEY =", os.getenv("GEMINI_API_KEY"))