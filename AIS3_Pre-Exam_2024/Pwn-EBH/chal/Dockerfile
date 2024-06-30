FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq python3 python3-pip sqlite3 qemu-system-x86
RUN pip3 install flask

RUN useradd -m user
RUN mkdir -p /home/user/web /home/user/challenge
COPY --chown=user:user ./web /home/user/web
COPY --chown=user:user ./challenge /home/user/challenge

WORKDIR /home/user/web
RUN sqlite3 EBH.db < init.sql
RUN mkdir -p uploads

CMD ["flask", "run", "--host=0.0.0.0"]
