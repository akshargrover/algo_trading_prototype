import os 
import datetime
from config import DATA_DIR


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def today():
    return datetime.date.today()
