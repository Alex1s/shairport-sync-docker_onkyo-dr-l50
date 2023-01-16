FROM python:3.11-alpine
RUN apk -U add v4l-utils
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY *.py .
EXPOSE 80
ENTRYPOINT uvicorn main:app --host=0.0.0.0 --port=80 --log-level=debug
