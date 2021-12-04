#!/usr/bin/env python

import json
import random

from gornilo import Verdict, Checker, PutRequest, GetRequest, CheckRequest

from client import Client, HttpError
from data import get_random_creds, get_random_document, get_park_request, get_attraction_request
from models import RegisterRequest
from pretty_client import PrettyClient

checker = Checker()

START_BALANCE = 1000


@checker.define_check
def check_service(request: CheckRequest) -> Verdict:
    try:
        client = PrettyClient(Client(request.hostname, 7777))

        def check_moderator():
            login, password = get_random_creds()
            request = RegisterRequest(
                login=login,
                password=password,
                document=get_random_document()
            )
            user_id = client.register_and_login(request)
            if user_id is None:
                return Verdict.MUMBLE("Failed to register and login")

            park_id = client.create_park(get_park_request(True))
            if park_id is None:
                return Verdict.MUMBLE("Failed to create park")

            last_parks = client.get_last_parks()
            created_park = [park for park in last_parks.parks if park.id == park_id and park.user_id == user_id]
            if len(created_park) != 1:
                return Verdict.MUMBLE("Failed to find created park in last parks list")

            my_parks = client.get_my_parks()
            created_park = [park for park in my_parks.parks if park.id == park_id]
            if len(created_park) != 1:
                return Verdict.MUMBLE("Failed to find created park in my parks list")

            park = client.add_attraction(created_park[0].id, get_attraction_request())
            if created_park[0].attractions_count + 1 != park.attractions_count:
                return Verdict.MUMBLE(f"Failed to add attraction to park {park}")

            client.logout()
            return None

        def check_visitor():
            login, password = get_random_creds()
            register_request = RegisterRequest(
                login=login,
                password=password,
                document=get_random_document()
            )
            user_id = client.register_and_login(register_request)
            if user_id is None:
                return Verdict.MUMBLE("Failed to register and login")

            park_id = client.create_park(get_park_request(True))
            if park_id is None:
                return Verdict.MUMBLE("Failed to create park")
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
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag_into_the_service1(request: PutRequest) -> Verdict:
    try:
        client = PrettyClient(Client(request.hostname, 7777))

        login, password = get_random_creds()
        register_request = RegisterRequest(login=login, password=password, document=request.flag)
        user_id = client.register_and_login(register_request)
        if user_id is None:
            return Verdict.MUMBLE("Failed to register and login")

        park_id = client.create_park(get_park_request(True))
        if park_id is None:
            return Verdict.MUMBLE("Failed to create park")

        flag_id = {
            "login": login,
            "password": password,
            "user_id": user_id,
        }
        return Verdict.OK(json.dumps(flag_id))
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))


@checker.define_get(vuln_num=1)
def get_flag_from_the_service1(request: GetRequest) -> Verdict:
    try:
        flag_id = json.loads(request.flag_id)
        client = PrettyClient(Client(request.hostname, 7777))

        user_id = client.login(flag_id["login"], flag_id["password"])
        if user_id != flag_id["user_id"]:
            return Verdict.MUMBLE("Something wrong with registration or login")

        user = client.get_profile(user_id)
        if user.document != request.flag:
            return Verdict.CORRUPT("Failed to find flag")

        return Verdict.OK()
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))


@checker.define_put(vuln_num=2, vuln_rate=1)
def put_flag_into_the_service2(request: PutRequest) -> Verdict:
    try:
        client = PrettyClient(Client(request.hostname, 7777))

        login, password = get_random_creds()
        register_request = RegisterRequest(login=login, password=password, document=request.flag)
        user_id = client.register_and_login(register_request)
        if user_id is None:
            return Verdict.MUMBLE("Failed to register and login")

        park_id = client.create_park(get_park_request(True))
        if park_id is None:
            return Verdict.MUMBLE("Failed to create park")

        attraction_request = get_attraction_request()
        attraction_request.ticket = request.flag
        attraction_request.cost = random.randint(START_BALANCE + 300, START_BALANCE + 4000)
        attraction = client.add_attraction(park_id, attraction_request)
        if attraction is None:
            return Verdict.MUMBLE("Failed to add attraction to park")

        flag_id = {
            "login": login,
            "password": password,
            "user_id": user_id,
            "park_id": park_id,
        }
        return Verdict.OK(json.dumps(flag_id))
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))


@checker.define_get(vuln_num=2)
def get_flag_from_the_service2(request: GetRequest) -> Verdict:
    try:
        flag_id = json.loads(request.flag_id)
        client = PrettyClient(Client(request.hostname, 7777))

        user_id = client.login(flag_id["login"], flag_id["password"])
        if user_id != flag_id["user_id"]:
            return Verdict.MUMBLE("Something wrong with registration or login")

        my_parks = client.get_my_parks()
        created_parks = [x for x in my_parks.parks if x.id == flag_id["park_id"]]
        if not any(created_parks) and created_parks[0].attractions_count < 1:
            return Verdict.MUMBLE("Failed to created park info")
        attractions = [x for x in created_parks[0].attractions if x.ticket == request.flag]
        if len(attractions) != 1:
            return Verdict.CORRUPT("Failed to find flag")

        return Verdict.OK()
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))

checker.run()
