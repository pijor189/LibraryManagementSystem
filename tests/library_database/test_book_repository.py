import pytest

from exceptions.book_exceptions import ItemInitializationError, MissingItemError
from exceptions.library_exceptions import (
    BookCurrentlyBorrowedError,
    InvalidNumberOfBooksError,
)


@pytest.mark.smoke
def test_rejects_book_with_invalid_data(test_db):
    """
        Attempt to add book with invalid data
    """
    with pytest.raises(ItemInitializationError):
        test_db.book.add_book(
            "",
            "",
            "",
            0,
            0
        )


@pytest.mark.smoke
def test_rejects_ebook_with_invalid_data(test_db):
    """
        Attempt to add ebook with invalid data
    """
    with pytest.raises(ItemInitializationError):
        test_db.book.add_ebook(
            "",
            "",
            "",
            0,
            0
        )


@pytest.mark.smoke
def test_book_inventory_management(test_db):
    """
        1. Add more copies of book
        2. Reduce amount of book
        3. Remove a book from library
    """
    # step 1
    book_id = test_db.book.find_book_by_title("The Hobbit")[0]["id"]

    test_db.book.add_existing_book(book_id, 1)

    assert test_db.book.find_book_by_id(book_id)["amount"] == 2

    # step 2
    test_db.book.reduce_existing_book(book_id, 1)

    assert test_db.book.find_book_by_id(book_id)["amount"] == 1

    # step 3
    test_db.book.remove_book(book_id)

    assert not test_db.book.find_book_by_id(book_id)


@pytest.mark.smoke
def test_ebook_inventory_management(test_db):
    """
        Remove an ebook from library
    """
    ebook_id = test_db.book.find_book_by_title("Python 101")[0]["id"]

    test_db.book.remove_book(ebook_id)

    assert not test_db.book.find_book_by_id(ebook_id)


@pytest.mark.smoke
def test_invalid_amount_to_extend_book_copies(test_db):
    """
        Attempt to extend book copies with invalid amount
    """
    book_id = test_db.book.find_book_by_title("The Hobbit")[0]["id"]

    with pytest.raises(InvalidNumberOfBooksError):
        test_db.book.add_existing_book(book_id, 0)

    assert test_db.book.find_book_by_id(book_id)["amount"] == 1


@pytest.mark.smoke
def test_attempt_to_extend_not_existent_book(test_db):
    """
        Attempt to extend not existent book
    """
    with pytest.raises(MissingItemError):
        test_db.book.add_existing_book(0, 1)


@pytest.mark.smoke
def test_attempt_to_reduce_not_existent_book(test_db):
    """
        Attempt to reduce not existent book
    """
    with pytest.raises(MissingItemError):
        test_db.book.reduce_existing_book(0, 1)


@pytest.mark.smoke
def test_attempt_to_reduce_book_with_invalid_amount(test_db):
    """
        Attempt to reduce a book copies with invalid amount
    """
    with pytest.raises(InvalidNumberOfBooksError):
        test_db.book.reduce_existing_book(
            test_db.book.find_book_by_title("The Hobbit")[0]["id"],
            0
        )


@pytest.mark.smoke
def test_attempt_to_remove_not_existent_book(test_db):
    """
        Attempt to remove not existent book from library
    """
    with pytest.raises(MissingItemError):
        test_db.book.remove_book(0)


@pytest.mark.smoke
def test_attempt_to_remove_already_borrowed_book(test_db):
    """
        1. Borrow a book
        2. Attempt to remove already borrowed book from library
    """
    # step 1
    book_id = test_db.book.find_book_by_title("The Hobbit")[0]["id"]
    user_id = test_db.user.find_user_by_name("Tomasz Nowak")[0]["id"]
    test_db.borrow.borrow_book(user_id, book_id, 1)

    assert test_db.user.get_all_books_from_user(user_id)

    # step 2
    with pytest.raises(BookCurrentlyBorrowedError):
        test_db.book.remove_book(book_id)


@pytest.mark.smoke
def test_attempt_to_remove_already_borrowed_ebook(test_db):
    """
        1. Borrow an ebook
        2. Attempt to remove already borrowed ebook from library
    """
    # step 1
    ebook_id = test_db.book.find_book_by_title("Python 101")[0]["id"]
    user_id = test_db.user.find_user_by_name("Tomasz Nowak")[0]["id"]
    test_db.borrow.borrow_book(user_id, ebook_id, 1)

    assert test_db.user.get_all_ebooks_from_user(user_id)

    # step 2
    with pytest.raises(BookCurrentlyBorrowedError):
        test_db.book.remove_book(ebook_id)


@pytest.mark.smoke
def test_get_all_available_books(test_db):
    """
        Get all available books from library
    """
    all_books = len(test_db.book.get_all_books())

    book_id = test_db.book.find_book_by_title("The Hobbit")[0]["id"]
    user_id = test_db.user.find_user_by_name("Tomasz Nowak")[0]["id"]
    test_db.borrow.borrow_book(user_id, book_id, 1)

    all_available_books = len(test_db.book.get_available_books())

    assert all_books
    assert all_available_books
    assert all_books > all_available_books
    assert test_db.user.get_all_books_from_user(user_id)


@pytest.mark.smoke
def test_find_book_by_genre(test_db):
    """
        Find a book by a genre
    """
    assert test_db.book.find_book_by_genre("historical fiction")
    assert not test_db.book.find_book_by_genre("abc")


@pytest.mark.smoke
def test_find_book_by_author(test_db):
    """
        Find a book by an author
    """
    assert test_db.book.find_book_by_author("Henryk Sienkiewicz")
    assert not test_db.book.find_book_by_author("Krzysztof Nowak")
