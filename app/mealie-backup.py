"""
mealie-backup.py

Automates the backup of Mealie data and uploads the backup to a Nextcloud WebDAV server.

This script:
- Authenticates with the Mealie API and Nextcloud WebDAV using secrets from /run/secrets.
- Performs a connectivity check on the Mealie server.
- Deletes existing backups on the Mealie server.
- Creates a new backup and retrieves its download token.
- Downloads the backup file to a temporary location.
- Uploads the backup file to a specified Nextcloud WebDAV directory.
- Logs operations and errors to /app/script.log.

Classes:
    Mealie: Handles Mealie API configuration and authentication.
    Nextcloud: Handles Nextcloud WebDAV configuration and authentication.

Functions:
    load_secrets(): Loads secrets from /run/secrets.
    build_url(*parts): Joins URL parts with single slashes.
    health_check(url): Checks if the Mealie server is reachable.
    get_backups(url): Retrieves a list of existing backups.
    delete_backup(url, backup_name): Deletes a specific backup.
    delete_local_backups(url): Deletes all existing backups.
    create_backup(url): Creates a new backup on the Mealie server.
    get_backup_token(backup_name): Retrieves a download token for a backup.
    get_backup_file(file_token): Downloads a backup file using its token.
    upload_file_webdav(nextcloud, filename, local_path): Uploads a file to Nextcloud WebDAV.

Entry point:
    When run as a script, performs the full backup and upload workflow.
"""

import os
import datetime
import logging
from pathlib import Path
import requests

# Set a fixed path for the log file
LOG_FILE = "/app/script.log"


# Logging Configuration
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',  # Overwrite log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Mealie:
    """Handles Mealie API configuration."""
    def __init__(self):
        secrets = load_secrets()
        self.base_url = secrets.get('MEALIE_BASE_URL_TS')
        self.backup_url = build_url(self.base_url, os.getenv('MEALIE_BACKUP_PATH'))
        self.health_url = build_url(self.base_url, os.getenv('MEALIE_HEALTH_PATH'))
        self.download_url = build_url(self.base_url, os.getenv('MEALIE_DOWNLOAD_PATH'))
        self.auth_token = secrets.get('MEALIE_AUTH_TOKEN')
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}" if self.auth_token else "",
            "Content-Type": "application/json"
        }


class Nextcloud:
    '''Handles Nextcloud WebDAV configuration as a backup target.'''
    def __init__(self):
        secrets = load_secrets()

        self.user = os.getenv('NC_USER')
        self.password = secrets.get('NC_PASS')
        self.webdav_url = build_url(
            secrets.get('NC_BASE_URL_TS'),
            os.getenv('WEBDAV_PATH'),
            os.getenv('NC_USER')
            )


def load_secrets():
    """Load all secrets from /run/secrets into a dictionary"""
    secrets = {}
    secrets_dir = Path("/run/secrets")

    for secret_file in secrets_dir.iterdir():
        if secret_file.is_file():
            secrets[secret_file.name] = secret_file.read_text().strip()

    return secrets


def build_url(*parts):
    """
    Build URL from any number of parts, ensuring exactly one slash between each"""
    if not parts:
        return ""

    # Filter out empty/None parts and strip slashes
    clean_parts = []
    for part in parts:
        if part:  # Skip None or empty strings
            clean_parts.append(str(part).strip('/'))

    # Join with single slashes
    return '/'.join(clean_parts)


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
        logging.info("Health check successful: %s", response.status_code)
        print(f"{datetime.datetime.now()} - Health check successful: {response.status_code}")
        return True
    except requests.RequestException as e:
        logging.error("Health check failed: %s", e)
        print(f"{datetime.datetime.now()} - Health check failed: {e}")
        return False


def get_local_backups(url: str):
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
        response = requests.get(url, headers=mealie.headers, timeout=10)
        response.raise_for_status()
        backups = response.json()  # Returns a dictionary
        logging.info("Fetched backups: %s", backups)
        return backups
    except requests.RequestException as e:
        logging.error("Error fetching backups: %s", e)
        print(f"{datetime.datetime.now()} - Error fetching backups: {e}")
        return {}


def delete_backup(url: str, backup_name: str):
    """
    Delete a specific backup by its name.

    Args:
        url (str): The URL and backup endpoint for the Mealie API
        backup_name (str): The name of the backup to delete

    Notes:
        - Sends a DELETE request to the backup API endpoint.
        - Logs and prints the result of the deletion.
        - Handles and logs errors if the request fails.
    """
    try:
        delete_url = f"{url}/{backup_name}"
        response = requests.delete(delete_url, headers=mealie.headers, timeout=10)
        response.raise_for_status()
        logging.info("Deleted backup: %s", backup_name)
        print(f"{datetime.datetime.now()} - Deleted backup: {backup_name}")
    except requests.RequestException as e:
        logging.error("Error deleting backup %s: %s", backup_name, e)
        print(f"{datetime.datetime.now()} - Error deleting backup {backup_name}: {e}")


def delete_local_backups(url: str):
    """
    Delete existing backups on the server so that only the most recent
    is locally available.

    Args:
        url (str): The URL and backup endpoint for the Mealie API

    Notes:
        - Fetches the list of backups via `get_backups`.
        - Iterates over the `imports` list in the response and deletes each backup by its name.
        - Logs and prints the status of each deletion.
        - Skips backups that do not have a valid `name` field.
    """
    backups = get_local_backups(url)
    print(f"{datetime.datetime.now()} - Backups found: {len(backups['imports'])}")
    imports = backups.get('imports', [])
    for backup in imports:
        backup_name = backup.get('name')
        if backup_name:
            delete_backup(url, backup_name)
    logging.info("All backups deleted.")
    print(f"{datetime.datetime.now()} - All backups deleted.")


def create_backup(url: str):
    """
    Create a new backup by sending a POST request to the backups endpoint.

    Args:
        url (str): The URL and backup endpoint for the Mealie API

    Returns:
        str: The name of the newly created backup, or None if failed
    """
    try:
        response = requests.post(url, headers=mealie.headers, timeout=10)
        response.raise_for_status()
        logging.info("Backup created: %s", response.json())

        backups = get_local_backups(url)
        imports = backups.get('imports', [])

        new_backup_name = imports[0].get('name') if imports else None
        print(f"{datetime.datetime.now()} - New backup created: {new_backup_name}")
        logging.info("New backup created: %s", new_backup_name)
        return new_backup_name

    except requests.RequestException as e:
        logging.error("Error creating backup: %s", e)
        print(f"{datetime.datetime.now()} - Error creating backup: {e}")
        return None

def get_backup_token(backup_name):
    """
    Get file token for a specific backup by sending GET request to backup URL.

    Args:
        backup_name (str): Name of the backup file to get token for

    Returns:
        str: The file token string, or None if request fails
    """
    try:
        token_url = build_url(mealie.backup_url, backup_name)
        response = requests.get(token_url, headers=mealie.headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        file_token = data.get('fileToken')

        if file_token:
            logging.info("%s: %s", backup_name, file_token)
            print(f"{datetime.datetime.now()} - Token retrieved: {file_token}")
            return file_token
        else:
            logging.warning("No file_token found in response for %s", backup_name)
            return None

    except requests.RequestException as e:
        logging.error("Error getting backup token for %s: %s", backup_name, e)
        return None

def get_backup_file(file_token):
    """
    Download backup file using file token.

    Args:
        file_token (str): Token to authenticate the download

    Returns:
        str: Downloaded filename, or None if download fails
    """
    try:
        tokenized_download_url = mealie.download_url + file_token
        response = requests.get(
            tokenized_download_url,
            headers=mealie.headers,
            timeout=10
        )
        response.raise_for_status()

        # Extract filename from Content-Disposition header
        filename = None
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')

        # Fallback if filename not found in headers
        if not filename:
            filename = f"mealie_{datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')}.zip"

        temp_file_path = f"/tmp/{filename}"

        with open(temp_file_path, 'wb') as f:
            f.write(response.content)

        logging.info("Downloaded backup: %s", filename)
        print(f"{datetime.datetime.now()} - Downloaded: {filename}")
        return filename, temp_file_path

    except requests.RequestException as e:
        logging.error("Error downloading backup: %s", e)
        print(f"{datetime.datetime.now()} - Error downloading backup: {e}")
        return None

def upload_file_webdav(nextcloud, filename, local_path=None):
    """
    Upload a file to WebDAV server using PUT request.

    Args:
        nextcloud: Nextcloud instance with credentials and URLs
        filename: Target filename on server
        local_path: Local file path (defaults to /tmp/filename if None)

    Returns:
        bool: True if upload successful, False otherwise
    """
    if local_path is None:
        local_path = f"/tmp/{filename}"

    if not os.path.exists(local_path):
        logging.error("Local file does not exist:  %s", local_path)
        return False

    url = build_url(nextcloud.webdav_url, '/Mealie/', filename)
    logging.info("Uploading %s to %s", filename, url)

    try:
        with open(local_path, 'rb') as file:
            response = requests.put(
                url,
                data=file,
                auth=(nextcloud.user, nextcloud.password),
                headers={"X-Requested-With": "XMLHttpRequest"},
                timeout=60
            )

        # Check for successful upload (WebDAV typically returns 201 or 204)
        if response.status_code in [200, 201, 204]:
            print(
                f"{datetime.datetime.now()} - ",
                f"✓ Upload successful: {filename} ({response.status_code}"
            )
            logging.info("✓ Upload successful: %s (%s)", filename, response.status_code)
            return True
        else:
            logging.error("✗ Upload failed: %s - Status %s", filename, response.status_code)
            logging.error("Response: %s", response.text[:200])
            return False

    except requests.exceptions.Timeout:
        logging.error("✗ Upload timeout: %s", filename)
        return False
    except requests.exceptions.ConnectionError as e:
        logging.error("✗ Connection error uploading %s: %s", filename, e)
        return False
    except requests.exceptions.RequestException as e:
        logging.error("✗ Request error uploading %s: %s", filename, e)
        return False
    except FileNotFoundError:
        logging.error("✗ Local file not found: %s", local_path)
        return False
    except Exception as e:
        logging.error("✗ Unexpected error uploading %s: %s", filename, e)
        return False


if __name__ == "__main__":
    mealie = Mealie()
    nc = Nextcloud()

    if not mealie.auth_token:
        error_msg = "Authorization token is missing! Please check the AUTH_TOKEN secret."
        logging.error(error_msg)
        print(error_msg)
    else:
        if health_check(mealie.health_url):
            delete_local_backups(mealie.backup_url)
            created_backup = create_backup(mealie.backup_url)
            if created_backup:
                backupToken = get_backup_token(created_backup)
                result = get_backup_file(backupToken)
                if result is not None:
                    backup_file_name, backup_file_path = result
                    upload_file_webdav(nc, backup_file_name, backup_file_path)

                else:
                    print("Backup download failed.")

        else:
            error_msg = "Health check failed. Aborting backup operations."
            logging.error(error_msg)
            print(error_msg)
