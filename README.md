# mealie-backup
Project to automate [Mealie Recipe Manager](https://github.com/mealie-recipes/mealie) backups with a Python script via the Mealie API. Builds a Docker container to run the script and contains a Docker Compose to spin up the container and a Tailscale sidecar. Also included are systemd units to schedule and execute the compose file weekly.


**NOTE**: The Mealie does not currently provide a mechanism to exporting backup files via API. Backup files are generated and stored locally on the Mealie instance. 

## Structure
```
mealie-backup
├── docker-compose.yml             # Executes backup stack
├── Dockerfile                     # Builds app container w/ Python env
├── sample-env                     # Sample env file with req'd variables
├── .devcontainer
|    ├── devcontainer.json         # Defines DevContainer
|    ├── Dockerfile                # Defines DevContainer
     └── sample-env                # DevContainer Variables
├── app
|    ├── mealie-backup.py          # Backup script
|    ├── requirements.txt          # Required Python packages
|    └── script.log                # Contains HTTP status code of last run; .gitignore'd
└── systemd
    ├── mealie-backup.service      # Creates and destroys Compose stack
    ├── mealie-backup.timer        # Periodically executes service file
    └── systemd-setup.sh           # Sets up systemd units
```
## Manual Commands

| Function | Command |
| ------------- | ------------- |
| Start  | ```docker compose -f /path/to/docker-compose.yml --env-file /path/to/.env up --abort-on-container-exit```  |
| Stop/Clean-up  | ```docker compose -f /path/to/docker-compose.yml --env-file /path/to/.env down```  |
