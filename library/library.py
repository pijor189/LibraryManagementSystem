from .config import logger
from .book import Item, Book, EBook
from .user import User
from .loan import Loan
from exceptions.book_exceptions import MissingItemError
from exceptions.user_exceptions import MissingUserError
from exceptions.library_exceptions import (
    InvalidNumberOfBooksError, UserHasBorrowedItemsError
)
from utils.uid import generate_uid
from datetime import datetime


class Library:
    def __init__(self):
        self.catalog = {}
        self.users_list = {}
        self.loans = {}
        self.items_id = set()
        self.users_id = set()
        self.loans_id = set()

    def __str__(self):
        return f"List of books: {self.catalog}\nUsers: {self.users_list}"

    def add_book(self, item: Item) -> None:
        """
            Add a new book or ebook to the library catalog
            and assign unique IDs to it and its copies
        """
        if isinstance(item, Book) or isinstance(item, EBook):
            item.id = generate_uid(self.items_id)
            self.catalog[item.id] = item
            logger.info(f"{item.title} was added to the library")
        else:
            raise MissingItemError(f"There is no item {item} \
                matching the one you provided")

    def add_existing_book(self, book: Book, amount) -> None:
        """Add additional copies of an existing book in the library catalog"""
        book_in_list = self.check_book(book)
        if amount < 1:
            raise InvalidNumberOfBooksError("Invalid number of books to add")
        book_in_list.amount += amount

    def create_loan(
            self, user: User, book: Book | EBook, days: int = Loan.MAX_DAYS
        ) -> str:
        """Create a loan history record and generate a unique ID for it"""
        loan = Loan(user, book, days)
        loan.id = generate_uid(self.loans_id)
        self.loans[loan.id] = loan

        return loan.id

    def reduce_book_amount(self, book: Book, amount: int) -> None:
        """Reduce a book copies from the library if it is available"""
        if book.id not in self.catalog.keys():
            raise MissingItemError("There is no book like that \
                in the library")
        if not book.is_book_available():
            raise MissingItemError("The book is not available \
                and cannot be removed")
        if amount >= book.amount:
            raise InvalidNumberOfBooksError("Invalid amount \
                of books to remove")
        book.amount -= amount

    def remove_item(self, item: Item) -> None:
        """
            Remove an item from the catalog along with all its copies
            if it is a physical book. For ebooks,
            also remove related loans.
        """
        if item.id not in self.catalog.keys():
            raise MissingItemError("There is no item like that \
                in the library")
        if isinstance(item, EBook):
            for val in self.loans.values():
                if item.id == val.book_id:
                    user = self.find_user_by_id(val.user_id)
                    user.borrowed_ebooks.pop(val.id)
            self.catalog.pop(item.id)
        elif isinstance(item, Book):
            if not item.is_book_available():
                raise MissingItemError("The book is not available \
                    and cannot be removed")
            # if all copies are available, remove them and the original item
            self.catalog.pop(item.id)

    def check_user(self, user: User) -> User:
        """
            Validate that a user exists in the library
            and return the user object
        """
        user_in_list = next(
            (val for key, val in self.users_list.items() if key == user.id),
            None
        )

        if not user_in_list:
            raise MissingUserError(f"There is no user {user.name} \
                matching the one you provided")

        return user_in_list

    def check_book(self, item: Item) -> Book | EBook:
        """Validate that an item exists in the library catalog and return it"""
        book_in_list = next(
            (val for key, val in self.catalog.items() if key == item.id), None
        )

        if not book_in_list:
            raise MissingItemError(
                "There is no item matching the one you provided"
            )

        return book_in_list

    def register_user(self, user: User) -> None:
        """Register a new user in the library and assign a unique ID"""
        if isinstance(user, User):
            user.id = generate_uid(self.users_id)
            self.users_list[user.id] = user
            logger.info(f"User: {user.name} was registered in library")
        else:
            raise MissingUserError(f"There is no user {user} \
                matching the one you provided")

    def unregister_user(self, user: User) -> None:
        """Unregister a user from the library if they have no borrowed items"""
        user_in_list = self.check_user(user)

        if any(
            [
                user_in_list.borrowed_physical_books,
                user_in_list.borrowed_ebooks,
            ]
        ):
            raise UserHasBorrowedItemsError(
                f"{user_in_list.name} has borrowed books"
            )

        self.users_id.remove(user_in_list.id)
        self.users_list.pop(user_in_list.id)

    @staticmethod
    def choose_book(results: list[Book | EBook]) -> Book | EBook:
        """
            Allow the user to choose a book when multiple matches are found.
            Raises NoBook if no books are available.
        """
        if not results:
            raise MissingItemError("There is no book to choose from")

        if len(results) == 1:
            return results[0]

        logger.info("Found multiple versions:")

        for index, book in enumerate(results, start=1):
            book_type = "EBook" if isinstance(book, EBook) else "Book"
            print(f"{index}. {book.title} [{book_type}]")

        choice = int(input("Choose version: ")) - 1

        return results[choice]

    def borrow(
        self, user: User, item: Item | list[Item], days: int = Loan.MAX_DAYS
    ) -> None:
        """Borrow a book or ebook for a given user"""

        user_in_list = self.check_user(user)
        item_in_list = self.check_book(item)

        if isinstance(item_in_list, EBook):
            self.borrow_ebook(user_in_list, item_in_list)
        elif isinstance(item_in_list, Book):
            self.borrow_book(user_in_list, item_in_list, days)

    def borrow_ebook(self, user: User, ebook: EBook) -> None:
        """Assign an ebook to a user and create a loan record"""
        loan_id = self.create_loan(user, ebook)
        user.borrowed_ebooks[loan_id] = ebook.id
        logger.info(f"User: {user.name} borrow ebook: {ebook.title}")

    def borrow_book(self, user: User, book: Book, days: int) -> None:
        """
            Borrow a physical book if available,
            otherwise add the user to the waitlist
        """
        if any(book.waitlist) or not book.is_book_available():
            logger.info(f"Book '{book.title}' is not available,\
                {user} added to waitlist")
            self.add_to_waitlist(user, book)
            if book.is_book_available():
                self.process_waitlist(book)
            return

        if len(user.borrowed_physical_books) < user.LIMIT_OF_BOOKS:
            loan_id = self.create_loan(user, book, days)
            book.borrowed += 1
            user.borrowed_physical_books[loan_id] = book.id
            logger.info(f"User: {user.name} borrow book: {book.title}")
        else:
            logger.warning(f"User {user.name} can borrow maximum 3 books")
            self.add_to_waitlist(user, book)

    def return_book(self, user: User, book: Book) -> None:
        """
            Return a borrowed physical book and update its availability.
            Processes waitlist if needed
        """
        user_in_list = self.check_user(user)
        return_flag = False

        if book.id in user_in_list.borrowed_physical_books.values():
            for loan_id in user_in_list.borrowed_physical_books.keys():
                if loan_id in self.loans:
                    self.loans[loan_id].returned_at = datetime.now()
                    user_in_list.borrowed_physical_books.pop(loan_id)
                    book.borrowed -= 1
                    return_flag = True
                    logger.info(
                        f"User {user_in_list.name} \
                        returned the book: {book.title} to the library"
                    )
                    break

            if return_flag:
                if book.waitlist:
                    self.process_waitlist(book)
            else:
                raise MissingItemError(
                    f"User {user_in_list} \
                    has not returned any books to the library"
                )
        else:
            raise MissingItemError(
                f"User {user_in_list.name} \
                did not borrow a book like: {book}"
            )

    def return_all_items(self, user: User) -> None:
        """Return all books and ebooks borrowed by a user"""
        user_in_list = self.check_user(user)

        if (
            not user_in_list.borrowed_physical_books
            and not user_in_list.borrowed_ebooks
        ):
            raise MissingItemError(f"{user_in_list.name} \
                has not borrowed any items")

        borrowed_books = user_in_list.borrowed_physical_books.copy()

        for book_id in borrowed_books.values():
            book = self.find_book_by_id(book_id)
            self.return_book(user_in_list, book)

        user_in_list.borrowed_ebooks.clear()

    def get_all_books(self) -> list[Book | EBook]:
        """Return a list of all books and ebooks in the library"""
        return [book for book in self.catalog.values()]

    def get_all_users(self) -> list[User]:
        """Return a list of all registered users"""
        return [user for user in self.users_list.values()]

    def get_available_books(self) -> list[Book | EBook]:
        """Return a list of all currently available books for borrowing"""
        return [
            book for book in self.catalog.values()
            if isinstance(book, EBook) or book.is_book_available()
        ]

    def find_user_by_name(self, user_name: str) -> User | None:
        """Find user by name and return"""
        for user in self.users_list.values():
            if user.name == user_name:
                return user
        else:
            logger.info(f"There is no user {user_name} \
                matching the one you provided")
            return None

    def find_user_by_id(self, id: int) -> User | None:
        """Find user by id and return"""
        if id in self.users_list.keys():
            return self.users_list[id]
        else:
            logger.info(f"There is no user with ID {id} \
                            matching the one you provided")
            return None

    def find_book_by_title(self, book_name: str) -> list[Book | EBook] | None:
        """Find books by title and return a list of matching results"""
        result = []

        for val in self.catalog.values():
            if book_name.lower().strip() == val.title.lower().strip():
                result.append(val)

        if any(result):
            logger.info(f"Books matching: {result}")
        else:
            logger.info(f"There is no book matching the name: \
                {book_name}")

        return result

    def find_books_by_genre(self, genre: str) -> list[Book | EBook]:
        """Find and return all books matching a given genre"""
        result = []

        for val in self.catalog.values():
            if (genre.lower().strip()
                    in [i.lower().strip() for i in val.genre]):
                result.append(val)

        if any(result):
            logger.info(f"Books matching genre {genre.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the genre: \
                {genre.strip()}")

        return result

    def find_books_by_author(self, author: str) -> list[Book | EBook]:
        """Find and return all books written by a specific author"""
        result = []

        for val in self.catalog.values():
            if author.lower().strip() == val.author.lower().strip():
                result.append(val)

        if any(result):
            logger.info(f"Books matching author {author.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the author: \
                {author.strip()}")

        return result

    def find_book_by_id(self, id: str) -> Item | None:
        """Find and return book by id"""
        if id in self.catalog.keys():
            return self.catalog[id]
        else:
            logger.info(f"There is no item \
                matching the id {id}")
            return None

    def add_to_waitlist(self, user: User, book: Book) -> None:
        """
            Add a user to the waitlist for a book if it is
            unavailable or borrowing limit is exceeded
        """
        if (
            not book.is_book_available()
            or len(user.borrowed_physical_books) >= user.LIMIT_OF_BOOKS
        ):
            if self.check_waitlist(user, book):
                book.waitlist.add(user.id)
                logger.info(f"User {user} added to waitlist.")

    @staticmethod
    def check_waitlist(user: User, book: Book) -> bool:
        """Check whether a user is already in the waitlist for a book"""
        if any(u == user.id for u in book.waitlist):
            logger.info(f"User {user} already exists in the waitlist")
            return False
        return True

    def process_waitlist(self, book: Book) -> None:
        """
            Process the waitlist and assign the book to the next eligible user
        """
        for user_id in book.waitlist:
            next_user = self.users_list[user_id]
            borrowed_books = len(next_user.borrowed_physical_books.keys())

            if (
                borrowed_books < User.LIMIT_OF_BOOKS
            ):
                book.waitlist.remove(user_id)

                loan_id = self.create_loan(next_user, book, Loan.MAX_DAYS)

                book.borrowed += 1
                next_user.borrowed_physical_books[loan_id] = book.id

                logger.info(f"User: {next_user.name} \
                    borrow book: {book.title}")
                return
