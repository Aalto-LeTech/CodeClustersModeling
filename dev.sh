#!/usr/bin/env bash

# FLASK_DEBUG=1 python3 run.py
FLASK_APP=run.py FLASK_ENV=development python3 -m flask run --port 8500
