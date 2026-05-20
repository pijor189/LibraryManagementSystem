from fastapi import APIRouter
from pydantic import BaseModel
from .app_state import library
from library.user import User

router = APIRouter()


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    books: list
    ebooks: list


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        books=user.borrowed_physical_books,
        ebooks=user.borrowed_ebooks
    )


@router.get("/users", response_model=list[UserResponse])
def get_users():
    users = library.get_all_users()

    return [user_to_response(user) for user in users]


@router.post("/users")
def add_user(user: UserCreate):
    new_user = User(user.name)
    library.register_user(new_user)

    return user_to_response(new_user)
