from library.user import User
from interface import init_library, menu, clear_console, OPTIONS
from exceptions.user_exceptions import InvalidUser
from exceptions.book_exceptions import NoBook
import logging


logging.disable(logging.CRITICAL)


if __name__ == "__main__":
    lib = init_library()
    try:
        clear_console()
        user = User(input("Welcome! What's your name?\n"))
        lib.register_user(user)
    except InvalidUser as e:
        print(e)
        exit()

    running = True

    while running:
        clear_console()
        try:
            print("------LIBRARY SYSTEM------")
            print(OPTIONS)
            number = int(input("Choose an option: "))
            clear_console()
            if not menu(lib, user, number):
                running = False
            else:
                input("\nPress ENTER to continue...")
        except (TypeError, NoBook, ValueError) as e:
            print(f"\033[31m{e}\033[0m")
            input("\nPress ENTER to continue...")
