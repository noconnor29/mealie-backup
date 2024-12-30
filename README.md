# mealie-backup
Project to automate [Mealie Recipe Manager](https://github.com/mealie-recipes/mealie) backups with a Python script via the Mealie API. Builds a Docker container to run the script and contains a Docker Compose to spin up the container and a Tailscale sidecar.

## Directory Structure
```
mealie-backup
├── docker-compose.yml
├── Dockerfile
└── app
    ├── mealie-backup.py
    ├── script.log
    └── requirements.txt

mealie-backup-ts
└── state
```
## Commands
Start

```sudo docker compose -f docker-compose.yml --env-file .env up --abort-on-container-exit```

Clean 

```sudo docker compose -f docker-compose.yml --env-file .env down```
