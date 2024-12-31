import os
import requests
import datetime
import logging

# Configuration
BASE_URL = os.getenv("BASE_URL", "https://example.com")
ENDPOINT = os.getenv("ENDPOINT", "/api/admin/backups")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)
HEALTH_ENDPOINT = os.getenv("HEALTH_ENDPOINT", "/")  # Dedicated health check endpoint if available

URL = f"{BASE_URL}{ENDPOINT}"
HEALTH_URL = f"{BASE_URL}{HEALTH_ENDPOINT}"
DATA = {"key": "value"}  # Adjust your payload as needed
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else "",
    "Content-Type": "application/json"
}

# Set a fixed path for the log file
LOG_FILE = "/app/script.log"

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',  # Overwrite log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def health_check(url: str) -> bool:
    """
    Perform a health check on the API.
    
    Args:
        url (str): The health check URL.
    
    Returns:
        bool: True if the health check passes, False otherwise.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        logging.info(f"Health check successful: {response.status_code}")
        print(f"{datetime.datetime.now()} - Health check successful: {response.status_code}")
        return True
    except requests.RequestException as e:
        logging.error(f"Health check failed: {e}")
        print(f"{datetime.datetime.now()} - Health check failed: {e}")
        return False


def make_post_request():
    """
    Make a POST request to the API endpoint.
    """
    try:
        response = requests.post(URL, json=DATA, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"POST successful: {response.status_code}")
        print(f"{datetime.datetime.now()} - POST successful: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"POST Error: {e}")
        print(f"{datetime.datetime.now()} - POST Error: {e}")


if __name__ == "__main__":
    if not AUTH_TOKEN:
        error_msg = "Authorization token is missing! Please set the AUTH_TOKEN environment variable."
        logging.error(error_msg)
        print(error_msg)
    else:
        if health_check(HEALTH_URL):
            make_post_request()
        else:
            error_msg = "Health check failed. Aborting POST request."
            logging.error(error_msg)
            print(error_msg)