from library.user import User
from library.book import Book, EBook
from library.exceptions import InvalidUser, InvalidBook, NoBook, NoUser, InvalidNumberOfBooks
import logging
import pytest

"""
    Create a library
"""
def test_create_lib(create_lib):
    lib = create_lib
    assert len(lib.get_all_books()) == 10 + 4
    assert len(lib.get_all_users()) == 3

"""
    Create a invalid user
"""
def test_invalid_user():
    with pytest.raises(InvalidUser):
        user = User('')

"""
    Create a invalid book (invalid title)
"""
def test_invalid_book_invalid_title():
    with pytest.raises(InvalidBook):
        book = Book(1, "Henryk Sienkiewicz", "historical fiction", 1900)

"""
    Create a invalid book (empty title)
"""
def test_invalid_book_empty_title():
    with pytest.raises(InvalidBook):
        book = Book("", "Henryk Sienkiewicz", "historical fiction", 1900)

"""
    Create a invalid book (empty author)
"""
def test_invalid_book_empty_author():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", "", "historical fiction", 1900)

"""
    Create a invalid book (invalid author)
"""
def test_invalid_book_invalid_author():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", 1, "historical fiction", 1900, 1)

"""
    Create a invalid book (empty genre - string)
"""
def test_invalid_book_empty_genre_str():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", "Henryk Sienkiewicz", "", 1900)

"""
    Create a invalid book (empty genre - list)
"""
def test_invalid_book_empty_genre_list():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", "Henryk Sienkiewicz", [], 1900)

"""
    Create a invalid book (invalid genre)
"""
def test_invalid_book_invalid_genre():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", "Henryk Sienkiewicz", 1, 1900)

"""
    Create a invalid book (invalid amount)
"""
def test_invalid_book_invalid_amout():
    with pytest.raises(InvalidBook):
        book = Book("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "1")

"""
    Create a invalid ebook (file size not int)
"""
def test_invalid_ebook_invalid_file_size():
    with pytest.raises(InvalidBook):
        book = EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, "")

"""
    Create a invalid ebook (invalid file size)
"""
def test_invalid_ebook_too_small_file_size():
    with pytest.raises(InvalidBook):
        book = EBook("Krzyżacy", "Henryk Sienkiewicz", "historical fiction", 1900, -1)

"""
    Book not provided to add_book function
"""
def test_book_not_provided_to_add(create_lib, caplog):
    lib = create_lib
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.add_book("Potop")
    assert caplog.records[0].levelname == "ERROR"

"""
    User not provided to register_user function
"""
def test_user_not_provided_to_register(create_lib, caplog):
    lib = create_lib
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoUser):
            lib.register_user("Krzysztof")
    assert caplog.records[0].levelname == "ERROR"

"""
    Not register user provided to borrow function
"""
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
def test_not_added_book_provided_to_borrow(create_lib, caplog):
    lib = create_lib
    user = lib.users_list[0]
    book = Book("Nexus", "Yuval Noah Harari", ["non-fiction", "history", "technology", "society",
                 "artificial intelligence"], 2024)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.borrow(user, book)
    assert caplog.records[0].levelname == "ERROR"

"""
    Not register user provided to borrow function
"""
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
def test_invalid_book_to_add_more_copies(create_lib, caplog):
    lib = create_lib
    book = Book("Nexus", "Yuval Noah Harari", ["non-fiction", "history", "technology", "society",
                                               "artificial intelligence"], 2024)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(NoBook):
            lib.add_existing_book(book, 1)
    assert caplog.records[0].levelname == "ERROR"

"""
    Invalid number of books to add
"""
def test_invalid_number_books_add(create_lib, caplog):
    lib = create_lib
    book = lib.catalog[0]
    with caplog.at_level(logging.ERROR):
        with pytest.raises(InvalidNumberOfBooks):
            lib.add_existing_book(book, 0)
    assert caplog.records[0].levelname == "ERROR"

"""
    Find a book by a name (exist)
"""
def test_matching_book_by_name(create_lib):
    lib = create_lib
    result = lib.find_book_by_name(" Potop ")
    assert result is not None

"""
    Find a book by a name (not exist)
"""
def test_no_matching_book_by_name(create_lib):
    lib = create_lib
    result = lib.find_book_by_name("Potopy")
    assert result is None

"""
    Find a book by a genre (exist)
"""
def test_matching_book_by_genre(create_lib):
    lib = create_lib
    result = lib.find_books_by_genre("  historical fiction ")
    assert len(result) > 0

"""
    Find a book by a genre (not exist)
"""
def test_no_matching_book_by_genre(create_lib):
    lib = create_lib
    result = lib.find_books_by_genre("poetry")
    assert result == []

"""
    Find a book by an author (exist)
"""
def test_matching_book_by_author(create_lib):
    lib = create_lib
    result = lib.find_books_by_author(" Henryk Sienkiewicz  ")
    assert len(result) > 0

"""
    Find a book by an author (not exist)
"""
def test_no_matching_book_by_author(create_lib):
    lib = create_lib
    result = lib.find_books_by_author("Krzysztof Pijor")
    assert result == []

"""
1. Create a library and check all available books
2. Create a user and a book. Then user borrows the book and check again all available books 
"""
def test_get_available_books(create_lib):
    # step 1
    lib = create_lib
    available_books = lib.get_available_books()
    assert len(available_books) == len(lib.catalog)

    # step 2
    user = lib.users_list[0]
    book = lib.catalog[0]
    lib.borrow(user, book)
    available_books = lib.get_available_books()
    assert len(available_books) != len(lib.catalog)

"""
1. Create a library, a user and a book
2. User borrow a book titled '1984'
3. User return a book
"""
def test_return_book(create_lib):
    # step 1
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]

    # step 2
    lib.borrow(user, book)
    assert len(user.borrowed_physical_books) == 1
    assert any(b in user.borrowed_physical_books for b in book.copies)

    # step 3
    lib.return_book(user, book)
    assert len(user.borrowed_physical_books) == 0
    assert any(b not in user.borrowed_physical_books for b in book.copies)

"""
1. Create a library, a user and a book
2. User borrow an ebook titled 'Python 101'
"""
def test_borrow_ebook(create_lib):
    # step 1
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[13]

    # step 2
    lib.borrow(user, book)
    assert len(user.borrowed_physical_books) == 0
    assert len(user.borrowed_ebooks) == 1
    assert book in user.borrowed_ebooks

"""
1. Create a library
2. Add one more copy of a book '1984'
"""
def test_add_more_books(create_lib):
    # step 1
    lib = create_lib
    user = lib.users_list[0]
    book = lib.catalog[0]
    assert book.amount == 1
    assert len(lib.books_id) == 14

    # step 2
    lib.add_existing_book(book, 1)
    assert book.amount == 2
    assert len(lib.books_id) == 15

"""
1. Create a library
2. First user borrow a book titled '1984'
3. Second user borrow 3 another books
4. Second user want to borrow a book titled '1984', but it is not avalaible and he has 3 book already, 
    so he goes to the queue
5. First user return a book titled '1984', second user is in the queue, but he reached a limit
6. Second user return a book
7. Second user try again to borrow a book titled '1984'
"""
def test_borrow_book_and_process_waitlist(create_lib):
    # step 1
    lib = create_lib

    # step 2
    user1 = lib.users_list[0]
    book1 = lib.catalog[0]
    lib.borrow(user1, book1)
    assert len(user1.borrowed_physical_books) == 1
    assert any(b in user1.borrowed_physical_books for b in book1.copies)

    # step 3
    user2 = lib.users_list[1]
    book2 = lib.catalog[1]
    book3 = lib.catalog[2]
    book4 = lib.catalog[3]
    lib.borrow(user2, book2)
    lib.borrow(user2, book3)
    lib.borrow(user2, book4)
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)

    # step 4
    lib.borrow(user2, book1)
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)
    assert user2 in book1.waitlist

    # step 5
    lib.return_book(user1, book1)
    assert any(b not in user1.borrowed_physical_books for b in book1.copies)
    assert len(user1.borrowed_physical_books) == 0
    assert user2 in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)

    # step 6
    lib.return_book(user2, book2)
    assert user2 in book1.waitlist
    assert len(user2.borrowed_physical_books) == 2
    assert any(b not in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)

    # step 7
    lib.borrow(user2, book1)
    assert user2 not in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book1.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)

"""
1. Create a library
2. First user borrow a book titled '1984'
3. Second user borrow 3 another books
4. Second user want to borrow a book titled '1984', but it is not avalaible and he has 3 book already, 
    so he goes to the queue
5. Third user want to borrow a book titled '1084', but it is not avalaible, so he goes to the queue
6. First user return a book titled '1984', third user will borrow a book titled '1984'
"""
def test_process_waitlist_for_more_users(create_lib):
    # step 1
    lib = create_lib

    # step 2
    user1 = lib.users_list[0]
    book1 = lib.catalog[0]
    lib.borrow(user1, book1)
    assert len(user1.borrowed_physical_books) == 1
    assert any(b in user1.borrowed_physical_books for b in book1.copies)

    # step 3
    user2 = lib.users_list[1]
    book2 = lib.catalog[1]
    book3 = lib.catalog[2]
    book4 = lib.catalog[3]
    lib.borrow(user2, book2)
    lib.borrow(user2, book3)
    lib.borrow(user2, book4)
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)

    # step 4
    lib.borrow(user2, book1)
    assert len(user2.borrowed_physical_books) == 3
    assert any(b in user2.borrowed_physical_books for b in book2.copies)
    assert any(b in user2.borrowed_physical_books for b in book3.copies)
    assert any(b in user2.borrowed_physical_books for b in book4.copies)
    assert user2 in book1.waitlist

    # step 5
    user3 = lib.users_list[2]
    lib.borrow(user3, book1)
    assert user2 in book1.waitlist
    assert any(b not in user2.borrowed_physical_books for b in book1.copies)
    assert user3 in book1.waitlist
    assert any(b not in user3.borrowed_physical_books for b in book1.copies)

    # step 6
    lib.return_book(user1, book1)
    assert any(b not in user1.borrowed_physical_books for b in book1.copies)
    assert len(user1.borrowed_physical_books) == 0
    assert user2 in book1.waitlist
    assert len(user2.borrowed_physical_books) == 3
    assert any(b not in user2.borrowed_physical_books for b in book1.copies)
    assert user3 not in book1.waitlist
    assert any(b in user3.borrowed_physical_books for b in book1.copies)
