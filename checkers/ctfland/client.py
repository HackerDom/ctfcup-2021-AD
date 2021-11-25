import requests

THROTTLING_RESPONSE_CODE = 429


class Client:
    def __init__(self, host, port, retries_count=3):
        self._session = requests.Session()
        self.host = host
        self.port = port
        self.retries_count = retries_count

    def register(self, login, password, document):
        data = {"Login": login, "Password": password, "RepeatedPassword": password, "Document": document}
        return self._wrapped_post("auth/register", data=data)

    def login(self, login, password):
        data = {"Login": login, "Password": password}
        return self._wrapped_post("auth/login", data=data)

    def create_park(self, name, description, email, max_visitors, attraction_block, is_public):
        data = {
            "Name": name,
            "Description": description,
            "Email": email,
            "MaxVisitorsCount": max_visitors,
            "HtmlAttractionBlock": attraction_block,
            "IsPublic": is_public,
        }
        return self._wrapped_post("park/create", data=data)

    def add_attraction(self, park_id, name, description, cost):
        data = {
            "Name": name,
            "Description": description,
            "Cost": cost,
        }
        return self._wrapped_post(f"park/{park_id}/addAttraction", data=data)

    def get_my_parks(self, skip, take):
        return self._get("park/my", params={"skip": skip, "take": take})

    def get_last_parks(self, skip, take):
        return self._get("park", params={"skip": skip, "take": take})

    @staticmethod
    def _result(r, failed_url):
        return None if r is None or r.url == failed_url else r

    def _get_address(self):
        return f"http://{self.host}:{self.port}/"

    def _get(self, relative_url, **kwargs):
        return self._send(self._session.get, relative_url, **kwargs)

    def _wrapped_post(self, relative_url, **kwargs):
        r = self._post(relative_url, **kwargs)
        is_validation_failed = r is not None and r.url == relative_url
        if r is None or is_validation_failed:
            return None

        return r

    def _post(self, relative_url, **kwargs):
        return self._send(self._session.post, relative_url, **kwargs)

    def _send(self, method, relative_url, **kwargs):
        url = self._get_address() + relative_url
        print(f"Sending '{method.__name__}' method to '{url}'")

        for i in range(self.retries_count):
            print(f"Attempt #{i+1}")
            r = method(url, allow_redirects=True, **kwargs)
            if r.status_code == THROTTLING_RESPONSE_CODE:
                print(f"Rejected by throttling. Will try again.")
                continue

            if r.status_code >= 400:
                print(f"Failed! See more:\r\n {r.__dict__}")
                return None

            return r

        print("All attempts are failed!")
        return None
