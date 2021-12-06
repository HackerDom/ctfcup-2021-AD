import random
import string

ALPHA = string.ascii_lowercase + string.digits

with open('user-agents') as fin:
    USER_AGENTS = [line.strip() for line in fin]


def gen_user_agent():
    return random.choice(USER_AGENTS)


def gen_string(a=20, b=20):
    return ''.join(random.choice(ALPHA) for _ in range(random.randint(a, b)))
