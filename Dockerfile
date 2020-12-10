FROM alpine:latest

RUN apk add --no-cache git build-base py3-pip py3-wheel py3-yaml python3 python3-dev libffi-dev openssl-dev py-setuptools

RUN git clone --depth 1 https://gitlab.torproject.org/asn/onionbalance
RUN cd onionbalance && python3 setup.py install && cd -

# TODO: cleanup!
COPY rootfs /

RUN addgroup -S -g 107 tor \
    && adduser -S -G tor -u 104 tor

USER tor

WORKDIR /home/tor

ENV CONFIG_FILE=/home/tor/onionbalance.yaml

ENTRYPOINT ["python3", "/entrypoint.py"]

CMD onionbalance --ip "$TOR_CONTROL_IP" --port "$TOR_CONTROL_PORT" --config "$CONFIG_FILE"
