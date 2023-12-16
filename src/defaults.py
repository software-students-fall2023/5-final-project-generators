import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

print('host is ', os.getenv("MONGO_DB_HOST"))
MONGO_DB_HOST = os.getenv("MONGO_DB_HOST") or "localhost"
MONGO_DB_PORT = int(os.getenv("MONGO_DB_PORT") or 27017)
MONGO_DB_USERNAME = os.getenv("MONGO_DB_USERNAME")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")
DATABASE_NAME = os.getenv("MONGO_DB_NAME") or "financify"
SECRET_KEY = os.getenv("SECRET_KEY") or "secret"

print('username and password are ', MONGO_DB_USERNAME, MONGO_DB_PASSWORD)
ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"