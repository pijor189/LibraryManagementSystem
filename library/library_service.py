from .config import logger
from .book import Book, EBook, BookCopy
from .user import User
from .loan import Loan
from .exceptions import *
from utils.uid import generate_uid
from datetime import datetime

class Library:
    def __init__(self):
        self.catalog = []
        self.books_id = set()
        self.users_list = []
        self.users_id = set()
        self.loans = []

    def __str__(self):
        return f"List of books: {self.catalog}\nUsers: {self.users_list}"

    def add_book(self, book: Book):
        try:
            # Check if the book exists
            if isinstance(book, EBook):
                self.catalog.append(book)
                book.id = generate_uid(self.books_id)
                logger.info(f"EBook: {book.title} was added to the library")
            elif isinstance(book, Book):
                self.catalog.append(book)
                for _ in range(book.amount):
                    book_copy = BookCopy(book)
                    book_copy.id = generate_uid(self.books_id)
                    book.copies.append(book_copy)
                logger.info(f"Book: {book.title} was added to the library")
            else:
                raise NoBook(f"There is no book {book} matching the one you provided")
        except NoBook as e:
            logger.error(e)
            raise

    def add_existing_book(self, book: Book, amount):
        try:
            book_in_list = next((b for b in self.catalog if b.book_id == book.book_id), None)
            if not book_in_list:
                raise NoBook(f"There is no book {book_in_list} matching the one you provided")
            if amount < 1:
                raise InvalidNumberOfBooks(f"Invalid number of books to add")
            for _ in range(amount):
                book_copy = BookCopy(book_in_list)
                book_copy.id = generate_uid(self.books_id)
                book_in_list.copies.append(book_copy)
            book_in_list.amount += amount
        except (NoBook, InvalidNumberOfBooks) as e:
            logger.error(e)
            raise

    def remove_existing_book(self, book: Book, all_copies: bool, amount: int = 0):
        # TODO przemyśleć takie tematy jak:
        # co jeśli nie wszystkie książki do usunięcia są dostępne (wypozyczone)
        #   - czy usuwać te co są dostępne resztę pozostawić i jakoś flagą oznaczyć, że jak zwrocą to usunać
        #   - czy zwrócic wyjatek, ze nie da sie usunac bo nie wszystkie sa dostepne
        # w przypadku jesli chcemy usunac tylko kilka, to nalezaloby podac konkretne id ktorych,
        # bo moze chodzi o egzemplarz ktory sie uszkodzil, wiec nie moze to byc randomowy (ID)
        # TODO
        try:
            book_in_list = next((b for b in self.catalog if b.book_id == book.book_id), None)
            if not book_in_list:
                raise NoBook(f"There is no book {book_in_list} matching the one you provided")
            if all_copies:
                pass
        except NoBook as e:
            logger.error(e)
            raise

    def register_user(self, user: User):
        try:
            # Check if the user exists
            if isinstance(user, User):
                self.users_list.append(user)
                user.id = generate_uid(self.users_id)
                logger.info(f"User: {user.name} was registered in library")
            else:
                raise NoUser(f"There is no user {user} matching the one you provided")
        except NoUser as e:
            logger.error(e)
            raise

    def unregister_user(self, user: User):
        # TODO dodac mozliwosc usuniecia uzytkownika, jednak najpierw trzeba sprawdzic
        # czy nie ma jakiś wypozyczonych ksiazek aktualnie
        pass

    @staticmethod
    def choose_book(results):
        """ Allow the user to choose the book type when multiple matching books are found """
        if not results:
            raise NoBook(f"There is no book to choose from")

        if len(results) == 1:
            return results[0]

        logger.info("Found multiple versions:")
        for i, book in enumerate(results, start=1):
            book_type = "EBook" if isinstance(book, EBook) else "Book"
            print(f"{i}. {book.title} [{book_type}]")

        choice = int(input("Choose version: ")) - 1
        return results[choice]

    def borrow(self, user: User, book: Book | list[Book], days: int = Loan.MAX_DAYS):
        try:
            # Check if the user exists
            user_in_list = next((u for u in self.users_list if u.id == user.id), None)
            if not user_in_list:
                raise NoUser(f"There is no user {user.name} matching the one you provided")
            # Check if the book exists
            book_in_list = next((b for b in self.catalog if b.book_id == book.book_id), None)
            if not book_in_list:
                raise NoBook(f"There is no book {book_in_list} matching the one you provided")
            if isinstance(book, EBook):
                self.borrow_ebook(user, book)
            elif isinstance(book, Book):
                self.borrow_book(user, book, days)
            else:
                raise
        except (NoUser, NoBook) as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Another problem: {e}")
            raise

    def borrow_ebook(self, user: User, ebook: EBook):
        user.borrowed_ebooks.append(ebook)
        loan = Loan(user, ebook)
        self.loans.append(loan)
        logger.info(f"User: {user.name} borrow ebook: {ebook.title}")

    def borrow_book(self, user: User, book: Book, days: int):
        # Check if the book is available, otherwise, add the user to the waitlist
        if not book.available_copy():
            logger.info(f"Book '{book.title}' is not available")
            self.add_to_waitlist(user, book)
            return
        # Check if anyone is in the queue
        if book.waitlist:
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

    def return_book(self, user: User, book: Book):
        try:
            # Check if the user exists
            user_in_list = next((u for u in self.users_list if u.id == user.id), None)
            if user_in_list:
                # Check whether the user has borrowed this book
                for b in user_in_list.borrowed_physical_books:
                    if b in book.copies:
                        user_in_list.borrowed_physical_books.remove(b)
                        for l in self.loans:
                            if l.book == b.book and l.user == user_in_list:
                                l.returned_at = datetime.now()
                        b.is_available = True
                        b.loan = None
                        logger.info(f"User {user_in_list.name} returned the book: {b.book.title} to the library")
                        # Check if there is any user waiting for this book
                        if book.waitlist:
                            self.process_waitlist(book)
                        break
                else:
                    raise NoBook(f"User {user_in_list.name} did not borrow a book like: {book}")
            else:
                raise NoUser(f"There is no user '{user_in_list}' in our library")
        except (NoUser, NoBook) as e:
            logger.error(e)
            raise

    def get_all_books(self):
        """ List all books in the library """
        return self.catalog

    def get_all_users(self):
        """ List all users in the library """
        return self.users_list

    def get_available_books(self):
        """ List all books in the library that are currently available for borrowing """
        return [b for b in self.catalog if b.available_copy()]

    def find_user(self, user_name: str):
        for user in self.users_list:
            if user.name == user_name:
                return user
        else:
            logger.info(f"There is no user {user_name} matching the one you provided")
            return None

    def find_book_by_name(self, book_name: str):
        """ Check if such a book exists in the library, if yes, display it """
        result = []
        for book in self.catalog:
            if book_name.lower().strip() == book.title.lower().strip():
                logger.info(f"{book} Available: {"True" if book.available_copy() else "False"}")
                result.append(book)
        if not result:
            logger.info(f"There is no book {book_name} matching the one you provided")
            return None
        else:
            return result

    def find_books_by_genre(self, genre: str):
        """ Check whether books by this genre exist and display them """
        result = []
        for book in self.catalog:
            if genre.lower().strip() in [b.lower().strip() for b in book.genre]:
                result.append(book)
        if result:
            logger.info(f"Books matching genre {genre.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the genre: {genre.strip()}")
        return result

    def find_books_by_author(self, author: str):
        """ Check whether books by this author exist and display them """
        result = []
        for book in self.catalog:
            if author.lower().strip() == book.author.lower().strip():
                result.append(book)
        if result:
            logger.info(f"Books matching author {author.strip()}:\n{result}")
        else:
            logger.info(f"There is no book matching the author: {author.strip()}")
        return result

    def add_to_waitlist(self, user: User, book: Book):
        """ If the book is borrowed, add the user to the list. Otherwise, check if a user who exceeded the borrowing
            limit tried to borrow it, and add them to the list """
        if not book.available_copy() or len(user.borrowed_physical_books) > 2:
            if self.check_waitlist(user, book):
                book.waitlist.append(user)
                user.waitlist.append(book)
                logger.info(f"User {user} added to waitlist.")

    @staticmethod
    def check_waitlist(user: User, book: Book) -> bool:
        """ Check if the user already exists in the waitlist """
        if any(u.id == user.id for u in book.waitlist):
            logger.info(f"User {user} already exists in the waitlist")
            return False
        return True

    def process_waitlist(self, book: Book):
        """ Handle the queue and see if any user is eligible to borrow the book """
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
