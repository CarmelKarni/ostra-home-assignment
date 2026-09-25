# User Management REST API

A simple REST API server for managing users with create, read, update, and delete operations.

## API Documentation

Full OpenAPI specification available in `openapi.yaml`. You can view it with tools like:
- [Swagger UI](https://editor.swagger.io/) - Paste the openapi.yaml content
- [Redoc](https://redoc.ly/redoc/) - Paste the openapi.yaml content
- Local tools: `pip install flask-restx` for auto-generated docs

## Decisions

### Framework: Flask
- **Why**: Lightweight, easy to set up, minimal boilerplate for REST APIs
- **Alternative considered**: FastAPI (more modern, async support) but overkill for this simple project

### Database: SQLite with SQLAlchemy ORM
- **Why**: No external dependencies, perfect for prototyping, easy schema management
- **Alternative considered**: In-memory dict (simpler but no persistence), PostgreSQL (overkill for now)

### ID Generation: UUID
- **Why**: Guarantees uniqueness without a database sequence, collision-free
- **Alternative considered**: Sequential IDs (simpler but requires coordination)

### Port: 5000
- **Why**: Flask default, easy to change if needed

### Response Format: JSON
- **Why**: Industry standard for REST APIs, native Python support

## Assumptions

- Single-server deployment (no distributed system concerns)
- Synchronous request/response model (no async required for current scale)
- No authentication/authorization system required (all users can see/message each other)
- Message immutability except for read status (no edit/update of message content)
- Receiver-only deletion model (only receiver can delete received messages, only sender can delete sent messages via fetched list)
- No message persistence beyond current session (SQLite in-process, can be replaced)
- Messages are plaintext (no rich text, HTML, or formatting)
- Message length limit: 1000 characters maximum
- Message deletion is permanent (no soft delete or trash bin)

## API Endpoints

### Create User
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Get All Users
```bash
curl http://localhost:5000/users
```

### Get User by ID
```bash
curl http://localhost:5000/users/{id}
```

### Update User
```bash
curl -X PUT http://localhost:5000/users/{id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com"}'
```

### Delete User
```bash
curl -X DELETE http://localhost:5000/users/{id}
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Architecture

### Layered Architecture
The application follows a clean layered architecture:

1. **API Layer** (`app.py`) - Flask routes handling HTTP requests/responses
2. **Handler Layer** (`handlers/user_handler.py`) - Business logic and validation
3. **Repository Layer** (`repositories/`) - Data persistence abstraction
4. **Database Layer** (SQLAlchemy) - Actual database implementation

Each layer only depends on the layer below it, making the system loosely coupled and easy to test/modify.

### Repository Pattern
- **`UserRepository` (base)** - Abstract interface defining all user operations
- **`SQLAlchemyUserRepository`** - SQLAlchemy implementation

This design allows switching database implementations without changing the API or handler layers.

## Messaging System

The API includes a complete messaging system with:
- Send messages between users
- Fetch received messages with ID-based pagination
- Fetch unread messages
- Fetch sent messages
- Update message read status
- Delete individual messages
- Batch delete messages

### Message Endpoints
```bash
# Send message
curl -X POST http://localhost:5000/users/{userId}/messages/send \
  -H "Content-Type: application/json" \
  -d '{"receiverId": "user-123", "message": "Hello!"}'

# Fetch received messages
curl "http://localhost:5000/users/{userId}/messages/fetch?startIndex=0&endIndex=-1"

# Fetch unread messages
curl http://localhost:5000/users/{userId}/messages/unread

# Update read status
curl -X PATCH "http://localhost:5000/users/{userId}/messages/{messageId}/read-status?isRead=true"

# Delete message
curl -X DELETE http://localhost:5000/users/{userId}/messages/{messageId}

# Batch delete messages
curl -X DELETE http://localhost:5000/users/{userId}/messages/delete-batch \
  -H "Content-Type: application/json" \
  -d '{"messageIds": [1, 2, 3]}'
```

### Message Design Decisions

#### Integer Auto-increment Message IDs
- **Why**: Simpler than UUIDs, predictable ordering, efficient indexing
- **Alternative considered**: UUID (more complex, less efficient for range queries)

#### ID-based Pagination (not offset/limit)
- **Why**: More stable when deletions occur between requests, natural ordering with ID ranges
- **How**: `startIndex` (inclusive) and `endIndex` (exclusive) define message ID ranges
- **Optional parameters**: Both are optional
- **Special case**: Negative `endIndex` means no upper limit (fetch all from startIndex)

#### Message Length Limit
- **Why**: 1000 characters balances reasonable message length with storage efficiency
- **Validation**: Enforced at handler layer

#### Read Status Tracking
- **Design**: Boolean `is_read` field on messages, only receiver can update
- **Authorization**: Repository checks receiver ownership before allowing updates

#### Ownership Model
- **Send**: Any user can send to any user
- **Receive**: Only receiver can fetch/delete/update their own received messages
- **Authorization**: Enforced at repository layer

## Project Structure

```
.
├── README.md                                # This file
├── requirements.txt
├── openapi.yaml                             # OpenAPI 3.0 specification
├── app.py                                   # Flask application and routes
├── models.py                                # SQLAlchemy models and db initialization
├── users.db                                 # SQLite database (auto-created)
├── handlers/
│   ├── __init__.py
│   ├── user_handler.py                      # User business logic and validation
│   └── message_handler.py                   # Message business logic and validation
├── repositories/
│   ├── __init__.py
│   ├── base.py                              # Abstract repository interfaces
│   └── sqlalchemy_impl.py                   # SQLAlchemy implementations
└── tests/
    ├── test_message_handler.py              # 12 send_message tests
    ├── test_message_handler_fetch.py        # 30 fetch tests (fetch, unread, sent)
    ├── test_message_handler_delete.py       # 18 delete tests (single, batch)
    ├── test_sqlalchemy_delete_batch.py      # 11 delete_batch repository tests
    ├── test_sqlalchemy_get_by_receiver.py   # 13 get_by_receiver repository tests
    ├── test_sqlalchemy_update_read_status.py # 10 update_read_status repository tests
    └── test_e2e_messaging.py                # 4 end-to-end workflow tests

Total: 88 unit and E2E tests, all passing
```

### Test Coverage

**Unit Tests (84 tests)**:
- Handler layer: Send, fetch (all types), delete operations with validation
- Repository layer: SQLAlchemy-specific implementations, error handling, authorization checks

**E2E Tests (4 tests)**:
- Complete messaging workflow: create users → send messages → fetch → update status → delete
- Pagination with multiple messages
- Sent messages tracking across multiple recipients
- Authorization enforcement across users

All tests use in-memory SQLite database and mock isolation where appropriate.

### Future possible expansions:

- Add authentication/authorization (JWT, OAuth)
- Add message search/filtering (by content, date)
- Encrypt messages for privacy
- Add ability to fetch sent messages

