#!/usr/bin/env sh

if [ -z "$API_PORT" ]; then
  API_PORT=80
fi

if [ -z "$UVICORN_LOG_LEVEL" ]; then
  UVICORN_LOG_LEVEL=debug
fi

uvicorn main:app --host=0.0.0.0 --port="$API_PORT" --log-level="$UVICORN_LOG_LEVEL"
