#!/bin/bash

# Tentukan lokasi file log
LOG_FILE="/home/rahulilabs27/ai-integrated/bangkit_ai/deploy.log"

# Fungsi untuk mencatat ke log
log() {
  echo "$(date "+%Y-%m-%d %H:%M:%S") - $1" >> $LOG_FILE
}

# Mulai logging
log "Starting deployment..."

# Stop Gunicorn jika berjalan
log "Stopping Gunicorn..."
pkill gunicorn || log "Gunicorn not running or failed to stop"

log "Pulling latest changes from GitHub..."
sudo git pull origin main >> $LOG_FILE 2>&1

# Install dependencies dari requirements.txt
log "Installing dependencies from requirements.txt..."
pip install -r requirements.txt >> $LOG_FILE 2>&1

# Mulai Gunicorn dengan log ke file
log "Starting Gunicorn..."
gunicorn -w 1 -b 0.0.0.0:8080 main:app >> $LOG_FILE 2>&1 &

log "Deployment completed successfully!"
