# Real-Time Chat App (Backend)

This project is a backend service for a real-time chat application.  
It supports user authentication, conversations, messaging, and real-time communication using WebSockets.

The backend is built with an async-first approach for better performance and scalability.

## Tech Stack

- **FastAPI** – High-performance async Python web framework
- **WebSockets** – Real-time messaging
- **SQLAlchemy (Async)** – Async ORM for database access
- **Alembic** – Database migrations
- **PostgreSQL** – Primary relational database
- **AsyncPG** – Async PostgreSQL driver
- **Redis** – Caching and real-time support
- **JWT (python-jose)** – Authentication & authorization
- **Passlib / Argon2** – Secure password hashing
- **Pydantic** – Data validation and settings management
- **Docker & Docker Compose** – Containerization
- **Pytest** – Async testing setup

## Project Structure

The project follows a clean, modular architecture:
- `api` – Versioned API routes
- `models` – SQLAlchemy models
- `schemas` – Pydantic schemas
- `services` – Business logic
- `core` – Config, security, Redis
- `db` – Async database setup
- `alembic` – Database migrations
- `tests` – Automated tests

## Status

This project is under active development and built mainly for learning, practice and backend portfolio use.
