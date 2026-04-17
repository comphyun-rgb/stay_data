import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = os.getenv("DB_PATH", "data/seoul_stay.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{(BASE_DIR / DB_PATH).resolve()}"

# API Keys
VISIT_SEOUL_API_KEY = os.getenv("VISIT_SEOUL_API_KEY")
SEOUL_OPEN_DATA_API_KEY = os.getenv("SEOUL_OPEN_DATA_API_KEY")

# Areas for analysis
TARGET_DISTRICTS = ["마포구", "중구", "종로구", "서대문구"]

CLUSTER_MAPPING = {
    "홍대권": ["마포구", "서대문구"],
    "명동권": ["중구"],
    "종로권": ["종로구"],
    "신촌권": ["서대문구", "마포구"]
}
