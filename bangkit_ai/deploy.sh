#!/bin/bash

# Stop Gunicorn
pkill gunicorn

# Install pip requirements
pip install -r requirements.txt

# Start Gunicorn
gunicorn -w 1 -b 0.0.0.0:8080 main:app
