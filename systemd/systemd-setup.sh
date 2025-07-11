#!/bin/bash

# Define paths for the systemd unit files
SERVICE_FILE="mealie-backup.service"
TIMER_FILE="mealie-backup.timer"
SYSTEMD_DIR="/etc/systemd/system"

# Copy the service and timer files to /etc/systemd/system
echo "Copying $SERVICE_FILE and $TIMER_FILE to $SYSTEMD_DIR..."
sudo cp $SERVICE_FILE $TIMER_FILE $SYSTEMD_DIR

# Reload systemd to recognize the new files
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the service
echo "Enabling and starting $SERVICE_FILE..."
sudo systemctl enable $SERVICE_FILE
sudo systemctl start $SERVICE_FILE

# Enable and start the timer. Necessary?
echo "Enabling and starting $TIMER_FILE..."
sudo systemctl enable $TIMER_FILE
sudo systemctl start $TIMER_FILE 

# Check the status of the service and timer
echo "Checking the status of $SERVICE_FILE and $TIMER_FILE..."
sudo systemctl status $SERVICE_FILE
sudo systemctl status $TIMER_FILE.

echo "Done!"
