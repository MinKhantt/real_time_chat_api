# Real-Time Chat API (Backend)

Backend service for a real-time chat application. It provides authentication, 1-to-1 and group conversations, message history, and real-time messaging over WebSockets. The system is async-first for performance and scalability.

## What’s Implemented
- User registration, login, and access control (JWT)
- 1-to-1 conversations
- Group conversations with member roles (`owner`, `admin`, `member`)
- Group member management (add/remove/update role)
- Message history
- WebSocket real-time messaging
- Redis Pub/Sub for multi-instance broadcast

## Tech Stack
- **FastAPI** - Async Python web framework
- **WebSockets** - Real-time messaging
- **SQLAlchemy (Async)** - ORM for DB access
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **AsyncPG** - Async PostgreSQL driver
- **Redis** - Caching + Pub/Sub
- **JWT (python-jose)** - Auth
- **Passlib / Argon2** - Password hashing
- **Pydantic** - Data validation
- **Docker & Docker Compose** - Containerization
- **Pytest** - Testing

## Project Structure
- `app/api` - Versioned API routes
- `app/api/v1/chat_one_to_one.py` - 1-to-1 + shared conversation endpoints
- `app/api/v1/chat_group.py` - Group management endpoints
- `app/api/v1/chat_ws.py` - WebSocket endpoint
- `app/api/v1/chat.py` - Chat router aggregator
- `app/models` - SQLAlchemy models
- `app/schemas` - Pydantic schemas
- `app/services` - Business logic
- `app/core` - Config, security, Redis, WebSockets
- `app/db` - Async database setup
- `alembic` - Migrations
- `tests` - Automated tests

## Chat APIs

### Conversation APIs
- `GET /api/v1/chat/conversations`
- `POST /api/v1/chat/conversations`
  Body: `{"recipient_id": "<UUID>"}`
- `GET /api/v1/chat/conversations/{conversation_id}/messages?skip=0&limit=50`

### Group APIs
- `POST /api/v1/chat/groups`
- `GET /api/v1/chat/groups/{conversation_id}`
- `PATCH /api/v1/chat/groups/{conversation_id}`
- `GET /api/v1/chat/groups/{conversation_id}/members`
- `POST /api/v1/chat/groups/{conversation_id}/members`
- `DELETE /api/v1/chat/groups/{conversation_id}/members/{user_id}`
- `PATCH /api/v1/chat/groups/{conversation_id}/members/{user_id}/role`

### WebSocket
- Connect:
  `WS /api/v1/chat/ws/conversations/{conversation_id}`
- Header:
  `Authorization: Bearer <access_token>`
- Send (client -> server):
  `{"type":"message.send","content":"hello"}`
- Receive (server -> client):
  `{"type":"message.new","message":{...}}`

Notes:
- WebSocket auth uses `Authorization: Bearer <token>` (works for non-browser WS clients).
- Redis Pub/Sub is used to broadcast messages across multiple app instances.

## Getting Started (Docker)
1. Clone the repository:
   - `git clone https://github.com/MinKhantt/real_time_chat_api.git`
   - `cd real_time_chat_api`
2. Create `.env`:
   - `cp .env.example .env`
3. Run:
   - `docker-compose up -d --build`
4. Open API docs:
   - `http://localhost:8000/docs#/`

## Status
This project is intended for learning and development.

Implemented now:
- Auth and access control
- 1-to-1 chat
- Group chat core APIs
- WebSocket + Redis broadcast

Planned next:
- Tests for new group flows
- API docs examples for each group endpoint
