# Library Management System
![CI Pipeline](https://github.com/pijor189/LibraryManagementSystem/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/pijor189/LibraryManagementSystem/graph/badge.svg?token=9ef1c7fa-c6f8-403a-b0cc-d568e7e48f1c)](https://codecov.io/gh/pijor189/LibraryManagementSystem)

A Python-based Library Management System for managing books, users, loans, and library operations.

The application provides a command-line interface (CLI) that allows users to register, log in, browse the library 
catalog, borrow and return books, extend loans, and manage their accounts. All application data is stored persistently 
in an SQLite database.

This project was developed as a learning project focused on:

Python application architecture
- Object-oriented programming (OOP)
- SQLite database design and integration
- Automated testing with pytest
- Code quality and static analysis
- Continuous Integration with GitHub Actions

Features
- User registration and authentication
- Book and eBook management
- Borrowing and returning library items
- Loan extension
- Book availability tracking
- Library inventory management
- Persistent data storage with SQLite
- Interactive command-line interface (CLI)
- Comprehensive automated test suite
- Continuous Integration using GitHub Actions

Planned improvements include:
- REST API implementation
- Web application (e.g. FastAPI + frontend)
- User roles (librarian / reader)
- Reservation system improvements
- Docker support

---

## Technologies

- **Language**: Python 3.13
- **Database**: SQLite
- **Testing**: pytest, pytest-cov
- **Code Quality**: Ruff, mypy
- **CI/CD**: GitHub Actions

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pijor189/LibraryManagementSystem.git
cd LibraryManagementSystem
```

---

# Testing

Run the full test suite:

```bash
pytest
```