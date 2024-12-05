#!/bin/bash

# Tentukan lokasi file log
LOG_FILE="/home/rahulilabs27/ai-integrated/bangkit_ai/deploy.log"

# Fungsi untuk mencatat ke log
log() {
  echo "$(date "+%Y-%m-%d %H:%M:%S") - $1" >> $LOG_FILE
}

# Pastikan direktori dan file log memiliki izin yang benar
log "Verifying log file permissions..."

# Memastikan bahwa file log dapat ditulis
if [ ! -w "$LOG_FILE" ]; then
  log "Log file is not writable. Attempting to set proper permissions..."
  
  # Jika file log tidak dapat ditulis, berikan izin menulis pada file log
  sudo chmod u+w "$LOG_FILE"
  sudo chown $(whoami):$(whoami) "$LOG_FILE"  # Pastikan file log dimiliki oleh user yang menjalankan skrip
fi

# Pastikan direktori tempat file log berada memiliki izin yang benar
log "Verifying directory permissions..."

if [ ! -w "$(dirname "$LOG_FILE")" ]; then
  log "Directory is not writable. Attempting to set proper permissions..."
  
  # Jika direktori log tidak bisa diakses, beri izin menulis
  sudo chmod u+w "$(dirname "$LOG_FILE")"
  sudo chown -R $(whoami):$(whoami) "$(dirname "$LOG_FILE")"  # Pastikan direktori dimiliki oleh user yang menjalankan skrip
fi

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
