#!/bin/bash
cd /home/egor/checkmind/backend
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 main:app
