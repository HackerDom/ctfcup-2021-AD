import random
import string
import json

from gornilo import Checker, CheckRequest, GetRequest, PutRequest, Verdict
from connector import Connector

checker = Checker()

def get_random_card():
    return "".join(random.choices(string.digits, k=16))

def get_random_str():
    return "".join(random.choices(string.digits + string.ascii_letters, k=random.randint(1,11)))


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    connect = Connector(request.hostname)
    action = "transfer"
    sender = get_random_card()
    reciever = get_random_card()
    value = random.randint(100, 100000)
    comment = get_random_str()
    try:
        res = connect.send_message(f"{action} {sender} {reciever} {value} {comment}")
        if not res:
            return Verdict.DOWN("connection error")
        action = "checkid"
        try:
            res = res.split(b"\n")
            id = res[0].decode("utf-8")
            encoded = res[1]
        except Exception:
            return Verdict.MUMBLE("incorrect answer")
        res = connect.send_message(f"{action} {id}")
        if not res:
            return Verdict.DOWN("connection error")
        try:
            res = res.decode("utf-8")
            res = json.loads(res)
        except Exception:
            return Verdict.MUMBLE("incorrect answer")
        if res.get("comment") != comment:
            return Verdict.MUMBLE("incorrect answer")
        res = connect.send_message("show 0 10")
        if not res:
            return Verdict.DOWN("connection error")
        try:
            res = res.split(b"\n")
        except Exception:
            return Verdict.MUMBLE("incorrect answer")
        if encoded not in res:
            return Verdict.MUMBLE("incorrect answer")
        res = connect.send_message(f"show {random.randint(0, 10)} 20")
        if not res:
            return Verdict.DOWN("connection error")
        return Verdict.OK()
    finally:
        connect.close_connection()


@checker.define_put(vuln_rate=1, vuln_num=1)
async def put(request: PutRequest) -> Verdict:
    connect = Connector(request.hostname)
    action = "transfer"
    sender = get_random_card()
    reciever = get_random_card()
    value = random.randint(1, 1000000)
    comment = request.flag
    try:
        res = connect.send_message(f"{action} {sender} {reciever} {value} {comment}")
        if not res:
            return Verdict.DOWN("connection error")
        try:
            res = res.split(b"\n")
            id = res[0].decode("utf-8")
        except Exception:
            Verdict.MUMBLE("incorrect answer")
        return Verdict.OK(id)
    finally:
        connect.close_connection()

@checker.define_get(vuln_num=1)
async def get(request: GetRequest) -> Verdict:
    connect = Connector(request.hostname)
    action = "checkid"
    id = request.flag_id.strip()
    try:
        res = connect.send_message(f"{action} {id}")
        if not res:
            return Verdict.DOWN("connection error")
        try:
            res = res.decode("utf-8")
            res = json.loads(res)
        except Exception:
            return Verdict.MUMBLE("incorrect answer")
        if res.get("comment") != request.flag:
            return Verdict.CORRUPT("invald flag")
        return Verdict.OK()
    finally:
        connect.close_connection()
    

if __name__ == "__main__":
    checker.run()
