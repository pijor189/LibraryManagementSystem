from library.library import Library
from library.book import Book, EBook
from library.user import User
from utils.data_loader import DataLoader
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]


def create_books() -> tuple[list[Book], list[EBook]]:
    book1 = Book(
        "1984",
        "George Orwell",
        ["dystopian fiction", "political fiction", "science fiction"],
        1949,
    )
    book2 = Book(
        "Dune",
        "Frank Herbert",
        ["science fiction", "space opera", "political fiction"],
        1965,
    )
    book3 = Book(
        "Clean Code",
        "Robert C. Martin",
        ["technical literature", "software engineering", "non-fiction"],
        2008,
    )
    book4 = Book(
        "The Hobbit",
        "J.R.R. Tolkien",
        ["fantasy", "adventure fiction"],
        1937,
    )
    book5 = Book(
        "Krzyżacy",
        "Henryk Sienkiewicz",
        ["historical fiction"],
        1900,
    )
    book6 = Book(
        "Ogniem i mieczem",
        "Henryk Sienkiewicz",
        ["historical fiction"],
        1884,
    )
    book7 = Book(
        "Potop",
        "Henryk Sienkiewicz",
        ["historical fiction"],
        1886,
    )
    book8 = Book(
        "Faraon",
        "Bolesław Prus",
        ["historical fiction", "political fiction", "psychological novel"],
        1897,
    )
    book9 = Book(
        "Trylogia",
        "Henryk Sienkiewicz",
        ["historical fiction"],
        1888,
    )
    book10 = Book(
        "Chłopi",
        "Władysław Reymont",
        ["realistic fiction", "social novel", "epic literature"],
        1904,
    )

    ebook1 = EBook(
        "Mistrz i Małgorzata",
        "Michaił Bułhakow",
        ["magical realism", "philosophical fiction", "satire"],
        1967,
        5,
    )
    ebook2 = EBook(
        "1984",
        "George Orwell",
        ["dystopian fiction", "political fiction", "science fiction"],
        1949,
        2,
    )
    ebook3 = EBook(
        "Brave New World",
        "Aldous Huxley",
        ["dystopian fiction", "science fiction"],
        1932,
        3,
    )
    ebook4 = EBook(
        "Python 101",
        "John Doe",
        ["technical literature", "educational programming"],
        2020,
        5,
    )

    all_books = [
        book1, book2, book3, book4, book5,
        book6, book7, book8, book9, book10
    ]
    all_ebooks = [ebook1, ebook2, ebook3, ebook4]
    return all_books, all_ebooks


def create_users() -> list[User]:
    user1 = User("Jan Kowalski")
    user2 = User("Anna Nowak")
    user3 = User("Piotr Wiśniewski")
    all_users = [user1, user2, user3]
    return all_users


def pytest_addoption(parser):
    parser.addoption("--smoke", action="store_true")
    parser.addoption("--regression", action="store_true")
    parser.addoption("--nightly", action="store_true")
    parser.addoption("--stress", action="store_true")


def pytest_collection_modifyitems(config, items):
    markers = {
        "--smoke": {"smoke"},
        "--regression": {"smoke", "regression"},
        "--nightly": {"smoke", "regression", "nightly"},
        "--stress": {"stress"},
    }
    selected_markers = set()

    for option, markers in markers.items():
        if config.getoption(option):
            selected_markers.update(markers)

    if not selected_markers:
        return

    selected = []
    deselected = []

    for item in items:
        if selected_markers.intersection(item.keywords):
            selected.append(item)
        else:
            deselected.append(item)

    items[:] = selected
    config.hook.pytest_deselected(items=deselected)


@pytest.fixture(scope="function")
def create_lib():
    lib = Library()
    """users = create_users()
    books, ebooks = create_books()"""
    users = DataLoader.load_users(f"{BASE_DIR}/data/users.json")
    books, ebooks = DataLoader.load_books(f"{BASE_DIR}/data/books.json")
    for book in books:
        lib.add_book(book)
    for ebook in ebooks:
        lib.add_book(ebook)
    for user in users:
        lib.register_user(user)
    yield lib
    del lib
