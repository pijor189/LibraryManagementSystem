import os
import data.state as state

from library.book import EBook
from library.library import Library
from library.user import User
from library.loan import Loan
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


def show(data: Any, clear: bool=True) -> None:
    if clear:
        clear_console()
    if not data:
        return
    for d in data:
        print(d)


def run_cli() -> None:
    try:
        running = True

        while running:
            clear_console()
            show(
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
                user = state.lib.find_user_by_id(
                    input("Please provide your ID: ")
                )
                if not user:
                    print("\nNot valid ID, please try again")
                    input("\nPress ENTER to continue...")
                else:
                    running = False

            elif option == 2:
                first_name = input("Please provide your first name: ")
                last_name = input("Please provide your last name: ")
                state.user_repository.register_user(
                    " ".join([first_name, last_name])
                )
                user = list(state.lib.users_list.values())[-1]
                running = False
            else:
                running = False
                state.db.close()
                exit()
    except UserInitializationError:
        state.db.close()
        exit()

    running = True

    while running:
        clear_console()
        try:
            print("------LIBRARY SYSTEM------")
            show(USER_OPTIONS)
            number = int(input("Choose an option: "))
            clear_console()
            if not menu(
                state.lib,
                user,
                number
            ):
                running = False
            else:
                input("\nPress ENTER to continue...")
        except (TypeError, MissingItemError, ValueError) as e:
            print(f"\033[31m{e}\033[0m")
            input("\nPress ENTER to continue...")

    state.db.close()


def menu(lib: Library, user: User, option: int) -> bool:
    if option == 1:
        show(lib.get_all_books())
    elif option == 2:
        show(lib.get_available_books())
    elif option == 3:
        find_book_options(lib)
    elif option == 4:
        show_user_account(lib, user)
    elif option == 5:
        borrow_option(lib, user)
    elif option == 6:
        extend_option(lib, user)
    elif option == 7:
        return_option(lib, user)
    elif option == 8:
        return False
    else:
        print("Wrong option")
    return True


def find_book_options(lib: Library) -> None:
    running = True

    while running:
        clear_console()
        show(
            [
                "1. Find book by a name",
                "2. Find book by a genre",
                "3. Find book by an author",
                "4. Back to menu",
            ]
        )
        number = int(input("Select: "))

        if not isinstance(number, int) or number not in range(1, 5):
            print("Not valid number, choose again")
            input("\nPress ENTER to continue...")
        else:
            clear_console()
            if number == 1:
                name = input("Name of search book: ")
                show(lib.find_book_by_title(name))
            elif number == 2:
                genre = input("Genre of search book: ")
                show(lib.find_books_by_genre(genre))
            elif number == 3:
                author = input("Author of search book: ")
                show(lib.find_books_by_author(author))
            running = False


def find_user_option(lib: Library) -> None:
    user_name = input("Name a user what you want to find: ")
    result = lib.find_user_by_name(user_name)
    print(result if result else f"Provide user {user_name} does not exist")


def show_user_account(lib: Library, user: User) -> None:
    books = [
        lib.find_book_by_id(book)
        for book in user.borrowed_physical_books.values()
    ]
    ebooks = [
        lib.find_book_by_id(ebook)
        for ebook in user.borrowed_ebooks.values()
    ]
    print(f"User\n\n{user.id} - {user.name}\n\nBorrowed books:\n")
    show(books, False)
    show(ebooks, False)


def get_days() -> int:
    while True:
        days = int(
            input(
                "How many days would you like to borrow this book for? "
                "(Maximum: 30 days): "
            )
        )
        if days <= 0 or days > 30:
            print("You have provided invalid count of days")
        else:
            return days


def borrow_option(lib: Library, user: User) -> None:
    book_name = input("Name a book what you want to borrow: ")
    book = lib.find_book_by_title(book_name)
    book = lib.choose_book(book)
    days = Loan.MAX_DAYS

    if not isinstance(book, EBook):
        if book.is_book_available():
            days = get_days()
        else:
            print(f"Book '{book.title}' is not available")
    state.borrowing_repository.borrow_book(user, book, days)


def extend_option(lib: Library, user: User) -> None:
    if user.borrowed_physical_books:
        print("Books you borrowed:")
        for index, book_id in enumerate(user.borrowed_physical_books.values(), start=1):
            book = lib.find_book_by_id(book_id)
            print(f"{index}. {book.id} - {book.title}")

        book_id = input("Provide book ID you want to extend: ")
        book = lib.find_book_by_id(book_id)

        for loan in lib.loans.values():
            if user.id == loan.user_id and book.id == loan.book_id:
                state.borrowing_repository.extend_loan(loan, get_days())
    else:
        print("You dont have any books that you can extend")


def return_option(lib: Library, user: User) -> None:
    if user.borrowed_physical_books:
        print("Books you borrowed:\n")

        for index, book_id in enumerate(user.borrowed_physical_books.values(), start=1):
            book = lib.find_book_by_id(book_id)
            print(f"{index}. {book.id} - {book.title}")

        book_id = input("Provide book ID what you want to return: ")
        book = lib.find_book_by_id(book_id)
        state.borrowing_repository.return_book(user, book)
    else:
        print("You dont have any books that you can return")
