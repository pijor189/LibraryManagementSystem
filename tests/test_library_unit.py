from library.user import User
from library.book import Book, EBook
from library.exceptions import (
    InvalidUser,
    InvalidBook,
    NoBook,
    NoUser,
    InvalidNumberOfBooks,
)
from unittest.mock import patch
import logging
import pytest


"""
    Create a library
"""


@pytest.mark.smoke
def test_create_lib(create_lib):
    lib = create_lib
    assert len(lib.get_all_books()) == 10 + 4
    assert len(lib.get_all_users()) == 3


"""
    Create a invalid user
"""


@pytest.mark.regression
def test_invalid_user():
    with pytest.raises(InvalidUser):
        User("")


"""
    Create a invalid book (invalid title)
"""


@pytest.mark.regression
def test_invalid_book_invalid_title():
    with pytest.raises(InvalidBook):
        Book(1, "Henryk Sienkiewicz", "historical fiction", 1900)


"""
    Create a invalid book (empty title)
"""


@pytest.mark.regression
def test_invalid_book_empty_title():
    with pytest.raises(InvalidBook):
        Book("", "Henryk Sienkiewicz", "historical fiction", 1900)


"""
    Create a invalid book (empty author)
"""


@pytest.mark.regression
def test_invalid_book_empty_author():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", "", "historical fiction", 1900)


"""
    Create a invalid book (invalid author)
"""


@pytest.mark.regression
def test_invalid_book_invalid_author():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", 1, "historical fiction", 1900, 1)


"""
    Create a invalid book (empty genre - string)
"""


@pytest.mark.regression
def test_invalid_book_empty_genre_str():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", "Henryk Sienkiewicz", "", 1900)


"""
    Create a invalid book (empty genre - list)
"""


@pytest.mark.regression
def test_invalid_book_empty_genre_list():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", "Henryk Sienkiewicz", [], 1900)


"""
    Create a invalid book (invalid genre)
"""


@pytest.mark.regression
def test_invalid_book_invalid_genre():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", "Henryk Sienkiewicz", 1, 1900)


"""
    Create a invalid book (invalid amount)
"""


@pytest.mark.regression
def test_invalid_book_invalid_amout():
    with pytest.raises(InvalidBook):
        Book("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "1")


"""
    Create a invalid ebook (file size not int)
"""


@pytest.mark.regression
def test_invalid_ebook_invalid_file_size():
    with pytest.raises(InvalidBook):
        EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "")


"""
    Create a invalid ebook (invalid file size)
"""


@pytest.mark.regression
def test_invalid_ebook_too_small_file_size():
    with pytest.raises(InvalidBook):
        EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, -1)


"""
    Book not provided to add_book function
"""


@pytest.mark.regression
def test_book_not_provided_to_add(create_lib, caplog):
    lib = create_lib
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.add_book("Potop")
    assert caplog.records[0].levelname == "ERROR"


"""
    User not provided to register_user function
"""


@pytest.mark.regression
def test_user_not_provided_to_register(create_lib, caplog):
    lib = create_lib
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoUser):
            lib.register_user("Krzysztof")
    assert caplog.records[0].levelname == "ERROR"


"""
    Not register user provided to borrow function
"""


@pytest.mark.regression
def test_not_register_user_provided_to_borrow(create_lib, caplog):
    lib = create_lib
    user = User("Adam Nowak")
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoUser):
            lib.borrow(user, book)
    assert caplog.records[0].levelname == "ERROR"


"""
    Not added book provided to borrow function
"""


@pytest.mark.regression
def test_not_added_book_provided_to_borrow(create_lib, caplog):
    lib = create_lib
    user = lib.users_list[0]
    book = Book(
        "Nexus",
        "Yuval Noah Harari",
        ["non-fiction", "history", "technology", "society", "artificial intelligence"],
        2024,
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.borrow(user, book)
    assert caplog.records[0].levelname == "ERROR"


"""
    Not register user provided to borrow function
"""


@pytest.mark.regression
def test_not_valid_data_provided_to_borrow(create_lib, caplog):
    lib = create_lib
    user = "Adam Nowak"
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception):
            lib.borrow(user, book)
    assert caplog.records[0].levelname == "ERROR"


"""
    Not register user provided to return_book function
"""


@pytest.mark.regression
def test_not_register_user_provided_to_return_book(create_lib, caplog):
    lib = create_lib
    user = User("Adam Nowak")
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoUser):
            lib.return_book(user, book)
    assert caplog.records[0].levelname == "ERROR"


"""
    Not borrowed book provided to return_book function
"""


@pytest.mark.regression
def test_not_borrowed_book_provided_to_return_book(create_lib, caplog):
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.return_book(user, book)
    assert caplog.records[0].levelname == "ERROR"


"""
    Invalid book to add more copies
"""


@pytest.mark.regression
def test_invalid_book_to_add_more_copies(create_lib, caplog):
    lib = create_lib
    book = Book(
        "Nexus",
        "Yuval Noah Harari",
        ["non-fiction", "history", "technology", "society", "artificial intelligence"],
        2024,
    )
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.add_existing_book(book, 1)
    assert caplog.records[0].levelname == "ERROR"


"""
    Invalid number of books to add
"""


@pytest.mark.regression
def test_invalid_number_books_add(create_lib, caplog):
    lib = create_lib
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(InvalidNumberOfBooks):
            lib.add_existing_book(book, 0)
    assert caplog.records[0].levelname == "ERROR"


"""
    Invalid number of days to extend a loan
"""


@pytest.mark.regression
def test_invalid_extend_loan(create_lib):
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    lib.borrow(user, book)
    loan = lib.loans[0]
    with pytest.raises(ValueError):
        loan.extend(-1)


"""
    No book available in the list
"""


@pytest.mark.regression
def test_no_book_to_choose(create_lib):
    lib = create_lib
    books = lib.find_book_by_name("123")
    with pytest.raises(NoBook):
        lib.choose_book(books)


"""
    Only one book is returned from choose_book
"""


@pytest.mark.regression
def test_choose_with_one_option(create_lib):
    lib = create_lib
    books = lib.find_book_by_name("Dune")
    books = lib.choose_book(books)
    assert isinstance(books, Book)


"""
    Choose a book from a list of two books (Book and EBook)
"""


@pytest.mark.regression
def test_choose_with_more_option(create_lib):
    lib = create_lib
    books = lib.find_book_by_name("1984")
    with patch("builtins.input", return_value=2):
        books = lib.choose_book(books)
    assert isinstance(books, EBook)


"""
    Find a book by a name (exist)
"""


@pytest.mark.regression
def test_matching_book_by_name(create_lib):
    lib = create_lib
    result = lib.find_book_by_name(" Potop ")
    assert result is not None


"""
    Find a book by a name (not exist)
"""


@pytest.mark.regression
def test_no_matching_book_by_name(create_lib):
    lib = create_lib
    result = lib.find_book_by_name("Potopy")
    assert result is None


"""
    Find a book by a genre (exist)
"""


@pytest.mark.regression
def test_matching_book_by_genre(create_lib):
    lib = create_lib
    result = lib.find_books_by_genre("  historical fiction ")
    assert len(result) > 0


"""
    Find a book by a genre (not exist)
"""


@pytest.mark.regression
def test_no_matching_book_by_genre(create_lib):
    lib = create_lib
    result = lib.find_books_by_genre("poetry")
    assert result == []


"""
    Find a book by an author (exist)
"""


@pytest.mark.regression
def test_matching_book_by_author(create_lib):
    lib = create_lib
    result = lib.find_books_by_author(" Henryk Sienkiewicz  ")
    assert len(result) > 0


"""
    Find a book by an author (not exist)
"""


@pytest.mark.regression
def test_no_matching_book_by_author(create_lib):
    lib = create_lib
    result = lib.find_books_by_author("Krzysztof Pijor")
    assert result == []


"""
    Find existing user
"""


@pytest.mark.regression
def test_find_existing_user(create_lib):
    lib = create_lib
    user = lib.find_user("Anna Nowak")
    assert isinstance(user, User)


"""
    Attempt to find nonexistent user
"""


@pytest.mark.regression
def test_find_nonexistent_user(create_lib):
    lib = create_lib
    user = lib.find_user("Tomasz Nowak")
    assert not isinstance(user, User)


"""
    Attempt to borrow the unavailable book twice
"""


@pytest.mark.regression
def test_borrow_unavailable_book_twice(create_lib):
    lib = create_lib
    book = lib.catalog[0]
    user1 = lib.users_list[0]
    user2 = lib.users_list[1]
    lib.borrow(user1, book)
    lib.borrow(user2, book)
    assert any(b in user1.borrowed_physical_books for b in book.copies)
    assert user2 in book.waitlist

    lib.borrow(user2, book)
    assert user2 in book.waitlist


"""
    Attempt to unregister nonexistent user
"""


@pytest.mark.regression
def test_unregister_nonexistent_user(create_lib):
    lib = create_lib
    user = User("Krzysztof Pijor")
    with pytest.raises(NoUser):
        lib.unregister_user(user)


"""
    Attempt to borrow four books when the maximum allowed is three
"""


@pytest.mark.regression
def test_attempt_to_borrow_four_books(create_lib):
    lib = create_lib
    user = lib.users_list[0]
    for i, book in enumerate(lib.catalog, start=1):
        lib.borrow(user, book)
        if i == 4:
            break
    assert len(user.borrowed_physical_books) == 3
    assert user.waitlist is not None
