# mealie-backup
Project to automate [Mealie Recipe Manager](https://github.com/mealie-recipes/mealie) backups with a Python script via the Mealie API. Builds a Docker container to run the script and contains a Docker Compose to spin up the container and a Tailscale sidecar.

Also included are systemd units to schedule and execute the compose file weekly.

## Structure
```
mealie-backup
├── docker-compose.yml             # Executes backup stack
├── Dockerfile                     # Builds app container w/ Python env
├── app
|    ├── mealie-backup.py          # Backup script
|    ├── script.log                # Contains HTTP status code of last run
|    └── requirements.txt          # Required Python packages
└── systemd
    ├── mealie-backup.service      # Creates and destroys Compose stack
    └── mealie-backup.timer        # Periodically executes service file
```
## Manual Commands

| Function | Command |
| ------------- | ------------- |
| Start  | ```docker compose -f /path/to/docker-compose.yml --env-file /path/to/.env up --abort-on-container-exit```  |
| Stop/Clean-up  | ```docker compose -f /path/to/docker-compose.yml --env-file /path/to/.env down```  |
