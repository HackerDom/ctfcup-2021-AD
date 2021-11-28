import random
import string
import uuid

from ctfland.models import CreateParkRequest, AddAttractionRequest


def get_random_creds():
    return f"user-{uuid.uuid4()}", uuid.uuid4()


def get_random_document():
    return f"document-{uuid.uuid4()}"


def get_attraction_data() -> AddAttractionRequest:
    return AddAttractionRequest(
        name=f"attraction-{uuid.uuid4()}",
        description="Великолепное произведение исскуства!",
        cost=random.randint(450, 700),
        ticket=f"ticket-{uuid.uuid4()}"
    )


def get_random_park_data(is_public=True) -> CreateParkRequest:
    return CreateParkRequest(
        name=f"park-{uuid.uuid4()}",
        description=get_random_park_description(),
        email=get_random_email(),
        max_visitors=random.randint(50, 10_000),
        attraction_block=get_random_park_attraction_block(),
        is_public=is_public
    )


def get_random_email():
    symbols = string.digits + string.ascii_letters + "_-"
    domains = ["test.ctf", "mail.ctf", "yandex.ctf", "google.ctf"]

    return f"{random.sample(symbols, random.randint(5, 13))}@{random.choice(domains)}"


def get_random_park_attraction_block():
    known_desc = [
        "<h4>$name</h4><p>$name</p><p>А стоит то всего $cost рубликов.</p>",
    ]
    return random.choice(known_desc)


def get_random_park_description():
    known_desc = [
        "Привет, $userLogin! Вон ты какой вымахал, пора бы уже и в парк аттракционов наш сходить",
    ]
    return random.choice(known_desc)
