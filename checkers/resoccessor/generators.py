import random
import string

ALPHA = string.ascii_lowercase + string.digits

with open('checkers/resoccessor/user-agents') as fin:
    USER_AGENTS = [line.strip() for line in fin]


def gen_user_agent():
    return random.choice(USER_AGENTS)


def gen_string(a=20, b=20):
    return ''.join(random.choice(ALPHA) for _ in range(random.randint(a, b)))


def _check_trigger(rule, user_groups):
    return rule[1] == (rule[0] in user_groups)


def check(groups, rules, user_id):
    user_groups = set(groups[user_id])
    for rule in rules:
        if _check_trigger(rule, user_groups):
            return rule[2]

    return 0


def gen_schema():
    group_count = random.randint(1, 10)
    user_count = random.randint(3, 20)
    user_with_access = random.randint(1, user_count - 1)
    groups = [[]] + [[group_id for group_id in range(group_count) if random.random() < 0.5] for _ in range(user_count)]
    group_ids = list(range(group_count))
    random.shuffle(group_ids)
    group_ids_iter = iter(group_ids)
    rules = []

    for _ in range(min(random.randint(1, 10), group_count)):
        group_id = next(group_ids_iter)
        rules.append([group_id, random.randint(0, 1), int(random.random() > 0.2)])

    if not check(groups, rules, user_with_access):
        access_rule_index = 0

        for rule_index in range(len(rules)):
            rule = rules[rule_index]
            if _check_trigger(rule, groups[user_with_access]) and not rule[2]:
                access_rule_index = rule_index
                break

        groups[user_with_access].append(group_count)
        rules.insert(access_rule_index, [group_count, 1, 1])

    return {
        "groups": groups,
        "rules": rules,
    }, user_with_access
