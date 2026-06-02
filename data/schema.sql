CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    year INTEGER NOT NULL,
    amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS book_copies (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY(book_id) REFERENCES books(id)
);

CREATE TABLE IF NOT EXISTS ebooks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    year INTEGER NOT NULL,
    file_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS borrowings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    book_id INTEGER,
    type TEXT NOT NULL CHECK(type IN ('physical', 'ebook')),
    borrowed_at TEXT NOT NULL,
    due_to TEXT NOT NULL,
    returned_at TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);

CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    created_at TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);
