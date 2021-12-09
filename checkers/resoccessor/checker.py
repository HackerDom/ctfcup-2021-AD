#!/usr/bin/env python3.9
import functools
import json
import sys

import requests
import traceback

from gornilo import CheckRequest, Verdict, Checker, PutRequest, GetRequest

from generators import gen_string, gen_user_agent, gen_schema

checker = Checker()


REGISTER_URL = "http://{hostname}:{port}/register"
LOGIN_URL = "http://{hostname}:{port}/login"
GEN_TOKEN_URL = "http://{hostname}:{port}/gen_token"
UPLOAD_RESOURCE_URL = "http://{hostname}:{port}/upload_resource"
LIST_RESOURCES_URL = "http://{hostname}:{port}/list_resources"
SET_SCHEMA_URL = "http://{hostname}:{port}/set_schema/{resource_uuid}"
GET_RESOURCE_URL = "http://{hostname}:{port}/get_resource/{resource_uuid}?token={token}"


def patch_hostport(func):
    def res_func(hostport, *args):
        host, port = hostport.split(":")
        return func(host, port, *args)
    return res_func


def get_creds(url_template, hostname, port, username, password):
    session = requests.Session()
    url = url_template.format(hostname=hostname, port=port)
    data = {
        "name": username,
        "password": password,
    }
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, json=data)
    r.raise_for_status()
    return session


register = patch_hostport(functools.partial(get_creds, REGISTER_URL))


@patch_hostport
def gen_token(hostname, port, session):
    url = GEN_TOKEN_URL.format(hostname=hostname, port=port)
    r = session.post(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    data = json.loads(r.content)
    if not isinstance(data, dict):
        raise IncorrectDataError(f"Incorrect data type: {type(data)}")
    if 'token' not in data or 'count' not in data:
        raise IncorrectDataError(f"There is no 'token' or 'count' in data: {data}")
    return data['token'], data['count']


@patch_hostport
def upload_resource(hostname, port, session, data):
    url = UPLOAD_RESOURCE_URL.format(hostname=hostname, port=port)
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, data=data)
    r.raise_for_status()
    return r.content.decode()


@patch_hostport
def list_resources(hostname, port, session):
    url = LIST_RESOURCES_URL.format(hostname=hostname, port=port)
    r = session.post(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    resources = json.loads(r.content.decode())
    if not isinstance(resources, list):
        raise IncorrectDataError(f"resources has wrong type: {type(resources)}")
    return resources


@patch_hostport
def set_schema(hostname, port, session, resource_uuid, schema):
    url = SET_SCHEMA_URL.format(hostname=hostname, port=port, resource_uuid=resource_uuid)
    r = session.post(url, headers={'User-Agent': gen_user_agent()}, json=schema)
    r.raise_for_status()


@patch_hostport
def get_resource(hostname, port, token, resource_uuid):
    url = GET_RESOURCE_URL.format(hostname=hostname, port=port, resource_uuid=resource_uuid, token=token)
    r = requests.get(url, headers={'User-Agent': gen_user_agent()})
    r.raise_for_status()
    return r.content.decode()


class IncorrectDataError(Exception):
    pass


DOWN_ERRORS = {requests.exceptions.ConnectionError, ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError}
INCORRECT_HTTP_ERRORS = {requests.exceptions.HTTPError}
INCORRECT_DATA_ERRORS = {IncorrectDataError, UnicodeError, json.JSONDecodeError}
KNOWN_ERRORS = DOWN_ERRORS | INCORRECT_HTTP_ERRORS | INCORRECT_DATA_ERRORS


class NetworkChecker:
    def __init__(self):
        self.verdict = Verdict.OK()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type in DOWN_ERRORS:
            self.verdict = Verdict.DOWN("Service is down")
        if exc_type in INCORRECT_HTTP_ERRORS:
            self.verdict = Verdict.MUMBLE(f"Incorrect http code")
        if exc_type in INCORRECT_DATA_ERRORS:
            self.verdict = Verdict.MUMBLE(f"Incorrect data format")

        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)
            traceback.print_tb(exc_traceback, file=sys.stdout)

        if exc_type and exc_type not in KNOWN_ERRORS:
            self.verdict = Verdict.CHECKER_ERROR("Checker error")
        return True


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag(request: PutRequest) -> Verdict:
    with NetworkChecker() as nc:
        username, password = gen_string(), gen_string()
        session = register(request.hostname, username, password)

        token = None
        count = None
        schema, user_id = gen_schema()
        while count != user_id:
            token, count = gen_token(request.hostname, session)

        resource_uuid = upload_resource(request.hostname, session, request.flag)
        resource_uuids = list_resources(request.hostname, session)

        if len(resource_uuids) != 1:
            raise IncorrectDataError(f"len(resource_uuids) = {resource_uuids}")

        if resource_uuids[0] != resource_uuid:
            raise IncorrectDataError(f"different resource uuids: {resource_uuids[0]} and {resource_uuid}")

        set_schema(request.hostname, session, resource_uuid, schema)
        flag_id = f"{token}:{resource_uuid}"

        nc.verdict = Verdict.OK(flag_id)
    return nc.verdict


@checker.define_get(vuln_num=1)
def get_flag(request: GetRequest) -> Verdict:
    with NetworkChecker() as nc:
        token, resource_uuid = request.flag_id.strip().split(":")
        real_flag = get_resource(request.hostname, token, resource_uuid)

        if request.flag != real_flag:
            print(f"Different flags, expected: {request.flag}, real: {real_flag}")
            return Verdict.CORRUPT("Corrupt flag")
        nc.verdict = Verdict.OK()
    return nc.verdict


if __name__ == '__main__':
    checker.run()
