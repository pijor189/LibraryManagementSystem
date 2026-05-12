from library.book import EBook
from library.library_service import Library
from library.user import User
from utils.data_loader import DataLoader
from library.loan import Loan

def init_library():
    lib = Library()
    users = DataLoader.load_users("data/users.json")
    books, ebooks = DataLoader.load_books("data/books.json")
    for book in books:
        lib.add_book(book)
    for ebook in ebooks:
        lib.add_book(ebook)
    for user in users:
        lib.register_user(user)

    return lib

def show(data):
    for d in data:
        print(d)

def menu(lib: Library, user: User, option: int) -> bool:
    if option == 1:
        show(lib.get_all_books())
    elif option == 2:
        show(lib.get_available_books())
    elif option == 3:
        show(["1. Find book by a name", "2. Find book by a genre", "3. Find book by an author"])
        number = int(input("Select: "))
        if not isinstance(number, int):
            raise TypeError("Not valid number")
        if number == 1:
            name = input("Name of search book: ")
            show(lib.find_book_by_name(name))
        elif number == 2:
            genre = input("Genre of search book: ")
            show(lib.find_books_by_genre(genre))
        elif number == 3:
            author = input("Author of search book: ")
            show(lib.find_books_by_author(author))
        else:
            print("Wrong option")
    elif option == 4:
        user_name = input("Name a user what you want to find: ")
        result = lib.find_user(user_name)
        print(result)
    elif option == 5:
        book_name = input("Name a book what you want to borrow: ")
        book = lib.find_book_by_name(book_name)
        book = lib.choose_book(book)
        days = Loan.MAX_DAYS
        if not isinstance(book, EBook):
            days = int(input("How many days would you like to borrow this book for? (Maximum: 30 days): "))
        lib.borrow(user, book, days)
    elif option == 6:
        if user.borrowed_physical_books:
            for b in user.borrowed_physical_books:
                print(b.book.title, "\n", b.loan, sep="")
            book_name = input("Choose a book you want to extend: ")
            book = lib.find_book_by_name(book_name)
            for loan in lib.loans:
                if user.id == loan.user.id and loan.book in book[0].copies:
                    days = int(input("How many days would you like to extend this book for?"
                                       " (Maximum: 30 days): "))
                    loan.extend(days)
        else:
            print("You dont have any books that you can extend")
    elif option == 7:
        if user.borrowed_physical_books:
            for b in user.borrowed_physical_books:
                print(b.book.title, "\n", b.loan, sep="")
            book_name = input("Name a book what you want to return: ")
            book = lib.find_book_by_name(book_name)
            lib.return_book(user, book[0])
        else:
            print("You dont have any books that you can return")
    elif option == 8:
        return False
    else:
        print("Wrong option")
    return True
