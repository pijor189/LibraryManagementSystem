from library.library_service import Library
from utils.data_loader import DataLoader

library = Library()
users = DataLoader.load_users("data/users.json")
books, ebooks = DataLoader.load_books("data/books.json")

for book in books:
    library.add_book(book)
for ebook in ebooks:
    library.add_book(ebook)
for user in users:
    library.register_user(user)
