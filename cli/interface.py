import os
import data.database_state as state

from rich.console import Console
from rich.table import Table
from typing import Any
from exceptions.user_exceptions import UserInitializationError
from exceptions.book_exceptions import MissingItemError


USER_OPTIONS = [
    "1. Show all books",
    "2. Show available books",
    "3. Find a book",
    "4. Show my account",
    "5. Borrow a book",
    "6. Extend book loan",
    "7. Return a book",
    "8. Exit"
]


def clear_console() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def show_options(data: Any, clear: bool = True) -> None:
    if clear:
        clear_console()
    if not data:
        return
    for d in data:
        print(d)


def display_data(data: Any, clear: bool = True) -> None:
    if clear:
        clear_console()
    if not data:
        return

    console = Console()
    table = Table(show_lines=True)

    if isinstance(data, list):
        data = [dict(d) for d in data]

        for header in data[0].keys():
            table.add_column(header)

        for d in data:
            table.add_row(*[str(v) for v in d.values()])
    else:
        data = dict(data)

        for header in data.keys():
            table.add_column(header)

        table.add_row(*[str(v) for v in data.values()])

    console.print(table)


def run_cli() -> None:
    try:
        running = True

        while running:
            clear_console()
            show_options(
                [
                    "Welcome!",
                    "1. Log in",
                    "2. Sign in",
                    "3. Exit"
                ]
            )
            option = int(input("Choose an option: "))
            clear_console()
            if option == 1:
                user = state.user_repo.find_user_by_id(
                    input("Please provide your ID: ")
                )
                if not user:
                    print("\nNot valid ID, please try again.")
                    input("\nPress ENTER to continue...")
                else:
                    user_id = user[0]
                    running = False

            elif option == 2:
                first_name = input("Please provide your first name: ")
                last_name = input("Please provide your last name: ")
                user_id = state.user_repo.register_user(
                    " ".join([first_name.strip(), last_name.strip()])
                )
                running = False
            else:
                running = False
                state.db.close()
                exit()
    except (UserInitializationError, Exception):
        state.db.close()
        exit()

    running = True

    while running:
        clear_console()
        try:
            print("------LIBRARY SYSTEM------")
            show_options(USER_OPTIONS)
            option = int(input("Choose an option: "))
            clear_console()
            if not menu(
                user_id,
                option
            ):
                running = False
            else:
                input("\nPress ENTER to continue...")
        except (TypeError, MissingItemError, ValueError) as e:
            print(f"\033[31m{e}\033[0m")
            input("\nPress ENTER to continue...")

    state.db.close()


def menu(user_id: str, option: int) -> bool:
    if option == 1:
        display_data(state.book_repo.get_all_books())
    elif option == 2:
        display_data(state.book_repo.get_available_books())
    elif option == 3:
        find_book_options()
    elif option == 4:
        show_user_account(user_id)
    elif option == 5:
        borrow_option(user_id)
    elif option == 6:
        extend_option(user_id)
    elif option == 7:
        return_option(user_id)
    elif option == 8:
        return False
    else:
        print("Wrong option.")
    return True


def find_book_options() -> None:
    running = True

    while running:
        clear_console()
        show_options(
            [
                "1. Find a book by name",
                "2. Find a book by genre",
                "3. Find a book by author",
                "4. Find a book by id",
                "5. Back to menu"
            ]
        )
        option = int(input("Select: "))

        if not isinstance(option, int) or option not in range(1, 6):
            print("Not valid option, choose again.")
            input("\nPress ENTER to continue...")
        else:
            clear_console()
            if option == 1:
                title = input("Title of search book: ")
                display_data(state.book_repo.find_book_by_title(title))
            elif option == 2:
                genre = input("Genre of search book: ")
                display_data(state.book_repo.find_book_by_genre(genre))
            elif option == 3:
                author = input("Author of search book: ")
                display_data(state.book_repo.find_book_by_author(author))
            elif option == 4:
                uid = input("ID of search book: ")
                display_data(state.book_repo.find_book_by_id(uid))
            running = False


def find_user_option() -> None:
    running = True

    while running:
        clear_console()
        show_options(
            [
                "1. Find an user by name",
                "2. Find an user by id",
                "3. Back to menu"
            ]
        )
        option = int(input("Select: "))

        if not isinstance(option, int) or option not in range(1, 4):
            print("Not valid option, choose again.")
            input("\nPress ENTER to continue...")
        else:
            clear_console()
            if option == 1:
                name = input("Name of search user: ")
                display_data(state.user_repo.find_user_by_name(name))
            elif option == 2:
                uid = input("ID of search book: ")
                display_data(state.user_repo.find_user_by_id(uid))
            running = False


def show_user_account(user_id: str) -> None:
    user = state.user_repo.find_user_by_id(user_id)
    books = state.user_repo.get_all_books_from_user(user_id)
    ebooks = state.user_repo.get_all_ebooks_from_user(user_id)
    books.extend(ebooks)

    print(f"User: {user["id"]} - {user["name"]}")
    display_data(books, False)


def get_days() -> int:
    attempts = 1

    while attempts < 4:
        days = int(
            input(
                "How many days would you like to borrow this book for? "
                "(Maximum: 30 days): "
            )
        )
        if days <= 0 or days > 30:
            print("You have provided invalid count of days.")
            attempts += 1
        else:
            return days
    else:
        print("Too many failed attempts. Lockout duration: 1 day.")
        return 1


def borrow_option(user_id: str) -> None:
    name = input("Name a book what you want to borrow: ")
    data = state.book_repo.find_book_by_title(name)

    if not data:
        print(f"Book {name} does not exist")
        return
    elif len(data) > 1:
        choice = input(
            "Do you want book(1) or ebook(2)?\nChoose one option "
            "or click ENTER: "
        ).strip()
        option = int(choice) if choice.isdigit() else 0

        if option in range(1, 3):
            book = data[option - 1]
        elif option == 0:
            return
        else:
            print("Not valid option.")
            return
    else:
        book = data[0]

    days = 30

    if book["type"] == 'book':
        days = get_days()

    state.borrow_repo.borrow_book(user_id, book["id"], days)


def extend_option(user_id: str) -> None:
    books = state.user_repo.get_all_books_from_user(user_id)

    if books:
        display_data(books)

        book_id = input("\nProvide book ID you want to extend "
                        "or click ENTER: ").strip()

        if book_id == "":
            return

        book = state.book_repo.find_book_by_id(book_id)

        if book:
            state.borrow_repo.extend_loan(book_id, user_id, get_days())
        else:
            print(f"Book {book_id} does not exist.")
    else:
        print("You dont have any books that you can extend.")


def return_option(user_id: str) -> None:
    books = state.user_repo.get_all_books_from_user(user_id)

    if books:
        display_data(books)

        book_id = input("\nProvide book ID you want to return "
                        "or click ENTER: ").strip()

        if book_id == "":
            return

        book = state.book_repo.find_book_by_id(book_id)

        if book:
            state.borrow_repo.return_book(user_id, book_id)
        else:
            print(f"Book {book_id} does not exist.")
    else:
        print("You dont have any books that you can return")
