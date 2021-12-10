import requests
from gornilo import Verdict

from models import *

THROTTLING_RESPONSE_CODE = 429


class HttpError(Exception):
    def __init__(self, verdict: Verdict, *args, **kwargs):
        super(*args, **kwargs)
        self.verdict = verdict

    def __str__(self):
        return str(self.verdict)


class Client:
    def __init__(self, host, port, retries_count=3):
        self._session = requests.Session()
        self.host = host
        self.port = port
        self.retries_count = retries_count

    def register(self, request: RegisterRequest):
        data = {
            "Login": request.login,
            "Password": request.password,
            "RepeatedPassword": request.password,
            "Document": request.document,
        }
        return self._wrapped_post("auth/register", data=data)

    def login(self, login, password):
        data = {"Login": login, "Password": password}
        return self._wrapped_post("auth/login", data=data)

    def create_park(self, request: CreateParkRequest):
        data = {
            "Name": request.name,
            "Description": request.description,
            "Email": request.email,
            "MaxVisitorsCount": request.max_visitors,
            "HtmlAttractionBlock": request.attraction_block,
            "IsPublic": request.is_public,
        }
        return self._wrapped_post("park/create", data=data)

    def add_attraction(self, park_id, request: AddAttractionRequest):
        data = {
            "Name": request.name,
            "Description": request.description,
            "Cost": request.cost,
            "TicketKey": request.ticket,
        }
        return self._wrapped_post(f"attraction/{park_id}/add", data=data)

    def get_my_parks(self, skip, take):
        return self._get("park/my", params={"skip": skip, "take": take})

    def get_last_parks(self, skip, take):
        return self._get("park", params={"skip": skip, "take": take})

    def get_profile(self, user_id):
        return self._get(f"auth/profile/{user_id}")

    def get_park(self, park_id):
        return self._get(f"park/{park_id}")

    def logout(self):
        return self._post("auth/logout")

    def buy_ticket(self, attraction_id):
        return self._wrapped_post(f"attraction/{attraction_id}/buy")

    @staticmethod
    def _result(r, failed_url):
        return None if r is None or r.url == failed_url else r

    def _get_address(self):
        return f"http://{self.host}:{self.port}/"

    def _get(self, relative_url, **kwargs):
        return self._send(self._session.get, relative_url, **kwargs)

    def _wrapped_post(self, relative_url, **kwargs):
        r = self._post(relative_url, **kwargs)
        is_validation_failed = r.url.endswith(relative_url)
        if is_validation_failed:
            return None

        return r

    def _post(self, relative_url, **kwargs):
        return self._send(self._session.post, relative_url, **kwargs)

    def _send(self, method, relative_url, **kwargs):
        url = self._get_address() + relative_url
        print(f"Sending '{method.__name__}' method to '{relative_url}'")

        for i in range(self.retries_count):
            print(f"Attempt #{i+1}/{self.retries_count}")
            try:
                r = method(url, allow_redirects=True, **kwargs)
            except requests.RequestException as e:
                print(e)
                raise HttpError(Verdict.DOWN(f"Failed to send request to {relative_url}"))

            if r.status_code == THROTTLING_RESPONSE_CODE:
                print(f"Rejected by throttling. Will try again.")
                continue

            if r.status_code >= 400:
                print(f"Request to {relative_url} failed with status code {r.status_code}. See more:\r\n{r.__dict__}")
                verdict = Verdict.DOWN if r.status_code in [502, 503] else Verdict.MUMBLE
                raise HttpError(verdict(f"Request to {relative_url} failed with status code {r.status_code}"))

            return r

        raise HttpError(Verdict.DOWN(f"Request to {relative_url} rejected by throttling too many times."))
