#!/usr/bin/env sh

if [ -z "$API_PORT" ]; then
  API_PORT=80
fi

uvicorn main:app --host=0.0.0.0 --port="$API_PORT" --log-level=debug
