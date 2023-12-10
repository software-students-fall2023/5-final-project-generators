import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

MONGO_DB_HOST = os.getenv("MONGO_DB_HOST") or "localhost"
MONGO_DB_PORT = int(os.getenv("MONGO_DB_PORT") or 27017)
MONGO_DB_USERNAME = os.getenv("MONGO_DB_USERNAME")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")
DATABASE_NAME = os.getenv("MONGO_DB_NAME") or "financify"
SECRET_KEY = os.getenv("SECRET_KEY")

ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"