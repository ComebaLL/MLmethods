import os

BASE_URL = "https://poedb.tw/us/Unique_item"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DATA_DIR = "data"
HTML_DIR = os.path.join(DATA_DIR, "raw_html")
IMG_DIR = os.path.join(DATA_DIR, "images")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
REQUEST_DELAY = 1.0
MAX_CONCURRENT_DOWNLOADS = 15