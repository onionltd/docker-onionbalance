#!/usr/bin/env python3

import base64
import ipaddress
import socket
import re
import yaml

from os import environ
from os import execvp
from os import makedirs
from sys import argv


def resolve_hostname(hostname):
    try:
        _ = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            addr = socket.getaddrinfo(hostname, None, socket.AF_INET,
                                      socket.SOCK_STREAM, socket.IPPROTO_TCP)
            return addr[0][4][0]
        except socket.gaierror:
            return None
    return hostname


def main():
    if 'CONFIG_FILE' not in environ:
        raise Exception('CONFIG_FILE not defined')

    if 'TOR_CONTROL_IP' in environ:
        address = resolve_hostname(environ['TOR_CONTROL_IP'])
        if address is None:
            raise Exception('TOR_CONTROL_IP failed to resolve hostname')
        environ['TOR_CONTROL_IP'] = address
    else:
        raise Exception('TOR_CONTROL_IP not defined')

    if 'TOR_CONTROL_PORT' not in environ:
        raise Exception('TOR_CONTROL_PORT not defined')

    dirname = "hskeys"
    makedirs(dirname, exist_ok=True)

    data = {}

    for var in environ:
        match = re.search('(.*)_TOR_SERVICE_KEY|(.*)_TOR_SERVICE_NODE_(.*)', var)

        if match == None:
            continue

        service_name = match.group(1).lower() if match.group(1) else match.group(2).lower()

        if service_name not in data:
            data[service_name] = {}

        if match.group(1):
            file = "{}/{}.key".format(dirname, service_name)
            key = base64.b64decode(environ[var])

            with open(file, 'wb') as fd:
                fd.write(key)

            data[service_name]['key'] = file
        else:
            node_name = match.group(3).lower()
            address = environ[var]

            if "instances" not in data[service_name]:
                data[service_name]['instances'] = []

            data[service_name]['instances'].append({'address': address, 'name': 'node {}'.format(node_name)})

    config = {'services': []}

    for service_name in data:
        config['services'].append(data[service_name])

    with open(environ['CONFIG_FILE'], 'w') as fd:
        fd.write(yaml.dump(config))

    if len(argv) > 1:
        execvp(argv[1], argv[1:])

if __name__ == '__main__':
    main()
