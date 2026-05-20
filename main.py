from library.user import User
from interface import init_library, menu, clear_console
from library.exceptions import NoBook, InvalidUser
import logging
from fastapi import FastAPI
from api.books import router as books_router
from api.users import router as users_router

# logging.disable(logging.CRITICAL)

app = FastAPI()

app.include_router(books_router)
app.include_router(users_router)

if __name__ == "__main__":

    """lib = init_library()
    print()
    try:
        user = User(input("Welcome! What's your name?\n"))
        lib.register_user(user)
    except InvalidUser as e:
        print(e)
        exit()

    options = [
        "1. Show all books",
        "2. Show available books",
        "3. Find a book",
        "4. Find a user",
        "5. Borrow a book",
        "6. Extend book loan",
        "7. Return a book",
        "8. Exit",
    ]
    running = True

    while running:
        clear_console()

        try:
            print("------LIBRARY SYSTEM------")
            for option in options:
                print(option)
            number = int(input("Choose an option: "))
            if not menu(lib, user, number):
                running = False
            else:
                input("\nPress ENTER to continue...")
        except (TypeError, NoBook, ValueError) as e:
            print(f"\033[31m{e}\033[0m")
            input("\nPress ENTER to continue...")"""
