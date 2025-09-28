import os
from dotenv import load_dotenv

# Load environment variables with explicit path
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    DB_HOST = os.getenv("DB_HOST", "database-1.chcyc88wcx2l.eu-north-1.rds.amazonaws.com")
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "DBpicshot")
    DB_NAME = os.getenv("DB_NAME", "eventsreminder")
    USE_PURE = os.getenv("USE_PURE", "True").lower() == "true"