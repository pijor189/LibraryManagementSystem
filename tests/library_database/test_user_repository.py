import pytest

from exceptions.user_exceptions import MissingUserError, UserInitializationError


@pytest.mark.smoke
def test_invalid_user_flow(test_db):
    """
        Attempt to register user with invalid data
    """
    with pytest.raises(UserInitializationError):
        test_db.user.register_user("")

    with pytest.raises(MissingUserError):
        test_db.user.unregister_user("")

