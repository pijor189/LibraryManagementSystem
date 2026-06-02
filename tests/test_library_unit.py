import pytest
from library.user import User
from library.book import Book, EBook, BookCopy
from library.loan import Loan
from exceptions.book_exceptions import (
    BookInitializationError, MissingBookError
)
from exceptions.user_exceptions import (
    UserInitializationError, MissingUserError
)
from exceptions.library_exceptions import InvalidNumberOfBooksError
from exceptions.loan_exceptions import (
    InvalidExtendDaysError, LoanInitializationError
)
from unittest.mock import patch


@pytest.mark.smoke
def test_create_lib(create_lib):
    """
        Create a library
    """
    lib = create_lib
    print(lib)
    assert len(lib.get_all_books()) == 10 + 4
    assert len(lib.get_all_users()) == 3


@pytest.mark.regression
def test_invalid_user():
    """
        Create a invalid user
    """
    with pytest.raises(UserInitializationError):
        User("")


@pytest.mark.regression
def test_invalid_book_invalid_title():
    """
        Create a invalid book (invalid title)
    """
    with pytest.raises(BookInitializationError):
        Book(1, "Henryk Sienkiewicz", "historical fiction", 1900)


@pytest.mark.regression
def test_invalid_book_empty_title():
    """
        Create a invalid book (empty title)
    """
    with pytest.raises(BookInitializationError):
        Book("", "Henryk Sienkiewicz", "historical fiction", 1900)


@pytest.mark.regression
def test_invalid_book_empty_author():
    """
        Create a invalid book (empty author)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", "", "historical fiction", 1900)


@pytest.mark.regression
def test_invalid_book_invalid_author():
    """
        Create a invalid book (invalid author)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", 1, "historical fiction", 1900, 1)


@pytest.mark.regression
def test_invalid_book_empty_genre_str():
    """
        Create a invalid book (empty genre - string)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", "Henryk Sienkiewicz", "", 1900)


@pytest.mark.regression
def test_invalid_book_empty_genre_list():
    """
        Create a invalid book (empty genre - list)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", "Henryk Sienkiewicz", [], 1900)


@pytest.mark.regression
def test_invalid_book_invalid_genre():
    """
        Create a invalid book (invalid genre)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", "Henryk Sienkiewicz", 1, 1900)


@pytest.mark.regression
def test_invalid_book_invalid_amout():
    """
        Create a invalid book (invalid amount)
    """
    with pytest.raises(BookInitializationError):
        Book("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "1")


@pytest.mark.regression
def test_create_book_invalid_year():
    """
        Attempt to create a book with a year that is too high
    """
    with pytest.raises(BookInitializationError):
        Book(
            "Nexus",
            "Yuval Noah Harari",
            [
                "non-fiction",
                "history",
                "technology",
                "society",
                "artificial intelligence"
            ],
            3026,
        )


@pytest.mark.regression
def test_create_book_nonexistent_year():
    """
        Attempt to create a book with a year equal to 0
    """
    with pytest.raises(BookInitializationError):
        Book(
            "Nexus",
            "Yuval Noah Harari",
            [
                "non-fiction",
                "history",
                "technology",
                "society",
                "artificial intelligence"
            ],
            0,
        )


@pytest.mark.regression
def test_invalid_ebook_invalid_file_size():
    """
        Create a invalid ebook (file size not int)
    """
    with pytest.raises(BookInitializationError):
        EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "")


@pytest.mark.regression
def test_invalid_ebook_too_small_file_size():
    """
        Create a invalid ebook (invalid file size)
    """
    with pytest.raises(BookInitializationError):
        EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, -1)


@pytest.mark.regression
def test_return_books_with_empty_list(create_lib):
    """
        Return book with empty borrowed books list
    """
    lib = create_lib
    user = lib.users_list[0]
    with pytest.raises(MissingBookError):
        lib.return_all_items(user)


@pytest.mark.regression
def test_book_not_provided_to_add(create_lib):
    """
        Book not provided to add_book function
    """
    lib = create_lib
    with pytest.raises(MissingBookError):
        lib.add_book("Potop")


@pytest.mark.regression
def test_user_not_provided_to_register(create_lib):
    """
        User not provided to register_user function
    """
    lib = create_lib
    with pytest.raises(MissingUserError):
        lib.register_user("Krzysztof")


@pytest.mark.regression
def test_not_register_user_provided_to_borrow(create_lib, caplog):
    """
        Not register user provided to borrow function
    """
    lib = create_lib
    user = User("Adam Nowak")
    book = lib.catalog[0]
    with pytest.raises(MissingUserError):
        lib.borrow(user, book)


@pytest.mark.regression
def test_not_added_book_provided_to_borrow(create_lib):
    """
        Not added book provided to borrow function
    """
    lib = create_lib
    user = lib.users_list[0]
    book = Book(
        "Nexus",
        "Yuval Noah Harari",
        ["non-fiction", "history", "technology",
         "society", "artificial intelligence"
         ],
        2024,
    )
    with pytest.raises(MissingBookError):
        lib.borrow(user, book)


@pytest.mark.regression
def test_not_valid_data_provided_to_borrow(create_lib):
    """
        Not register user provided to borrow function
    """
    lib = create_lib
    user = "Adam Nowak"
    book = lib.catalog[0]
    with pytest.raises(Exception):
        lib.borrow(user, book)


@pytest.mark.regression
def test_not_register_user_provided_to_return_book(create_lib):
    """
        Not register user provided to return_book function
    """
    lib = create_lib
    user = User("Adam Nowak")
    book = lib.catalog[0]
    with pytest.raises(MissingUserError):
        lib.return_book(user, book)


@pytest.mark.regression
def test_not_borrowed_book_provided_to_return_book(create_lib):
    """
        Not borrowed book provided to return_book function
    """
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    with pytest.raises(MissingBookError):
        lib.return_book(user, book)


@pytest.mark.regression
def test_invalid_book_to_add_more_copies(create_lib):
    """
        Invalid book to add more copies
    """
    lib = create_lib
    book = Book(
        "Nexus",
        "Yuval Noah Harari",
        [
            "non-fiction", "history", "technology",
            "society", "artificial intelligence"
        ],
        2024,
    )
    with pytest.raises(MissingBookError):
        lib.add_existing_book(book, 1)


@pytest.mark.regression
def test_invalid_number_books_add(create_lib):
    """
        Invalid number of books to add
    """
    lib = create_lib
    book = lib.catalog[0]
    with pytest.raises(InvalidNumberOfBooksError):
        lib.add_existing_book(book, 0)


@pytest.mark.regression
def test_borrow_book_invalid_days(create_lib):
    """
        Invalid number of days to borrow a book
    """
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    with pytest.raises(InvalidExtendDaysError):
        lib.borrow(user, book, 0)


@pytest.mark.regression
def test_invalid_extend_loan(create_lib):
    """
        Invalid number of days to extend a loan
    """
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    lib.borrow(user, book)
    loan = lib.loans[0]
    print(loan)
    with pytest.raises(InvalidExtendDaysError):
        loan.extend(-1)


@pytest.mark.regression
def test_loan_creation_with_invalid_user(create_lib):
    """
        Invalid loan initialization: invalid user provided
    """
    lib = create_lib
    with pytest.raises(LoanInitializationError):
        Loan("Krzysztof Pijor", lib.catalog[0], 1)


@pytest.mark.regression
def test_loan_creation_with_invalid_book(create_lib):
    """
        Invalid loan initialization: invalid book provided
    """
    lib = create_lib
    with pytest.raises(LoanInitializationError):
        Loan(lib.users_list[0], "The Hobbit", 1)


@pytest.mark.regression
def test_loan_creation_with_invalid_book_days(create_lib):
    """
        Invalid loan initialization: invalid days provided (str)
    """
    lib = create_lib
    with pytest.raises(LoanInitializationError):
        Loan(lib.users_list[0], lib.catalog[0], "1")


@pytest.mark.regression
def test_no_book_to_choose(create_lib):
    """
        No book available in the list
    """
    lib = create_lib
    books = lib.find_book_by_name("123")
    with pytest.raises(MissingBookError):
        lib.choose_book(books)


@pytest.mark.regression
def test_choose_with_one_option(create_lib):
    """
        Only one book is returned from choose_book
    """
    lib = create_lib
    books = lib.find_book_by_name("Dune")
    books = lib.choose_book(books)
    assert isinstance(books, Book)


@pytest.mark.regression
def test_choose_with_more_option(create_lib):
    """
        Choose a book from a list of two books (Book and EBook)
    """
    lib = create_lib
    books = lib.find_book_by_name("1984")
    with patch("builtins.input", return_value=2):
        books = lib.choose_book(books)
    assert isinstance(books, EBook)


@pytest.mark.regression
def test_matching_book_by_name(create_lib):
    """
        Find a book by a name (exist)
    """
    lib = create_lib
    result = lib.find_book_by_name(" Potop ")
    assert result is not None


@pytest.mark.regression
def test_no_matching_book_by_name(create_lib):
    """
        Find a book by a name (not exist)
    """
    lib = create_lib
    result = lib.find_book_by_name("Potopy")
    assert len(result) == 0


@pytest.mark.regression
def test_matching_book_by_genre(create_lib):
    """
        Find a book by a genre (exist)
    """
    lib = create_lib
    result = lib.find_books_by_genre("  historical fiction ")
    assert len(result) > 0


@pytest.mark.regression
def test_no_matching_book_by_genre(create_lib):
    """
        Find a book by a genre (not exist)
    """
    lib = create_lib
    result = lib.find_books_by_genre("poetry")
    assert result == []


@pytest.mark.regression
def test_matching_book_by_author(create_lib):
    """
        Find a book by an author (exist)
    """
    lib = create_lib
    result = lib.find_books_by_author(" Henryk Sienkiewicz  ")
    assert len(result) > 0


@pytest.mark.regression
def test_no_matching_book_by_author(create_lib):
    """
        Find a book by an author (not exist)
    """
    lib = create_lib
    result = lib.find_books_by_author("Krzysztof Pijor")
    assert result == []


@pytest.mark.regression
def test_find_existing_user(create_lib):
    """
        Find existing user
    """
    lib = create_lib
    user = lib.find_user("Anna Nowak")
    assert isinstance(user, User)


@pytest.mark.regression
def test_find_nonexistent_user(create_lib):
    """
        Attempt to find nonexistent user
    """
    lib = create_lib
    user = lib.find_user("Tomasz Nowak")
    assert not isinstance(user, User)


@pytest.mark.regression
def test_borrow_unavailable_book_twice(create_lib):
    """
        Attempt to borrow the unavailable book twice
    """
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


@pytest.mark.regression
def test_unregister_nonexistent_user(create_lib):
    """
        Attempt to unregister nonexistent user
    """
    lib = create_lib
    user = User("Krzysztof Pijor")
    with pytest.raises(MissingUserError):
        lib.unregister_user(user)


@pytest.mark.regression
def test_attempt_to_borrow_four_books(create_lib):
    """
        Attempt to borrow four books when the maximum allowed is three
    """
    lib = create_lib
    user = lib.users_list[0]
    for i, book in enumerate(lib.catalog, start=1):
        lib.borrow(user, book)
        if i == 4:
            break
    assert len(user.borrowed_physical_books) == 3
    assert user.waitlist is not None


@pytest.mark.regression
def test_attempt_remove_not_available_book_copy(create_lib):
    """
        Attempt to remove a not available book copy from the library
    """
    lib = create_lib
    book_copy = lib.catalog[0].copies[0]
    book_copy.is_available = False
    with pytest.raises(MissingBookError):
        lib.remove_book_copy(book_copy)


@pytest.mark.regression
def test_attempt_remove_nonexistent_book(create_lib):
    """
        Attempt to remove a nonexistent book from the library
    """
    lib = create_lib
    book = Book(
        "Nexus",
        "Yuval Noah Harari",
        [
            "non-fiction", "history",
            "technology", "society", "artificial intelligence"
        ],
        2024,
    )
    with pytest.raises(MissingBookError):
        lib.remove_book(book)


@pytest.mark.regression
def test_attempt_remove_nonexistent_book_copy(create_lib):
    """
        Attempt to remove a nonexistent book copy from the library
    """
    lib = create_lib
    book_copy = BookCopy(lib.catalog[0])
    with pytest.raises(MissingBookError):
        lib.remove_book_copy(book_copy)
