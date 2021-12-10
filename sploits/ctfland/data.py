import random
import string
import uuid

from models import CreateParkRequest, AddAttractionRequest, RegisterRequest


def get_random_creds():
    return f"user-{uuid.uuid4()}", str(uuid.uuid4())


def get_random_document():
    return f"document-{uuid.uuid4()}"


def get_register_request() -> RegisterRequest:
    login, password = get_random_creds()
    return RegisterRequest(
        login=login,
        password=password,
        document=get_random_document(),
    )


def get_attraction_request() -> AddAttractionRequest:
    return AddAttractionRequest(
        name=f"attraction-{uuid.uuid4()}",
        description="Великолепное произведение исскуства!",
        cost=random.randint(450, 700),
        ticket=f"ticket-{uuid.uuid4()}"
    )


def get_park_request(is_public=True) -> CreateParkRequest:
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

    a, b = get_random_string(string.ascii_letters, 2, 2)
    first_part = f"{a}{get_random_string(symbols, 5, 13)}{b}"
    return f"{first_part}@{random.choice(domains)}"


def get_random_park_attraction_block():
    known_desc = [
        "<h4>$name</h4><p>$desc</p><p>А стоит то всего $cost рубликов.</p>",
        "<p>Название: $name</p><p>Описание: $desc</p><p>Стоимость: $cost руб.</p>",
        "<h3>$name</h3><p>Пс, парень, на клоунов хочешь посмотреть? Тогда покупай билет. Для тебя персональная скидка - 50%. $cost монеток получается.</p>",
        "<p>АРАААБСКААААЯ НОООООООООЧЬ<br />\"$name\" аттракцион<br />Крутая качель, и с ней карусель</p><p>И стоит $cost рублей.</p>",
    ]
    return random.choice(known_desc)


def get_random_park_description():
    known_desc = [
        "Привет, $userLogin! Вон ты какой вымахал, пора бы уже и в парк аттракционов наш сходить",
        "Где провести детский день рождения весело и интересно, знает наш парк! Анимационные программы, тематические комнаты, буфет. Постоянные акции и скидки. Ждем тебя, $userLogin!",
        "Миссия нашего парка: создание сказочной страны, где дети и их родители получают радость семейного общения и познание мира через игру",
    ]
    return random.choice(known_desc)


def get_random_string(alphabet, min_count, max_count):
    return "".join(random.sample(alphabet, random.randint(min_count, max_count)))
