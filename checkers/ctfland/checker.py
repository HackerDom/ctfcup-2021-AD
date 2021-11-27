import json

from gornilo import Verdict, Checker, PutRequest, GetRequest, CheckRequest

from ctfland.client import Client, HttpError
from ctfland.data import get_random_creds, get_random_document, get_random_park_data, get_attraction_data
from ctfland.pretty_client import PrettyClient

checker = Checker()


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    try:
        client = PrettyClient(Client(request.hostname, 7777))

        login, password = get_random_creds()
        user_id = client.register_and_login(login, password, get_random_document())
        park_id = client.create_park(**get_random_park_data())

        last_parks = client.get_last_parks()
        created_park = [park for park in last_parks if park.id == park_id and park.user_id == user_id]
        if len(created_park) != 1:
            return Verdict.MUMBLE("Failed to find created park in last parks list")

        my_parks = client.get_my_parks()
        created_park = [park for park in my_parks if park.id == park_id and park.user_id == user_id]
        if len(created_park) != 1:
            return Verdict.MUMBLE("Failed to find created park in my parks list")

        park = client.add_attraction(created_park[0].id, **get_attraction_data())
        if created_park[0].attractions_count + 1 != park.attractions_count:
            return Verdict.MUMBLE(f"Failed to add attraction to park {park}")

        return Verdict.OK()
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))


@checker.define_put(vuln_num=1, vuln_rate=1)
def put_flag_into_the_service(request: PutRequest) -> Verdict:
    try:
        client = PrettyClient(Client(request.hostname, 7777))

        login, password = get_random_creds()
        user_id = client.register_and_login(login, password, request.flag)

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
def get_flag_from_the_service(request: GetRequest) -> Verdict:
    try:
        flag_id = json.loads(request.flag_id)
        client = PrettyClient(Client(request.hostname, 7777))

        user_id = client.login(flag_id["login"], flag_id["password"])
        if user_id != flag_id["user_id"]:
            return Verdict.MUMBLE("Something wrong with registration or login")

        user = client.get_profile(user_id)
        if user.document != request.flag:
            return Verdict.CORRUPT("")

        return Verdict.OK()
    except HttpError as e:
        print(e)
        return e.verdict
    except Exception as e:
        print(e)
        return Verdict.MUMBLE(str(e))
