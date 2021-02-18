#!/bin/sh

gunicorn -c gunicorn_config.py "app.main:app" -k uvicorn.workers.UvicornWorker
