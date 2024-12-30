import os
import requests
import datetime
import logging

# Configuration
#BASE_URL = os.getenv("BASE_URL", "https://example.com")
BASE_URL = os.getenv("BASE_URL", "https://homeassistant.merino-cloud.ts.net")
ENDPOINT = os.getenv("ENDPOINT", "/api/admin/backups")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)

URL = f"{BASE_URL}{ENDPOINT}"
DATA = {"key": "value"}  # Adjust your payload as needed
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "Content-Type": "application/json"
}

# Set a fixed path for the log file
LOG_FILE = "/app/script.log"

URL = f"{BASE_URL}{ENDPOINT}"
DATA = {"key": "value"}  # Adjust your payload as needed
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "Content-Type": "application/json"
}

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',  # Overwrite log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def make_post_request():
    try:
        response = requests.post(URL, json=DATA, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"POST successful: {response.status_code}")
        print(f"{datetime.datetime.now()} - POST successful: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error: {e}")
        print(f"{datetime.datetime.now()} - Error: {e}")

if __name__ == "__main__":
    if not AUTH_TOKEN:
        error_msg = "Authorization token is missing! Please set AUTH_TOKEN environment variable."
        logging.error(error_msg)
        print(error_msg)
    else:
        make_post_request()
