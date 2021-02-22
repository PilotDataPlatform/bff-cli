#!/bin/sh

gunicorn -c gunicorn_config.py "run:app" -k uvicorn.workers.UvicornWorker
