# Real-Time Chat API (Backend)

Backend service for a real-time chat application. It provides authentication, 1-to-1 conversations, message history, and real-time messaging over WebSockets. The system is async-first for performance and scalability.

## What’s Implemented
- User registration, login, and access control (JWT)
- 1-to-1 conversations
- Message history
- WebSocket real-time messaging
- Redis Pub/Sub for multi-instance broadcast

## Tech Stack
- **FastAPI** – Async Python web framework
- **WebSockets** – Real-time messaging
- **SQLAlchemy (Async)** – ORM for DB access
- **Alembic** – Database migrations
- **PostgreSQL** – Primary database
- **AsyncPG** – Async PostgreSQL driver
- **Redis** – Caching + Pub/Sub
- **JWT (python-jose)** – Auth
- **Passlib / Argon2** – Password hashing
- **Pydantic** – Data validation
- **Docker & Docker Compose** – Containerization
- **Pytest** – Testing

## Project Structure
- `app/api` – Versioned API routes
- `app/models` – SQLAlchemy models
- `app/schemas` – Pydantic schemas
- `app/services` – Business logic
- `app/core` – Config, security, Redis, WebSockets
- `app/db` – Async database setup
- `alembic` – Migrations
- `tests` – Automated tests

## Real-Time Chat

### REST
- Create or get a 1-to-1 conversation
  - `POST /api/v1/chat/conversations`
  - Body: `{"recipient_id": "<UUID>"}`

- Fetch message history
  - `GET /api/v1/chat/conversations/{conversation_id}/messages?skip=0&limit=50`

### WebSocket
- Connect
  - `WS /api/v1/chat/ws/conversations/{conversation_id}`
  - Header: `Authorization: Bearer <access_token>`

- Send (client -> server)
  - `{"type":"message.send","content":"hello"}`

- Receive (server -> client)
  - `{"type":"message.new","message":{...}}`

Notes:
- WebSocket auth uses `Authorization: Bearer <token>` (works for non-browser WS clients).
- Redis Pub/Sub is used to broadcast messages across multiple app instances.

## Getting Started (Docker)
1. Clone the repository:
   - `git clone https://github.com/MinKhantt/real_time_chat_app.git`
   - `cd real_time_chat_app`

2. Create `.env`:
   - `cp .env.example .env`

3. Run:
   - `docker-compose up -d`

4. Open API docs:
   - `http://localhost:8000/docs#/`

## Status
This project is intended for learning and development. Group chat is not implemented yet.
