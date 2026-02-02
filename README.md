# Real-Time Chat Api (Backend)

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

This project is intended for learning and development purposes. 
It is a work in progress and is being developed while I am learning backend development.

Right now implemented secure login, registration and access control.
Real-time chat functionality is in progress.

## Getting Started with Docker
### Clone the repository
- git clone <https://github.com/MinKhantt/real_time_chat_app.git>
- cd real_time_chat_app
- create .env file and run - cp .env.example .env
- then run - docker-compose up -d
- and you can test in http://localhost:8000/docs#/

