import logging

import pytest

from exceptions.book_exceptions import MissingItemError
from exceptions.library_exceptions import UserHasBorrowedItemsError
from library.user import User

logging.disable(logging.CRITICAL)


@pytest.mark.regression
def test_extend_ebook(create_lib):
    """
        1. Borrow an ebook
        2. Attempt to extend the ebook
    """
    # step 1
    lib = create_lib
    user = next(iter(lib.users_list.values()))
    book = list(lib.catalog.values())[13]
    lib.borrow(user, book)
    loan = next(iter(lib.loans.values()))
    assert loan.due_date is None
    assert not loan.is_overdue()

    # step 2
    loan.extend(1)
    assert loan.due_date is None
    assert not loan.is_overdue()


@pytest.mark.regression
def test_extend_book(create_lib):
    """
        1. Borrow a book
        2. Attempt to extend a book by 30 days
    """
    # step 1
    lib = create_lib
    user = next(iter(lib.users_list.values()))
    book = next(iter(lib.catalog.values()))
    lib.borrow(user, book, 1)
    loan = next(iter(lib.loans.values()))
    assert loan.due_date is not None
    assert not loan.is_overdue()

    # step 2
    loan.extend(30)
    assert loan.due_date is not None
    assert not loan.is_overdue()


@pytest.mark.regression
def test_extend_book_above_limit(create_lib):
    """
        1. Borrow a book
        2. Attempt to extend a book by 31 days (1 above the limit)
    """
    # step 1
    lib = create_lib
    user = next(iter(lib.users_list.values()))
    book = next(iter(lib.catalog.values()))
    lib.borrow(user, book, 1)
    loan = next(iter(lib.loans.values()))
    assert loan.due_date is not None
    assert not loan.is_overdue()

    # step 2
    loan.extend(31)
    assert loan.due_date is not None
    assert not loan.is_overdue()


@pytest.mark.regression
def test_unregister_user(create_lib):
    """
        1. Create a library and a user. Register the user in the library
        2. The newly created user borrows a book and an ebook
        3. The user returns all borrowed items to the library
        4. Unregister the user
    """
    # step 1
    lib = create_lib
    user = User("Krzysztof Pijor")
    lib.register_user(user)
    assert user in lib.users_list.values()

    # step 2
    book = list(lib.catalog.values())[0]
    ebook = list(lib.catalog.values())[13]
    lib.borrow(user, book)
    lib.borrow(user, ebook)
    assert book.id in user.borrowed_physical_books.values()
    assert ebook.id in user.borrowed_ebooks.values()

    # step 3
    lib.return_all_items(user)
    assert len(user.borrowed_physical_books) == 0
    assert len(user.borrowed_ebooks) == 0

    # step 4
    lib.unregister_user(user)
    assert user not in lib.users_list.values()


@pytest.mark.regression
def test_unregister_user_with_items_in_list(create_lib):
    """
        1. Create a library and a user. Register the user in the library
        2. The newly created user borrows a book and an ebook
        3. Attempt to unregister the user with borrowed books
    """
    # step 1
    lib = create_lib
    user = User("Krzysztof Pijor")
    lib.register_user(user)
    assert user.id in lib.users_list

    # step 2
    book = list(lib.catalog.values())[0]
    ebook = list(lib.catalog.values())[13]
    lib.borrow(user, book)
    lib.borrow(user, ebook)
    assert book.id in user.borrowed_physical_books.values()
    assert ebook.id in user.borrowed_ebooks.values()

    # step 3
    with pytest.raises(UserHasBorrowedItemsError):
        lib.unregister_user(user)
    assert user.id in lib.users_list


@pytest.mark.regression
def test_get_available_books(create_lib):
    """
        1. Create a library and check all available books
        2. Create a user and a book.
            Then user borrows the book and check again all available books
    """
    # step 1
    lib = create_lib
    available_books = lib.get_available_books()
    assert len(available_books) == len(lib.catalog)

    # step 2
    user = next(iter(lib.users_list.values()))
    book = next(iter(lib.catalog.values()))
    lib.borrow(user, book)
    available_books = lib.get_available_books()
    assert len(available_books) != len(lib.catalog)


@pytest.mark.smoke
def test_return_book(create_lib):
    """
        1. Create a library, a user and a book
        2. User borrow a book titled '1984'
        3. User return a book
    """
    # step 1
    lib = create_lib
    user = next(iter(lib.users_list.values()))
    book = next(iter(lib.catalog.values()))

    # step 2
    lib.borrow(user, book)
    print(user.borrowed_physical_books)
    assert len(user.borrowed_physical_books) == 1
    assert book.id in user.borrowed_physical_books.values()

    # step 3
    lib.return_book(user, book)
    assert len(user.borrowed_physical_books) == 0
    assert book.id not in user.borrowed_physical_books.values()


@pytest.mark.smoke
def test_borrow_ebook(create_lib):
    """
        1. Create a library, a user and a book
        2. User borrow an ebook titled 'Python 101'
    """
    # step 1
    lib = create_lib
    user = next(iter(lib.users_list.values()))
    book = list(lib.catalog.values())[13]

    # step 2
    lib.borrow(user, book)
    assert len(user.borrowed_physical_books) == 0
    assert len(user.borrowed_ebooks) == 1
    assert book.id in user.borrowed_ebooks.values()


@pytest.mark.smoke
def test_add_and_reduce_books(create_lib):
    """
        1. Create a library
        2. Add one more copy of a book '1984'
        3. Reduce one copy of a book '1984'
    """
    # step 1
    lib = create_lib
    book = next(iter(lib.catalog.values()))
    assert book.amount == 1
    assert len(lib.catalog) == 14

    # step 2
    lib.add_existing_book(book, 1)
    assert book.amount == 2

    # step 3
    lib.reduce_book_amount(book, 1)
    assert book.amount == 1


@pytest.mark.regression
def test_remove_book(create_lib):
    """
        1. Create a library and let the user borrow a book
        2. Attempt to remove the book from the library
        3. User return a book and then the library
            can remove it from the catalog
    """
    # step 1
    lib = create_lib
    book = next(iter(lib.catalog.values()))
    user = next(iter(lib.users_list.values()))
    lib.borrow(user, book)
    assert user.borrowed_physical_books

    # step 2
    with pytest.raises(MissingItemError):
        lib.remove_item(book)
    assert len(lib.catalog) == 14
    assert user.borrowed_physical_books

    # step 3
    lib.return_book(user, book)
    lib.remove_item(book)
    assert len(lib.catalog) == 13
    assert not user.borrowed_physical_books


@pytest.mark.regression
def test_remove_ebook(create_lib):
    """
        1. Create a library and let the user borrow an ebook
        2. Remove the ebook from the library and from the user's ebook list
    """
    # step 1
    lib = create_lib
    book = list(lib.catalog.values())[13]
    user = list(lib.users_list.values())[0]
    lib.borrow(user, book)

    # step 2
    lib.remove_item(book)
    assert not user.borrowed_ebooks
    assert len(lib.catalog) == 13


@pytest.mark.nightly
def test_borrow_book_and_process_waitlist(create_lib):
    """
        1. Create a library
        2. First user borrow a book titled '1984'
        3. Second user borrow 3 another books
        4. Second user want to borrow a book titled '1984',
            but it is not available and he has 3 book already,
            so he goes to the queue
        5. First user return a book titled '1984',
            second user is in the queue, but he reached a limit
        6. Second user return a book
        7. Second user try again to borrow a book titled '1984'
    """
    # step 1
    lib = create_lib

    # step 2
    user1 = list(lib.users_list.values())[0]
    book1 = list(lib.catalog.values())[0]
    lib.borrow(user1, book1)
    assert len(user1.borrowed_physical_books) == 1
    assert book1.id in user1.borrowed_physical_books.values()

    # step 3
    user2 = list(lib.users_list.values())[1]
    book2 = list(lib.catalog.values())[1]
    book3 = list(lib.catalog.values())[2]
    book4 = list(lib.catalog.values())[3]
    lib.borrow(user2, book2)
    lib.borrow(user2, book3)
    lib.borrow(user2, book4)
    assert len(user2.borrowed_physical_books) == 3
    assert book2.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()

    # step 4
    lib.borrow(user2, book1)
    assert len(user2.borrowed_physical_books) == 3
    assert book2.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()
    assert user2.id in book1.waitlist

    # step 5
    lib.return_book(user1, book1)
    assert book1.id not in user1.borrowed_physical_books.values()
    assert len(user1.borrowed_physical_books) == 0
    assert user2.id in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert book2.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()

    # step 6
    lib.return_book(user2, book2)
    assert user2.id in book1.waitlist
    assert len(user2.borrowed_physical_books) == 2
    assert book2.id not in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()

    # step 7
    lib.borrow(user2, book1)
    assert user2.id not in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert book1.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()


@pytest.mark.nightly
def test_process_waitlist_for_more_users(create_lib):
    """
        1. Create a library
        2. First user borrow a book titled '1984'
        3. Second user borrow 3 another books
        4. Second user want to borrow a book titled '1984',
            but it is not available and he has 3 book already,
            so he goes to the queue
        5. Third user want to borrow a book titled '1084',
            but it is not available, so he goes to the queue
        6. First user return a book titled '1984',
            third user will borrow a book titled '1984'
    """
    # step 1
    lib = create_lib

    # step 2
    user1 = list(lib.users_list.values())[0]
    book1 = list(lib.catalog.values())[0]
    lib.borrow(user1, book1)
    assert len(user1.borrowed_physical_books) == 1
    assert book1.id in user1.borrowed_physical_books.values()

    # step 3
    user2 = list(lib.users_list.values())[1]
    book2 = list(lib.catalog.values())[1]
    book3 = list(lib.catalog.values())[2]
    book4 = list(lib.catalog.values())[3]
    lib.borrow(user2, book2)
    lib.borrow(user2, book3)
    lib.borrow(user2, book4)
    assert len(user2.borrowed_physical_books) == 3
    assert book2.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()

    # step 4
    lib.borrow(user2, book1)
    assert len(user2.borrowed_physical_books) == 3
    assert book2.id in user2.borrowed_physical_books.values()
    assert book3.id in user2.borrowed_physical_books.values()
    assert book4.id in user2.borrowed_physical_books.values()
    assert user2.id in book1.waitlist

    # step 5
    user3 = list(lib.users_list.values())[2]
    lib.borrow(user3, book1)
    assert user2.id in book1.waitlist
    assert book1.id not in user2.borrowed_physical_books.values()
    assert user3.id in book1.waitlist
    assert book1.id not in user3.borrowed_physical_books.values()

    # step 6
    lib.return_book(user1, book1)
    assert book1.id not in user1.borrowed_physical_books.values()
    assert len(user1.borrowed_physical_books) == 0
    assert user2.id in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert book1.id not in user2.borrowed_physical_books.values()
    assert user3.id not in book1.waitlist
    assert book1.id in user3.borrowed_physical_books.values()
