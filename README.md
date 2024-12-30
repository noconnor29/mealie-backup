# mealie-backup

## Directory Structure
mealie-backup
├── docker-compose.yml
├── Dockerfile
└── app
    ├── mealie-backup.py
    ├── script.log
    └── requirements.txt

mealie-backup-ts
└── state

## Commands
Start
```sudo docker compose -f docker-compose.yml --env-file .env up --abort-on-container-exit```

Clean Up
```sudo docker compose -f docker-compose.yml --env-file .env down```
