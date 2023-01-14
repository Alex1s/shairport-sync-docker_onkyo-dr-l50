FROM python:3.11-alpine
RUN apk -U add v4l-utils
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /usr/src/app
COPY *.py .
RUN uvicorn main:app --reload --log-level=debug