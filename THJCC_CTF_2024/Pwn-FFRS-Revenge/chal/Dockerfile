FROM ubuntu@sha256:a6d2b38300ce017add71440577d5b0a90460d0e57fd7aec21dd0d1b0761bbfb2

RUN apt-get update && \
    DEBAIN_FRONTEND=noninteractive apt-get install -qy gcc gcc-multilib xinetd

RUN useradd -m chal
RUN chown -R root:root /home/chal
RUN chmod -R 755 /home/chal

CMD ["/usr/sbin/xinetd", "-dontfork"]
