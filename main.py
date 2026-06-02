import logging
from library.user import User
from cli.interface import init_library, menu, clear_console, OPTIONS, initialize_database
from exceptions.user_exceptions import UserInitializationError
from exceptions.book_exceptions import MissingBookError
from utils.migrate_books import migrate_books, migrate_ebooks
from utils.migrate_users import migrate_users
from pathlib import Path
logging.disable(logging.CRITICAL)


if __name__ == "__main__":
    # tworzenie obiektu klasy Library - zaciagniecie danych z json
    lib = init_library()

    # tworzenie bazy danych
    db_file = Path("data/library.db")
    if db_file.exists():
        # usunięcie by stworzyć na nowo - testy
        db_file.unlink()

        # inicjalizacja bazy
        db = initialize_database()

        # migracja książek i użytkowników z plików json
        migrate_books()
        migrate_ebooks()
        migrate_users()

        # utworzenie użytkownika
        from repositories.user_repository import UserRepository
        user_repository = UserRepository(db)
        user_repository.add_user("Krzysztof Pijor")

        # zamknięcie bazy danych
        db.close()

    try:
        clear_console()
        user = User(input("Welcome! What's your name?\n"))
        lib.register_user(user)
    except UserInitializationError as e:
        print(e)
        exit()

    running = True

    while running:
        clear_console()
        try:
            print("------LIBRARY SYSTEM------")
            print(OPTIONS)
            number = int(input("Choose an option: "))
            clear_console()
            if not menu(lib, user, number):
                running = False
            else:
                input("\nPress ENTER to continue...")
        except (TypeError, MissingBookError, ValueError) as e:
            print(f"\033[31m{e}\033[0m")
            input("\nPress ENTER to continue...")
