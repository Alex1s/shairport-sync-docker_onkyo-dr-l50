FROM mikebrady/shairport-sync:4.3.1
RUN apk add --no-cache curl=8.3.0-r0
COPY ./power /usr/local/bin/
COPY ./volume /usr/local/bin/
COPY ./shairport-sync.conf /etc/shairport-sync.conf
