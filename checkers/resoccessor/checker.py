#!/usr/bin/env python3
import functools
import json
import re
import sys

import requests
import traceback

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

from generators import gen_string, gen_user_agent

checker = Checker()


PORT = 8080


REGISTER_URL = "http://{hostname}:{port}/register"
LOGIN_URL = "http://{hostname}:{port}/login"
GEN_TOKEN_URL = "http://{hostname}:{port}/gen_token"
UPLOAD_RESOURCE_URL = "http://{hostname}:{port}/upload_resource"
LIST_RESOURCES_URL = "http://{hostname}:{port}/list_resources"
SET_SCHEMA_URL = "http://{hostname}:{port}/set_schema/{resource_uuid}"
GET_RESOURCE_URL = "http://{hostname}:{port}/get_resource/{resource_uuid}?token={token}"


def get_creds(url_template, hostname, username, password):
    session = requests.Session()
    url = url_template.format(hostname=hostname, port=PORT)
    data = {
        "name": username,
        "password": password,
    }
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, json=data)
    r.raise_for_status()
    return session


login = functools.partial(get_creds, LOGIN_URL)
register = functools.partial(get_creds, REGISTER_URL)


def gen_token(hostname, session):
    url = GEN_TOKEN_URL.format(hostname=hostname, port=PORT)
    r = session.post(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    data = json.loads(r.content)
    if not isinstance(data, dict):
        raise IncorrectDataError(f"Incorrect data type: {type(data)}")
    if 'token' not in data or 'count' not in data:
        raise IncorrectDataError(f"There is no 'token' or 'count' in data: {data}")
    return data['token'], data['count']


def upload_resource(hostname, session, data):
    url = UPLOAD_RESOURCE_URL.format(hostname=hostname, port=PORT)
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, data=data)
    r.raise_for_status()
    return r.content.decode()


def list_resources(hostname, session):
    url = LIST_RESOURCES_URL.format(hostname=hostname, port=PORT)
    r = session.post(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    resources = json.loads(r.content.decode())
    if not isinstance(resources, list):
        raise IncorrectDataError(f"resources has wrong type: {type(resources)}")
    return resources


def set_schema(hostname, session, resource_uuid, schema):
    url = SET_SCHEMA_URL.format(hostname=hostname, port=PORT, resource_uuid=resource_uuid)
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, json=schema)
    r.raise_for_status()


def get_resource(hostname, token, resource_uuid):
    url = GET_RESOURCE_URL.format(hostname=hostname, port=PORT, resource_uuid=resource_uuid, token=token)
    r = requests.get(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    return r.content.decode()


class IncorrectDataError(Exception):
    pass


class NetworkChecker:
    def __init__(self):
        self.verdict = Verdict.OK()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type in {requests.exceptions.ConnectionError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError}:
            self.verdict = Verdict.DOWN("Service is down")
        if exc_type in {requests.exceptions.HTTPError}:
            self.verdict = Verdict.MUMBLE(f"Incorrect http code")
        if exc_type in {IncorrectDataError, UnicodeError, json.JSONDecodeError}:
            self.verdict = Verdict.MUMBLE(f"Incorrect data format")

        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)
            traceback.print_tb(exc_traceback, file=sys.stdout)
        return True


def main():
    name, password = gen_string(), gen_string()
    print(name, password)
    hostname = "127.0.0.1"
    session = register(hostname, name, password)
    token, count = gen_token(hostname, session)
    print(token, count)
    print(upload_resource(hostname, session, b'Content!'))
    resource_uuid = list_resources(hostname, session)[0]
    schema = {"groups": [[0, 1, 2], [0, 1, 2], [1, 2]], "rules": [[1, 1, 1]]}
    set_schema(hostname, session, resource_uuid, schema)
    print(get_resource(hostname, token, resource_uuid))


if __name__ == '__main__':
    main()
