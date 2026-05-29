from .config import logger
from .book import Book, EBook, BookCopy
from .user import User
from .loan import Loan
from exceptions.book_exceptions import MissingBookError
from exceptions.user_exceptions import MissingUserError
from exceptions.library_exceptions import (
    InvalidNumberOfBooksError, UserHasBorrowedItemsError
)
from utils.uid import generate_uid
from datetime import datetime


class Library:
    def __init__(self):
        self.catalog = []
        self.books_id = set()
        self.book_copy_id = set()
        self.users_list = []
        self.users_id = set()
        self.loans = []

    def __str__(self):
        return f"List of books: {self.catalog}\nUsers: {self.users_list}"

    def add_book(self, book: Book) -> None:
        """
            Add a new book or ebook to the library catalog
            and assign unique IDs to it and its copies
        """
        if isinstance(book, EBook):
            self.catalog.append(book)
            book.id = generate_uid(self.books_id)
            logger.info(f"EBook: {book.title} was added to the library")
        elif isinstance(book, Book):
            self.catalog.append(book)
            book.id = generate_uid(self.books_id)
            for _ in range(book.amount):
                book_copy = BookCopy(book)
                book_copy.id = generate_uid(self.book_copy_id)
                book.copies.append(book_copy)
            logger.info(f"Book: {book.title} was added to the library")
        else:
            raise MissingBookError(f"There is no book {book} \
                matching the one you provided")

    def add_existing_book(self, book: Book, amount) -> None:
        """Add additional copies of an existing book in the library catalog"""
        book_in_list = self.check_book(book)
        if amount < 1:
            raise InvalidNumberOfBooksError("Invalid number of books to add")
        for _ in range(amount):
            book_copy = BookCopy(book_in_list)
            book_copy.id = generate_uid(self.book_copy_id)
            book_in_list.copies.append(book_copy)
        book_in_list.amount += amount

    def remove_book_copy(self, book: BookCopy) -> None:
        """Remove a single book copy from the library if it is available"""
        if book.id not in self.book_copy_id:
            raise MissingBookError("There is no book like that \
                in the library")
        if not book.is_available:
            raise MissingBookError("The book is not available \
                and cannot be removed")
        self.book_copy_id.remove(book.id)

    def remove_book(self, book: Book) -> None:
        """
            Remove a book from the catalog along with all its copies
            if it is a physical book. For ebooks,
            also remove related loans.
        """
        if book.id not in self.books_id:
            raise MissingBookError("There is no book like that \
                in the library")
        if isinstance(book, EBook):
            for loan in self.loans:
                if book == loan.book:
                    loan.user.borrowed_ebooks.remove(book)
            self.books_id.remove(book.id)
            self.catalog.remove(book)
        elif isinstance(book, Book):
            # first check if all copies are available
            for b in book.copies:
                if not b.is_available:
                    raise MissingBookError("The book is not available \
                        and cannot be removed")
            # if all copies are available, remove them and the original item
            for b in book.copies:
                self.remove_book_copy(b)
            self.books_id.remove(book.id)
            self.catalog.remove(book)

    def check_user(self, user: User) -> User:
        """
            Validate that a user exists in the library
            and return the user object
        """
        user_in_list = next(
            (u for u in self.users_list if u.id == user.id),
            None
        )

        if not user_in_list:
            raise MissingUserError(f"There is no user {user.name} \
                matching the one you provided")

        return user_in_list

    def check_book(self, book: Book) -> Book | EBook:
        """Validate that a book exists in the library catalog and return it"""
        book_in_list = next(
            (b for b in self.catalog if b.id == book.id), None
        )

        if not book_in_list:
            raise MissingBookError(
                "There is no book matching the one you provided"
            )

        return book_in_list

    def register_user(self, user: User) -> None:
        """Register a new user in the library and assign a unique ID"""
        if isinstance(user, User):
            self.users_list.append(user)
            user.id = generate_uid(self.users_id)
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
        self.users_list.remove(user_in_list)

    @staticmethod
    def choose_book(results: list[Book | EBook]) -> Book | EBook:
        """
            Allow the user to choose a book when multiple matches are found.
            Raises NoBook if no books are available.
        """
        if not results:
            raise MissingBookError("There is no book to choose from")

        if len(results) == 1:
            return results[0]

        logger.info("Found multiple versions:")

        for i, book in enumerate(results, start=1):
            book_type = "EBook" if isinstance(book, EBook) else "Book"
            print(f"{i}. {book.title} [{book_type}]")

        choice = int(input("Choose version: ")) - 1

        return results[choice]

    def borrow(
        self, user: User, book: Book | list[Book], days: int = Loan.MAX_DAYS
    ) -> None:
        """Borrow a book or ebook for a given user"""

        user_in_list = self.check_user(user)
        book_in_list = self.check_book(book)

        if isinstance(book_in_list, EBook):
            self.borrow_ebook(user_in_list, book_in_list)
        elif isinstance(book_in_list, Book):
            self.borrow_book(user_in_list, book_in_list, days)

    def borrow_ebook(self, user: User, ebook: EBook) -> None:
        """Assign an ebook to a user and create a loan record"""
        user.borrowed_ebooks.append(ebook)
        loan = Loan(user, ebook)
        self.loans.append(loan)
        logger.info(f"User: {user.name} borrow ebook: {ebook.title}")

    def borrow_book(self, user: User, book: Book, days: int) -> None:
        """
            Borrow a physical book if available,
            otherwise add the user to the waitlist
        """
        if any(book.waitlist) or not book.available_copy():
            logger.info(f"Book '{book.title}' is not available,\
                {user} added to waitlist")
            self.add_to_waitlist(user, book)
            if book.available_copy():
                self.process_waitlist(book)
            return

        if len(user.borrowed_physical_books) < 3:
            book_copy = book.available_copy()
            user.borrowed_physical_books.append(book_copy)
            book_copy.is_available = False
            loan = Loan(user, book_copy, days)
            self.loans.append(loan)
            book_copy.loan = loan
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

        for b in user_in_list.borrowed_physical_books:
            if b in book.copies:
                user_in_list.borrowed_physical_books.remove(b)
                for loan in self.loans:
                    if loan.book == b and loan.user == user_in_list:
                        loan.returned_at = datetime.now()
                        break
                b.is_available = True
                b.loan = None
                logger.info(
                    f"User {user_in_list.name} \
                        returned the book: {b.book.title} to the library"
                )

                if book.waitlist:
                    self.process_waitlist(book)
                break
        else:
            raise MissingBookError(
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
            raise MissingBookError(f"{user_in_list.name} \
                has not borrowed any items")

        for book in user_in_list.borrowed_physical_books:
            self.return_book(user_in_list, book.book)

        user_in_list.borrowed_ebooks.clear()

    def get_all_books(self) -> list[Book | EBook]:
        """Return a list of all books and ebooks in the library"""
        return self.catalog

    def get_all_users(self) -> list[User]:
        """Return a list of all registered users"""
        return self.users_list

    def get_available_books(self) -> list[Book | EBook]:
        """Return a list of all currently available books for borrowing"""
        return [b for b in self.catalog if b.available_copy()]

    def find_user(self, user_name: str) -> User | None:
        for user in self.users_list:
            if user.name == user_name:
                return user
        else:
            logger.info(f"There is no user {user_name} \
                matching the one you provided")
            return None

    def find_book_by_name(self, book_name: str) -> list[Book | EBook] | None:
        """Find books by title and return a list of matching results"""
        result = []

        for book in self.catalog:
            if book_name.lower().strip() == book.title.lower().strip():
                logger.info(
                    f"{book} Available: \
                        {'True' if book.available_copy() else 'False'}"
                )
                result.append(book)

        if not result:
            logger.info(f"There is no book {book_name} \
                matching the one you provided")

        return result

    def find_books_by_genre(self, genre: str) -> list[Book | EBook]:
        """Find and return all books matching a given genre"""
        result = []

        for book in self.catalog:
            if (genre.lower().strip()
                    in [b.lower().strip() for b in book.genre]):
                result.append(book)

        if any(result):
            logger.info(f"Books matching genre {genre.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the genre: \
                {genre.strip()}")

        return result

    def find_books_by_author(self, author: str) -> list[Book | EBook]:
        """Find and return all books written by a specific author"""
        result = []

        for book in self.catalog:
            if author.lower().strip() == book.author.lower().strip():
                result.append(book)

        if any(result):
            logger.info(f"Books matching author {author.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the author: \
                {author.strip()}")

        return result

    def add_to_waitlist(self, user: User, book: Book) -> None:
        """
            Add a user to the waitlist for a book if it is
            unavailable or borrowing limit is exceeded
        """
        if not book.available_copy() or len(user.borrowed_physical_books) > 2:
            if self.check_waitlist(user, book):
                book.waitlist.append(user)
                user.waitlist.append(book)
                logger.info(f"User {user} added to waitlist.")

    @staticmethod
    def check_waitlist(user: User, book: Book) -> bool:
        """Check whether a user is already in the waitlist for a book"""
        if any(u.id == user.id for u in book.waitlist):
            logger.info(f"User {user} already exists in the waitlist")
            return False
        return True

    def process_waitlist(self, book: Book) -> None:
        """
            Process the waitlist and assign the book to the next eligible user
        """
        for i, u in enumerate(book.waitlist):
            if len(u.borrowed_physical_books) < 3:
                next_user = book.waitlist.pop(i)
                next_user.waitlist.remove(book)
                book_copy = book.available_copy()
                next_user.borrowed_physical_books.append(book_copy)
                loan = Loan(next_user, book_copy)
                self.loans.append(loan)
                book_copy.loan = loan
                book_copy.is_available = False
                logger.info(f"User: {next_user.name} \
                    borrow book: {book.title}")
                return
