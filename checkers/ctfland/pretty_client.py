from pydantic import BaseModel
import typing as t

from ctfland.client import Client
from bs4 import BeautifulSoup


class ParkItem(BaseModel):
    id: str
    name: str
    max_visitors: int
    attractions_count: int
    user_id: t.Optional[str]


class User(BaseModel):
    id: str
    login: str
    document: str


X = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>&#x41C;&#x43E;&#x439; &#x43F;&#x440;&#x43E;&#x444;&#x438;&#x43B;&#x44C; - CtfLand</title>
    <link rel="stylesheet" href="/lib/bootstrap/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="/css/site.css" />
<script type="text/javascript" src="http://ff.kis.v2.scr.kaspersky-labs.com/FD126C42-EBFA-4E12-B309-BB3FDD723AC1/main.js?attr=QTgIea1fGGLI79w3AwSOsg8CD18MRaKvS3AEtleqknkBKWohJy-Ves4-evqMntTykNc7_rCE8Wqrj-DAiYILkXDIZELCkOjelmCXoJL5qRpSEG1UHHPyGea3YStsvCpy" charset="UTF-8"></script></head>
<body>
    <header>
    <nav class="navbar navbar-expand-sm navbar-toggleable-sm navbar-light bg-white border-bottom box-shadow mb-3">
        <div class="container">
            <a class="navbar-brand" href="/">CtfLand</a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target=".navbar-collapse" aria-controls="navbarSupportedContent"
                    aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="navbar-collapse collapse d-sm-inline-flex justify-content-between">
                <ul class="navbar-nav flex-grow-1">
                        <li class="nav-item">
                            <a class="nav-link text-dark" href="/park">Новые парки</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-dark" href="/park/my">Мои парки</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-dark" href="/park/create">Создать парк</a>
                        </li>
                </ul>
                <ul class="navbar-nav">
    <li class="nav-item">
        <a class="nav-link" href="/auth/profile/9fcb22b8-cbf0-4ea8-ad1d-54fa0c7b6ae6">
            Привет, leo
        </a>
    </li>
    <li class="nav-item">
        <form class="form-inline" action="/auth/logout?returnUrl=%2F" method="post">
            <button  type="submit" class="nav-link btn btn-link text-dark">Выйти</button>
        <input name="__RequestVerificationToken" type="hidden" value="CfDJ8BMhf7_ZEBtCj8x_ksXhwJnfzR6aiqQE3Kfii_jczLU2lPrTCb3e605NPikYFLQ_RAtm019ddJM81m-xst6AEAhpg_CuIfUy4HrQLzZLSQbYf63FxIJD7aB9Tbx_O_zfo2ZrVSRCWUYcmmqQDUR03WQHJ14ZddqmXSmCPpBkv2YFh_JfKtfYdaZZfOok1Y3lpQ" /></form>
    </li>
</ul>

            </div>
        </div>
    </nav>
</header>


    <div class="container">
        <main role="main" class="pb-3">
            

<h2 class="title">&#x41C;&#x43E;&#x439; &#x43F;&#x440;&#x43E;&#x444;&#x438;&#x43B;&#x44C;</h2>
<p>Логин: leo</p>
    <p>Паспортные данные: leo</p>
<p>Зарегистрирован Thursday, 25 November 2021</p>

        </main>
    </div>

    <footer class="border-top footer text-muted">
        <div class="container">
            &copy; 2021 - CtfLand
        </div>
    </footer>
    <script src="/lib/jquery/dist/jquery.min.js"></script>
    <script src="/lib/bootstrap/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/js/site.js?v=Docv2pak8mfyRAzVoN-pxONFxWzFGkAEOqDoA3VTWDA"></script>
    <script src="https://ajax.aspnetcdn.com/ajax/jquery.validate/1.17.0/jquery.validate.min.js">
</script>
<script>(window.jQuery && window.jQuery.validator||document.write("\u003Cscript src=\u0022/lib/jquery-validation/dist/jquery.validate.min.js\u0022\u003E\u003C/script\u003E"));</script>
<script src="https://ajax.aspnetcdn.com/ajax/jquery.validation.unobtrusive/3.2.10/jquery.validate.unobtrusive.min.js">
</script>
<script>(window.jQuery && window.jQuery.validator && window.jQuery.validator.unobtrusive||document.write("\u003Cscript src=\u0022/lib/jquery-validation-unobtrusive/jquery.validate.unobtrusive.min.js\u0022\u003E\u003C/script\u003E"));</script>
</body>
</html>
"""


class PrettyClient:
    def __init__(self, client: Client):
        self._client = client

    def login(self, login, password):
        return self._client.login(login, password)

    def register_and_login(self, login, password, document):
        self._client.register(login, password, document)
        r = self._client.login(login, password)

        soup = BeautifulSoup(r.text, 'lxml')
        user_id = soup.header.select("a.nav-link")[3]['href'].split("/")[-1]
        return user_id

    def create_park(self, name, description, email, max_visitors, attraction_block, is_public):
        r = self._client.create_park(name, description, email, max_visitors, attraction_block, is_public)
        park_id = r.url.split('/')[-1]
        return park_id

    def get_my_parks(self, skip=0, take=100) -> t.List[ParkItem]:
        r = self._client.get_my_parks(skip, take)
        return self._parse_parks_list(r.text)

    def get_last_parks(self, skip=0, take=100) -> t.List[ParkItem]:
        r = self._client.get_last_parks(skip, take)
        return self._parse_parks_list(r.text)

    def add_attraction(self, park_id, name, description, cost):
        r = self._client.add_attraction(park_id, name, description, cost)
        parks = self._parse_parks_list(r.text)
        return [park for park in parks if park.id == park_id][0]

    def get_profile(self, user_id):
        r = self._client.get_profile(user_id)
        soup = BeautifulSoup(r.text, "lxml")
        ps = soup.find_all("p")
        print(ps)
        return User(
            id=user_id,
            login=ps[0].split(": ", 2)[-1],
            document=ps[1].split(": ", 2)[-1]
        )

    def _parse_parks_list(self, text):
        soup = BeautifulSoup(text, 'lxml')
        return list(map(self._parse_park_item, soup.select(".park-list-item")))

    @staticmethod
    def _parse_park_item(item) -> ParkItem:
        ps = item.find_all('p')
        is_author_exists = len(ps) > 2
        return ParkItem(
            id=item.h3.a['href'].split('/')[-1],
            name=item.h3.a.string,
            max_visitors=int(ps[-1].string.split(": ", 2)[-1]),
            attractions_count=int(ps[-2].string.split(": ", 2)[-1]),
            user_id=ps[0].a['href'].split('/')[-1] if is_author_exists else None
        )
