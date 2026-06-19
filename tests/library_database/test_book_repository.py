import pytest

from repositories.book_repository import BookRepository
from repositories.borrowing_repository import BorrowingRepository
from repositories.user_repository import UserRepository
from repositories.waitlist_repository import WaitlistRepository


@pytest.mark.smoke
def test_add_book(test_db):
    repo = BookRepository(test_db)

    book_id = repo.add_book(
        "Clean Code",
        "Robert Martin",
        "programming",
        2008,
        1
    )

    book = repo.find_book_by_id(book_id)

    user = UserRepository(test_db)
    borrow = BorrowingRepository(test_db, repo, user, None)
    waitlist = WaitlistRepository(test_db, borrow)
    borrow.waitlist_repo = waitlist

    user_id = user.register_user("Krzysztof Nowak")
    borrow.borrow_book(user_id, book_id, 1)
    borrow.return_all_items(user_id)

    assert book is not None
    assert book["title"] == "Clean Code"


@pytest.mark.smoke
def test_add_ebook(test_db):
    repo = BookRepository(test_db)

    ebook_id = repo.add_ebook(
        "Clean Code",
        "Robert Martin",
        "programming",
        2008,
        2000
    )

    ebook = repo.find_book_by_id(ebook_id)

    assert ebook is not None
    assert ebook["title"] == "Clean Code"

