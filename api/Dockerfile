FROM python:3.11-alpine
RUN apk --no-cache add v4l-utils
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./entrypoint.sh /
COPY *.py .
EXPOSE 80
ENTRYPOINT /entrypoint.sh
