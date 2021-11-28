from pydantic import BaseModel
import typing as t

from ctfland.client import Client
from bs4 import BeautifulSoup

from ctfland.models import *


class Purchase(BaseModel):
    name: str
    ticket: str


class ParkItem(BaseModel):
    id: str
    name: str
    max_visitors: int
    attractions_count: int
    user_id: t.Optional[str]
    attractions: t.Optional[t.List[Purchase]]


class UserPurchasesInfo(BaseModel):
    balance: int
    purchases: t.List[Purchase]


class User(BaseModel):
    id: str
    login: str
    document: str
    role: UserRole
    purchasesInfo: t.Optional[UserPurchasesInfo]


class ParksList(BaseModel):
    total_count: int
    parks: t.List[ParkItem]


class PrettyClient:
    def __init__(self, client: Client):
        self._client = client

    def login(self, login, password):
        r = self._client.login(login, password)

        soup = BeautifulSoup(r.text, 'lxml')
        user_id = soup.header.find(id="auth-username")['href'].split("/")[-1]
        return user_id

    def register_and_login(self, request: RegisterRequest):
        self._client.register(request)
        return self.login(request.login, request.password)

    def create_park(self, request: CreateParkRequest):
        r = self._client.create_park(request)
        park_id = r.url.split('/')[-1]
        return park_id

    def get_my_parks(self, skip=0, take=100) -> ParksList:
        r = self._client.get_my_parks(skip, take)
        return self._parse_parks_list(r.text)

    def get_last_parks(self, skip=0, take=100) -> ParksList:
        r = self._client.get_last_parks(skip, take)
        return self._parse_parks_list(r.text)

    def add_attraction(self, park_id, request: AddAttractionRequest):
        r = self._client.add_attraction(park_id, request)
        parks = self._parse_parks_list(r.text)
        return [park for park in parks.parks if park.id == park_id][0]

    def get_profile(self, user_id):
        r = self._client.get_profile(user_id)
        soup = BeautifulSoup(r.text, "lxml")
        role = UserRole.Visitor if self._get_value(soup.find(id="profile-role")) == "Покупатель" else UserRole.Moderator
        return User(
            id=user_id,
            login=self._get_value(soup.find(id="profile-login")),
            role=role,
            document=self._get_value(soup.find(id="profile-document")),
            purchasesInfo=None if role == UserRole.Moderator else self._parse_purchases_info(soup)
        )

    def _parse_parks_list(self, text) -> ParksList:
        soup = BeautifulSoup(text, 'lxml')
        return ParksList(
            total_count=int(self._get_value(soup.find(id="parks-counter"))),
            parks=list(map(self._parse_park_item, soup.select(".park-list-item"))),
        )

    def _parse_park_item(self, item) -> ParkItem:
        owner = item.find(class_="park-owner")
        max_visitors = item.find(class_="park-max-visitors")
        attractions_count = item.find(class_="attractions-counter")
        attractions = [Purchase(name=x.i.string, ticket=x.b.string) for x in item.select(".attractions li")]
        return ParkItem(
            id=item.h3.a['href'].split('/')[-1],
            name=item.h3.a.string,
            max_visitors=int(self._get_value(max_visitors)),
            attractions_count=int(self._get_value(attractions_count)),
            user_id=owner.a['href'].split("/")[-1] if owner else None,
            attractions=attractions,
        )

    def _parse_purchases_info(self, soup) -> UserPurchasesInfo:
        purchases = [Purchase(name=x.i.string, ticket=x.b.string) for x in soup.select(".profile-purchase")]
        return UserPurchasesInfo(
            balance=int(self._get_value(soup.find(id="profile-balance"))),
            purchases=purchases,
        )

    @staticmethod
    def _get_value(p):
        return p.string.split(": ", 2)[-1] if p else None
