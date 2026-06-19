CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    year INTEGER NOT NULL,
    amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ebooks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    year INTEGER NOT NULL,
    file_size INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS borrowings (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    book_id TEXT,
    type TEXT NOT NULL CHECK(type IN ('book', 'ebook')),
    borrowed_at TEXT NOT NULL,
    due_to TEXT,
    returned_at TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);

CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    book_id TEXT,
    position TEXT,

    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);
