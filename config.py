import os
import logging
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/discover"

DATABASE_URL = os.getenv("DATABASE_URL")

logger = logging.getLogger(__name__)
logger.info(f"DATABASE_URL host: {DATABASE_URL.split('@')[-1] if DATABASE_URL else 'NON TROVATO'}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL non configurato! Aggiungi il secret con: fly secrets set DATABASE_URL=...")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)