from dotenv import load_dotenv
import os

load_dotenv()

print("API Key:", os.getenv("API_KEY"))
print("Database:", os.getenv("DB_NAME"))