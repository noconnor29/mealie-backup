import os
import requests
import datetime
import logging


# Set a fixed path for the log file
LOG_FILE = "/app/script.log"

# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',  # Overwrite log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_secret(secret_name: str, default: str) -> str:
    """
    Load secret from Docker secrets file and return its content as a string.

    Args:
        secret_name (str): The name of the secret file to load from the Docker secrets 
                          directory (e.g., "api_key" loads from "/run/secrets/api_key").
        default (str, optional): Default value to return if the secret file does not exist.

    Returns:
        str: The content of the secret file with leading/trailing whitespace stripped,
             or the default value if file doesn't exist and default is provided.

    Raises:
        FileNotFoundError: If the secret file does not exist and no default is provided.
        PermissionError: If there are insufficient permissions to read the secret file.
        Exception: For any other errors encountered while reading the secret file.

    Notes:
        - Reads from the standard Docker secrets path "/run/secrets/{secret_name}".
        - Automatically strips whitespace from the secret content.
        - Returns default value only if file doesn't exist, not for other errors.
        - Designed for use in Docker containers with mounted secrets.
    """
    secret_path = f"/run/secrets/{secret_name}"
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        if default is not None:
            return default
        raise FileNotFoundError(f"Secret file not found: {secret_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading secret: {secret_path}")
    except Exception as e:
        raise Exception(f"Error reading secret {secret_name}: {str(e)}")

def build_url(base_url: str, endpoint: str):
    """
    Build a URL by combining base URL and endpoint with exactly one slash separator.

    Args:
        base_url (str): The base URL (e.g., "https://example.com" or "https://example.com/")
        endpoint (str): The endpoint path (e.g., "/api/backup" or "api/backup")

    Returns:
        str: Complete URL with exactly one slash between base_url and endpoint

    Examples:
        build_url("https://example.com", "/api/backup") -> "https://example.com/api/backup"
        build_url("https://example.com/", "api/backup") -> "https://example.com/api/backup"
        build_url("https://example.com/", "/api/backup") -> "https://example.com/api/backup"
        build_url("https://example.com", "api/backup") -> "https://example.com/api/backup"
    """
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

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


def get_backups(url: str):
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
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        backups = response.json()  # Returns a dictionary
        logging.info(f"Fetched backups: {backups}")
        return backups
    except requests.RequestException as e:
        logging.error(f"Error fetching backups: {e}")
        print(f"{datetime.datetime.now()} - Error fetching backups: {e}")
        return {}


def delete_backup(url: str, backup_name: str):
    """
    Delete a specific backup by its name.

    Args:
        url (str): The URL and backup endpoint for the Mealie API
        backup_name (str): The name of the backup to delete, typically the filename 
                           (e.g., "mealie_YYYY.MM.DD.HH.MM.SS.zip").

    Notes:
        - Sends a DELETE request to the backup API endpoint.
        - Logs and prints the result of the deletion.
        - Handles and logs errors if the request fails.
    """
    try:
        delete_url = f"{url}/{backup_name}"
        response = requests.delete(delete_url, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"Deleted backup: {backup_name}")
        print(f"{datetime.datetime.now()} - Deleted backup: {backup_name}")
    except requests.RequestException as e:
        logging.error(f"Error deleting backup {backup_name}: {e}")
        print(f"{datetime.datetime.now()} - Error deleting backup {backup_name}: {e}")


def delete_all_backups(url: str):
    """
    Delete all existing backups on the server.

    Args:
        url (str): The URL and backup endpoint for the Mealie API

    Notes:
        - Fetches the list of backups via `get_backups`.
        - Iterates over the `imports` list in the response and deletes each backup by its name.
        - Logs and prints the status of each deletion.
        - Skips backups that do not have a valid `name` field.
    """
    backups = get_backups(url)  # Fetch the backups
    print(f"{datetime.datetime.now()} - Backups found: {len(backups['imports'])}")
    imports = backups.get('imports', [])  # Extract the list of imports
    for backup in imports:
        backup_name = backup.get('name')  # Extract the backup name
        if backup_name:
            delete_backup(url, backup_name)  # Pass the name to delete_backup
    logging.info("All backups deleted.")
    print(f"{datetime.datetime.now()} - All backups deleted.")


def create_backup(url: str):
    """
    Create a new backup by sending a POST request to the backups endpoint.

    Args:
        url (str): The URL and backup endpoint for the Mealie API

    Notes:
        - Logs and prints the response if the backup creation is successful.
        - Handles and logs errors if the request fails.
    """
    try:
        response = requests.post(url, headers=HEADERS)
        response.raise_for_status()
        logging.info(f"Backup created: {response.json()}")
        backups = get_backups(url)  # Fetch the backups
        imports = backups.get('imports', [])  # Extract the list of imports
        for backup in imports:
            backup_name = backup.get('name')
        print(f"{datetime.datetime.now()} - New backup created: {backup_name}")
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
    '''base_url = load_secret("MEALIE_BASE_URL", "https://example.com")'''
    base_url = load_secret("MEALIE_BASE_URL_TS", "https://example.com")
    backup_endpoint = load_secret("MEALIE_BACKUP_ENDPOINT", "/api/admin/backups")
    auth_token = load_secret("MEALIE_AUTH_TOKEN", None)
    health_endpoint = load_secret("MEALIE_HEALTH_ENDPOINT", "/")  # Dedicated health check endpoint if available
    data = {"key": "value"}  # Adjust your payload as needed
    HEADERS = {
        "Authorization": f"Bearer {auth_token}" if auth_token else "",
        "Content-Type": "application/json"
    }
     
    if not auth_token:
        error_msg = "Authorization token is missing! Please set the AUTH_TOKEN environment variable."
        logging.error(error_msg)
        print(error_msg)
    else:
        if health_check(build_url(base_url, health_endpoint)):
            delete_all_backups(build_url(base_url, backup_endpoint))
            create_backup(build_url(base_url, backup_endpoint))
        else:
            error_msg = "Health check failed. Aborting backup operations."
            logging.error(error_msg)
            print(error_msg)
