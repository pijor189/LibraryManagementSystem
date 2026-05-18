import random


def generate_uid(uid_list: set) -> str:
    while True:
        uid = "".join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
        if uid not in uid_list:
            uid_list.add(uid)
            break
    return uid
