import pytest

from exceptions.book_exceptions import MissingItemError


@pytest.mark.smoke
def test_borrow_not_existent_book(test_db):
    """
        Attempt to borrow not existent book from library
    """
    user_id = test_db.user.find_user_by_name("Tomasz Nowak")[0]["id"]

    with pytest.raises(MissingItemError):
        test_db.borrow.borrow_book(user_id, 0)

    assert not test_db.user.get_all_books_from_user(user_id)

