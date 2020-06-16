#!/bin/sh

gunicorn -b localhost:8500 run:app