from .config import logger
from .book import Book, EBook, BookCopy
from .user import User
from .loan import Loan
from .exceptions import (
    NoBook,
    NoUser,
    InvalidNumberOfBooks,
    UserWithItemsCannotBeUnregistered,
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
        # Check if the book exists
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
            raise NoBook(f"There is no book {book} matching the one you provided")

    def add_existing_book(self, book: Book, amount) -> None:
        book_in_list = self.check_book(book)
        if amount < 1:
            raise InvalidNumberOfBooks("Invalid number of books to add")
        for _ in range(amount):
            book_copy = BookCopy(book_in_list)
            book_copy.id = generate_uid(self.book_copy_id)
            book_in_list.copies.append(book_copy)
        book_in_list.amount += amount

    def remove_book_copy(self, book: BookCopy) -> None:
        """Remove the book copy from the library"""
        if book.id not in self.book_copy_id:
            raise NoBook("There is no book like that in the library")
        if not book.is_available:
            raise NoBook("The book is not available and cannot be removed")
        self.book_copy_id.remove(book.id)

    def remove_book(self, book: Book) -> None:
        """Remove the original item and all copies if it is a physical version"""
        if book.id not in self.books_id:
            raise NoBook("There is no book like that in the library")
        if isinstance(book, EBook):
            for l in self.loans:
                if book == l.book:
                    l.user.borrowed_ebooks.remove(book)
            self.books_id.remove(book.id)
            self.catalog.remove(book)
        elif isinstance(book, Book):
            # first check if all copies are available
            for b in book.copies:
                if not b.is_available:
                    raise NoBook("The book is not available and cannot be removed")
            # if all copies are available, remove them and the original item
            for b in book.copies:
                self.remove_book_copy(b)
            self.books_id.remove(book.id)
            self.catalog.remove(book)

    def check_user(self, user: User) -> User:
        user_in_list = next((u for u in self.users_list if u.id == user.id), None)
        if not user_in_list:
            raise NoUser(f"There is no user {user.name} matching the one you provided")
        return user_in_list

    def check_book(self, book: Book) -> Book | EBook:
        book_in_list = next(
            (b for b in self.catalog if b.id == book.id), None
        )
        if not book_in_list:
            raise NoBook(
                f"There is no book {book_in_list} matching the one you provided"
            )
        return book_in_list

    def register_user(self, user: User) -> None:
        # Check if the user exists
        if isinstance(user, User):
            self.users_list.append(user)
            user.id = generate_uid(self.users_id)
            logger.info(f"User: {user.name} was registered in library")
        else:
            raise NoUser(f"There is no user {user} matching the one you provided")

    def unregister_user(self, user: User) -> None:
        """Unregister a user from the library"""
        user_in_list = self.check_user(user)

        if any(
            [
                user_in_list.borrowed_physical_books,
                user_in_list.borrowed_ebooks,
            ]
        ):
            raise UserWithItemsCannotBeUnregistered(
                f"{user_in_list.name} has borrowed books"
            )

        self.users_id.remove(user_in_list.id)
        self.users_list.remove(user_in_list)

    @staticmethod
    def choose_book(results: list[Book | EBook]) -> Book | EBook:
        """Allow the user to choose the book type when multiple matching books are found"""
        if not results:
            raise NoBook("There is no book to choose from")

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
        # Check if the user exists
        user_in_list = self.check_user(user)
        # Check if the book exists
        book_in_list = self.check_book(book)

        if isinstance(book_in_list, EBook):
            self.borrow_ebook(user_in_list, book_in_list)
        elif isinstance(book_in_list, Book):
            self.borrow_book(user_in_list, book_in_list, days)

    def borrow_ebook(self, user: User, ebook: EBook) -> None:
        user.borrowed_ebooks.append(ebook)
        loan = Loan(user, ebook)
        self.loans.append(loan)
        logger.info(f"User: {user.name} borrow ebook: {ebook.title}")

    def borrow_book(self, user: User, book: Book, days: int) -> None:
        # Check if the book is available, otherwise, add the user to the waitlist
        if not book.available_copy():
            logger.info(f"Book '{book.title}' is not available")
            self.add_to_waitlist(user, book)
            return
        # Check if anyone is in the queue
        if any(book.waitlist):
            self.add_to_waitlist(user, book)
            self.process_waitlist(book)
            return
        # Check if the user has exceeded the borrowing limit
        if len(user.borrowed_physical_books) < 3:
            book_copy = book.available_copy()
            user.borrowed_physical_books.append(book_copy)
            book_copy.is_available = False
            loan = Loan(user, book_copy, days)
            self.loans.append(loan)
            book_copy.loan = loan
            logger.info(f"User: {user.name} borrow book: {book.title}")
        else:
            # User exceeded the borrowing limit, add them to the waitlist.
            logger.warning(f"User {user.name} can borrow maximum 3 books")
            self.add_to_waitlist(user, book)

    def return_book(self, user: User, book: Book) -> None:
        # Check if the user exists
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
                    f"User {user_in_list.name} returned the book: {b.book.title} to the library"
                )
                # Check if there is any user waiting for this book
                if book.waitlist:
                    self.process_waitlist(book)
                break
        else:
            raise NoBook(
                f"User {user_in_list.name} did not borrow a book like: {book}"
            )

    def return_all_items(self, user: User) -> None:
        """Return all items borrowed from the library"""
        user_in_list = self.check_user(user)

        if (
            not user_in_list.borrowed_physical_books
            and not user_in_list.borrowed_ebooks
        ):
            raise NoBook(f"{user_in_list.name} has not borrowed any items")

        for book in user_in_list.borrowed_physical_books:
            self.return_book(user_in_list, book.book)

        user_in_list.borrowed_ebooks.clear()

    def get_all_books(self) -> list[Book | EBook]:
        """List all books in the library"""
        return self.catalog

    def get_all_users(self) -> list[User]:
        """List all users in the library"""
        return self.users_list

    def get_available_books(self) -> list[Book | EBook]:
        """List all books in the library that are currently available for borrowing"""
        return [b for b in self.catalog if b.available_copy()]

    def find_user(self, user_name: str) -> User | None:
        for user in self.users_list:
            if user.name == user_name:
                return user
        else:
            logger.info(f"There is no user {user_name} matching the one you provided")
            return None

    def find_book_by_name(self, book_name: str) -> list[Book | EBook] | None:
        """Check if such a book exists in the library, if yes, display it"""
        result = []
        for book in self.catalog:
            if book_name.lower().strip() == book.title.lower().strip():
                logger.info(
                    f"{book} Available: {'True' if book.available_copy() else 'False'}"
                )
                result.append(book)
        if not result:
            logger.info(f"There is no book {book_name} matching the one you provided")
            return None
        else:
            return result

    def find_books_by_genre(self, genre: str) -> list[Book | EBook]:
        """Check whether books by this genre exist and display them"""
        result = []
        for book in self.catalog:
            if genre.lower().strip() in [b.lower().strip() for b in book.genre]:
                result.append(book)
        if any(result):
            logger.info(f"Books matching genre {genre.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the genre: {genre.strip()}")
        return result

    def find_books_by_author(self, author: str) -> list[Book | EBook]:
        """Check whether books by this author exist and display them"""
        result = []
        for book in self.catalog:
            if author.lower().strip() == book.author.lower().strip():
                result.append(book)
        if any(result):
            logger.info(f"Books matching author {author.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the author: {author.strip()}")
        return result

    def add_to_waitlist(self, user: User, book: Book) -> None:
        """If the book is borrowed, add the user to the list. Otherwise, check if a user who exceeded the borrowing
        limit tried to borrow it, and add them to the list"""
        if not book.available_copy() or len(user.borrowed_physical_books) > 2:
            if self.check_waitlist(user, book):
                book.waitlist.append(user)
                user.waitlist.append(book)
                logger.info(f"User {user} added to waitlist.")

    @staticmethod
    def check_waitlist(user: User, book: Book) -> bool:
        """Check if the user already exists in the waitlist"""
        if any(u.id == user.id for u in book.waitlist):
            logger.info(f"User {user} already exists in the waitlist")
            return False
        return True

    def process_waitlist(self, book: Book) -> None:
        """Handle the queue and see if any user is eligible to borrow the book"""
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
                logger.info(f"User: {next_user.name} borrow book: {book.title}")
                return
