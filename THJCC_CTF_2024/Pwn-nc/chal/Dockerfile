FROM alpine:3.18

RUN apk add --no-cache python3 socat

RUN mkdir -p /chal
WORKDIR /chal

COPY ./src /chal

CMD ["socat", "TCP-LISTEN:20000,fork", "EXEC:'timeout 10 python3 server.py'"]