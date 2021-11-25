from ctfland.client import Client
from bs4 import BeautifulSoup


class PrettyClient:
    def __init__(self, client: Client):
        self._client = client

    def login(self, login, password):
        return self._client.login(login, password)

    def register_and_login(self, login, password, document):
        r = self._client.register(login, password, document)
        if r is None:
            return None
        r = self._client.login(login, password)
        if r is None:
            return None

        soup = BeautifulSoup(r.text, 'lxml')
        user_id = soup.header.select("a.nav-link")[3]['href'].split("/")[-1]
        return user_id

    def create_park(self, name, description, email, max_visitors, attraction_block, is_public):
        r = self._client.create_park(name, description, email, max_visitors, attraction_block, is_public)
        if r is None:
            return None

        park_id = r.url.split('/')[-1]
        return park_id, r

    def get_my_parks(self, skip=0, take=100):
        r = self._client.get_my_parks(skip, take)
        if r is None:
            return None

        soup = BeautifulSoup(r.text, 'lxml')
        return list(map(self._parse_park_item, soup.select(".park-list-item")))

    def get_last_parks(self, skip=0, take=100):
        r = self._client.get_last_parks(skip, take)
        if r is None:
            return None

        soup = BeautifulSoup(r.text, 'lxml')
        return list(map(self._parse_park_item, soup.select(".park-list-item")))

    @staticmethod
    def _parse_park_item(item):
        ps = item.find_all('p')
        is_author_exists = len(ps) > 2
        return {
            "id": item.h3.a['href'].split('/')[-1],
            "name": item.h3.a.string,
            "max_visitors": int(ps[-1].string.split(": ")[-1]),
            "attractions_count": int(ps[-2].string.split(": ")[-1]),
            "user_id": ps[0].a['href'].split('/')[-1] if is_author_exists else None
        }
