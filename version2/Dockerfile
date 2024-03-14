FROM alpine:latest
RUN apk --no-cache add netcat-openbsd bash
COPY listener.sh /listener.sh
RUN chmod +x /listener.sh
CMD ["/listener.sh"]
