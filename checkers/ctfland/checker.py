#!/usr/bin/env python3.9

import json
import random

from gornilo import Verdict, Checker, PutRequest, GetRequest, CheckRequest

from client import Client, HttpError
from data import get_random_creds, get_park_request, get_attraction_request, get_register_request
from models import RegisterRequest
from pretty_client import PrettyClient

checker = Checker()

START_BALANCE = 1000


def handle_exception(request_type):
    def handle_exception_inner(f: callable):
        def wrapped(request: request_type, *args, **kwargs) -> Verdict:
            try:
                return f(request, *args, **kwargs)
            except HttpError as e:
                print(e)
                return e.verdict
            except Exception as e:
                print(e)
                return Verdict.MUMBLE("Something went wrong")

        return wrapped

    return handle_exception_inner


def get_client(hostname: str):
    parts = hostname.split(":", 2)
    return PrettyClient(Client(parts[0], parts[1] if len(parts) > 1 else 7777))


def create_random_user(client: PrettyClient):
    user_id = client.register_and_login(get_register_request())
    return user_id


@checker.define_check
@handle_exception(CheckRequest)
def check_service(request: CheckRequest) -> Verdict:
    client = get_client(request.hostname)

    def check_moderator():
        user_id = create_random_user(client)
        if user_id is None:
            return Verdict.MUMBLE("Failed to register and login")

        park_request = get_park_request(True)
        park_id = client.create_park(park_request)
        if park_id is None:
            return Verdict.MUMBLE(f"Failed to create park {park_request}")

        last_parks = client.get_last_parks()
        created_park = [park for park in last_parks.parks if park.id == park_id and park.user_id == user_id]
        if len(created_park) != 1:
            return Verdict.MUMBLE("Failed to find created park in last parks list")

        my_parks = client.get_my_parks()
        created_park = [park for park in my_parks.parks if park.id == park_id]
        if len(created_park) != 1:
            return Verdict.MUMBLE("Failed to find created park in my parks list")

        (park, attraction) = client.add_attraction(created_park[0].id, get_attraction_request())
        if created_park[0].attractions_count + 1 != park.attractions_count:
            return Verdict.MUMBLE(f"Failed to add attraction to park {park}")

        client.logout()
        return None

    def check_visitor():
        user_id = create_random_user(client)
        if user_id is None:
            return Verdict.MUMBLE("Failed to register and login")

        park_request = get_park_request(True)
        park_id = client.create_park(park_request)
        if park_id is None:
            return Verdict.MUMBLE(f"Failed to create park {park_request}")
        attraction_request = get_attraction_request()
        attraction_request.cost = 15
        client.add_attraction(park_id, attraction_request)

        last_parks = client.get_last_parks()
        created_parks = [park for park in last_parks.parks if park.id == park_id]
        if not any(created_parks):
            return Verdict.MUMBLE("Failed to find created park in last parks")
        park = client.get_park(park_id)

        user_info = client.buy_ticket(park.attractions_ids[0], user_id)
        if not any([x for x in user_info.purchasesInfo.purchases if x.name == attraction_request.name and x.ticket == attraction_request.ticket]):
            return Verdict.MUMBLE("Failed to find bought ticket")

        return None

    verdict_maybe = check_moderator()
    if verdict_maybe is not None:
        return verdict_maybe

    verdict_maybe = check_visitor()
    if verdict_maybe is not None:
        return verdict_maybe

    return Verdict.OK()


@checker.define_put(vuln_num=1, vuln_rate=1)
@handle_exception(PutRequest)
def put_flag_into_the_service1(request: PutRequest) -> Verdict:
    client = get_client(request.hostname)

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document=request.flag)
    user_id = client.register_and_login(register_request)
    if user_id is None:
        return Verdict.MUMBLE("Failed to register and login")

    park_request = get_park_request(True)
    park_id = client.create_park(park_request)
    if park_id is None:
        return Verdict.MUMBLE(f"Failed to create park {park_request}")

    flag_id = {
        "login": login,
        "password": password,
        "user_id": user_id,
    }
    return Verdict.OK(json.dumps(flag_id))


@checker.define_get(vuln_num=1)
@handle_exception(GetRequest)
def get_flag_from_the_service1(request: GetRequest) -> Verdict:
    flag_id = json.loads(request.flag_id)
    client = get_client(request.hostname)

    user_id = client.login(flag_id["login"], flag_id["password"])
    if user_id != flag_id["user_id"]:
        return Verdict.MUMBLE("Something wrong with registration or login")

    user = client.get_profile(user_id)
    if user.document != request.flag:
        return Verdict.CORRUPT("Failed to find flag")

    return Verdict.OK()


@checker.define_put(vuln_num=2, vuln_rate=1)
@handle_exception(PutRequest)
def put_flag_into_the_service2(request: PutRequest) -> Verdict:
    client = get_client(request.hostname)

    register_request = get_register_request()
    user_id = client.register_and_login(register_request)
    if user_id is None:
        return Verdict.MUMBLE("Failed to register and login")

    park_request = get_park_request(True)
    park_id = client.create_park(park_request)
    if park_id is None:
        return Verdict.MUMBLE(f"Failed to create park {park_request}")

    attraction_request = get_attraction_request()
    attraction_request.ticket = request.flag
    attraction_request.cost = random.randint(START_BALANCE + 300, START_BALANCE + 4000)
    attraction = client.add_attraction(park_id, attraction_request)
    if attraction is None:
        return Verdict.MUMBLE("Failed to add attraction to park")

    flag_id = {
        "login": register_request.login,
        "password": register_request.password,
        "user_id": user_id,
        "park_id": park_id,
    }
    return Verdict.OK(json.dumps(flag_id))


@checker.define_get(vuln_num=2)
@handle_exception(GetRequest)
def get_flag_from_the_service2(request: GetRequest) -> Verdict:
    flag_id = json.loads(request.flag_id)
    client = get_client(request.hostname)

    user_id = client.login(flag_id["login"], flag_id["password"])
    if user_id != flag_id["user_id"]:
        return Verdict.MUMBLE("Something wrong with registration or login")

    my_parks = client.get_my_parks()
    created_parks = [x for x in my_parks.parks if x.id == flag_id["park_id"]]
    if not any(created_parks) and created_parks[0].attractions_count < 1:
        return Verdict.MUMBLE("Failed to created park info")
    attractions = [x for x in created_parks[0].attractions if x.ticket == request.flag]
    if len(attractions) == 0:
        return Verdict.CORRUPT("Failed to find flag")

    return Verdict.OK()

checker.run()
