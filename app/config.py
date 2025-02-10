import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# DB Config
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
HOST=os.getenv("HOST")

# DB URL
DB_CONFIG = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{HOST}:3306/{DB_NAME}"

# Sparrow SMS Credentials
SPARROW_API=os.getenv("SPARROW_API")
SPARROW_TOKEN=os.getenv("SPARROW_TOKEN")

# Upload Dir
BASE_UPLOAD_DIR = Path("uploads")
PRODUCTS_DIR = BASE_UPLOAD_DIR / "products"
USERS_DIR = BASE_UPLOAD_DIR / "users"
VOICES_DIR = BASE_UPLOAD_DIR / "voices"

# API Keys
OPENAI_KEY=os.getenv("OPENAI_KEY")
ASSEMBLYAI_KEY=os.getenv("ASSEMBLYAI_KEY")