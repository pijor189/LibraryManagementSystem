from datetime import date, timedelta

import pytest

from exceptions.library_exceptions import UserHasBorrowedItemsError


@pytest.mark.nightly
def test_end_to_end_book_borrowing_with_queue_management(test_db):
    """
        1. Add book to library
        2. Register user to library
        3. Borrow a book by new user
        4. Extend book loan by new user
        5. Another user borrow 3 books
        6. Attempt to borrow not available
            book by another users
        7. Return a book by new user and manage queue
    """

    # step 1
    book_id = test_db.book.add_book(
        "Clean Code",
        "Robert Martin",
        "programming",
        2008,
        1
    )

    book = test_db.book.find_book_by_id(book_id)

    assert book is not None
    assert book["title"] == "Clean Code"

    # step 2
    first_user_id = test_db.user.register_user("Krzysztof Nowak")
    first_user = test_db.user.find_user_by_id(first_user_id)

    assert first_user is not None
    assert first_user["name"] == "Krzysztof Nowak"

    # step 3
    test_db.borrow.borrow_book(first_user_id, book_id, 1)
    borrowed_books = test_db.user.get_all_books_from_user(first_user_id)

    assert borrowed_books[0]["title"] == "Clean Code"

    # step 4
    test_db.borrow.extend_loan(book_id, first_user_id, 1)
    due_to = test_db.borrow.db.fetchone(
        """
        SELECT due_to
        FROM borrowings
        WHERE book_id = ?
            AND user_id = ?
            AND returned_at IS NULL
        """,
        (
            book_id,
            first_user_id
        )
    )

    assert date.fromisoformat(due_to["due_to"]) == date.today() + timedelta(days=2)

    # step 5
    second_user = test_db.user.find_user_by_name("Tomasz Nowak")
    second_user_id = second_user[0]["id"]
    test_db.borrow.borrow_book(
        second_user_id,
        test_db.book.find_book_by_title("The Hobbit")[0]["id"]
    )
    test_db.borrow.borrow_book(
        second_user_id,
        test_db.book.find_book_by_title("Dune")[0]["id"]
    )
    test_db.borrow.borrow_book(
        second_user_id,
        test_db.book.find_book_by_title("1984")[0]["id"]
    )
    test_db.borrow.borrow_book(second_user_id, book_id, 1)

    waitlist = test_db.waitlist.db.fetchone(
        """
        SELECT user_id
        FROM waitlist
        WHERE user_id = ?
            AND book_id = ?
        """,
        (
            second_user_id,
            book_id
        )
    )

    assert test_db.user.get_all_books_from_user(second_user_id)
    assert second_user_id == waitlist["user_id"]

    # step 6
    third_user = test_db.user.find_user_by_name("Adam Kowalski")
    third_user_id = third_user[0]["id"]
    test_db.borrow.borrow_book(third_user_id, book_id, 1)
    waitlist = test_db.waitlist.db.fetchone(
        """
        SELECT user_id
        FROM waitlist
        WHERE user_id = ?
            AND book_id = ?
        """,
        (
            third_user_id,
            book_id
        )
    )

    assert not test_db.user.get_all_books_from_user(third_user_id)
    assert third_user_id == waitlist["user_id"]

    # step 7
    test_db.borrow.return_book(first_user_id, book_id)
    waitlist = test_db.waitlist.db.fetchone(
        """
        SELECT user_id
        FROM waitlist
        WHERE user_id = ?
            AND book_id = ?
        """,
        (
            second_user_id,
            book_id
        )
    )

    assert not test_db.user.get_all_books_from_user(first_user_id)
    assert test_db.user.get_all_books_from_user(second_user_id)
    assert second_user_id == waitlist["user_id"]
    assert test_db.user.get_all_books_from_user(third_user_id)


@pytest.mark.nightly
def test_unregister_requires_returning_all_borrowed_items(test_db):
    """
        1. Add ebook to library
        2. Borrow a book and an ebook by user
        3. Attempt to unregister a user with borrowed items
        4. Return all items by user
        5. Unregister a user
    """

    # step 1
    ebook_id = test_db.book.add_ebook(
        "Clean Code",
        "Robert Martin",
        "programming",
        2008,
        2000
    )

    ebook = test_db.book.find_book_by_id(ebook_id)
    user = test_db.user.find_user_by_name("Adam Kowalski")
    user_id = user[0]["id"]

    assert ebook is not None
    assert ebook["title"] == "Clean Code"

    # step 2
    book = test_db.book.find_book_by_title("The Hobbit")
    test_db.borrow.borrow_book(user_id, book[0]["id"], 30)
    borrowed_books = test_db.user.get_all_books_from_user(user_id)

    test_db.borrow.borrow_book(user_id, ebook_id)
    borrowed_ebooks = test_db.user.get_all_ebooks_from_user(user_id)

    assert borrowed_books[0]["title"] == "The Hobbit"
    assert borrowed_ebooks[0]["title"] == "Clean Code"

    # step 5
    with pytest.raises(UserHasBorrowedItemsError):
        test_db.user.unregister_user(user_id)
        user = test_db.user.find_user_by_id(user_id)

    assert user is not None

    # step 4
    test_db.borrow.return_all_items(user_id)

    assert not test_db.user.get_all_books_from_user(user_id)
    assert not test_db.user.get_all_ebooks_from_user(user_id)

    # step 5
    test_db.user.unregister_user(user_id)
    user = test_db.user.find_user_by_id(user_id)

    assert user is None

