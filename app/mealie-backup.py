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
    Perform a health check on the API to verify if the server is reachable and functional.

    Args:
        url (str): The health check URL, typically an endpoint of the server 
                   (e.g., "/" or "/health") used to test availability.

    Returns:
        bool: True if the health check passes (server responds successfully), False otherwise.

    Notes:
        - Sends a GET request to the provided URL.
        - Logs and prints the status of the health check.
        - A timeout of 5 seconds is used to ensure quick failure for unresponsive servers.
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


def get_backups():
    """
    Fetch the list of existing backups from the server.

    Returns:
        list: A list of dicts representing each backup containing details,
              including metadata like `name`, `date`, and `size`.

    Notes:
        - Sends a GET request to the backups API endpoint.
        - Logs and prints the response, including backup details if successful.
        - Returns an empty list if the request fails.
    """
    try:
        response = requests.get(URL, headers=HEADERS)
        response.raise_for_status()
        backups = response.json()  # Returns a dictionary
        logging.info(f"Fetched backups: {backups}")
        print(f"{datetime.datetime.now()} - Fetched backups: {backups}")
        return backups
    except requests.RequestException as e:
        logging.error(f"Error fetching backups: {e}")
        print(f"{datetime.datetime.now()} - Error fetching backups: {e}")
        return {}


def delete_backup(backup_name: str):
    """
    Delete a specific backup by its name.

    Args:
        backup_name (str): The name of the backup to delete, typically the filename 
                           (e.g., "mealie_YYYY.MM.DD.HH.MM.SS.zip").

    Notes:
        - Sends a DELETE request to the backup API endpoint.
        - Logs and prints the result of the deletion.
        - Handles and logs errors if the request fails.
    """
    try:
        delete_url = f"{URL}/{backup_name}"
        response = requests.delete(delete_url, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"Deleted backup: {backup_name}")
        print(f"{datetime.datetime.now()} - Deleted backup: {backup_name}")
    except requests.RequestException as e:
        logging.error(f"Error deleting backup {backup_name}: {e}")
        print(f"{datetime.datetime.now()} - Error deleting backup {backup_name}: {e}")


def delete_all_backups():
    """
    Delete all existing backups on the server.

    Notes:
        - Fetches the list of backups via `get_backups`.
        - Iterates over the `imports` list in the response and deletes each backup by its name.
        - Logs and prints the status of each deletion.
        - Skips backups that do not have a valid `name` field.
    """
    backups = get_backups()  # Fetch the backups
    imports = backups.get('imports', [])  # Extract the list of imports
    for backup in imports:
        backup_name = backup.get('name')  # Extract the backup name
        if backup_name:
            delete_backup(backup_name)  # Pass the name to delete_backup
    logging.info("All backups deleted.")
    print(f"{datetime.datetime.now()} - All backups deleted.")


def create_backup():
    """
    Create a new backup by sending a POST request to the backups endpoint.

    Notes:
        - Logs and prints the response if the backup creation is successful.
        - Handles and logs errors if the request fails.
    """
    try:
        response = requests.post(URL, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"Backup created: {response.json()}")
        print(f"{datetime.datetime.now()} - Backup created: {response.json()}")
    except requests.RequestException as e:
        logging.error(f"Error creating backup: {e}")
        print(f"{datetime.datetime.now()} - Error creating backup: {e}")


if __name__ == "__main__":
    """
    Main entry point of the script.

    - Validates if the AUTH_TOKEN environment variable is set.
    - Performs a health check on the server.
    - If the health check passes, deletes all existing backups and creates a new backup.
    - Logs and prints the status of each operation.
    """
    if not AUTH_TOKEN:
        error_msg = "Authorization token is missing! Please set the AUTH_TOKEN environment variable."
        logging.error(error_msg)
        print(error_msg)
    else:
        if health_check(HEALTH_URL):
            delete_all_backups()
            create_backup()
        else:
            error_msg = "Health check failed. Aborting backup operations."
            logging.error(error_msg)
            print(error_msg)
