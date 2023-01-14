FROM python:3.11-alpine
RUN apk -U add v4l-utils rust  # rustc is needed to compile watchfiles (because no binaries available for 32 bit arm)
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /usr/src/app
COPY *.py .
ENTRYPOINT uvicorn main:app --reload --log-level=debug