FROM mikebrady/shairport-sync:4.3.4
RUN apk add --no-cache curl
COPY ./power /usr/local/bin/
COPY ./volume /usr/local/bin/
COPY ./shairport-sync.conf /etc/shairport-sync.conf
