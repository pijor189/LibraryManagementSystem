import logging
from library.config import logger
from library.user import User
from library.interface import init_library, menu
from library.exceptions import NoBook, InvalidUser

logger.setLevel(logging.ERROR)

if __name__ == "__main__":
    lib = init_library()
    print()
    try:
        user = User(input("Welcome! What's your name?\n"))
        lib.register_user(user)
    except InvalidUser as e:
        logger.exception(e)
        exit()

    options = ["1. Show all books",
               "2. Show available books",
               "3. Find a book",
               "4. Find a user",
               "5. Borrow a book",
               "6. Extend book loan",
               "7. Return a book",
               "8. Exit"
               ]

    while True:
        try:
            print("------LIBRARY SYSTEM------")
            for option in options:
                print(option)
            number = int(input("Choose an option: "))
            if not menu(lib, user, number):
                break
        except (TypeError, NoBook, ValueError) as e:
            logger.error(e)
            continue
