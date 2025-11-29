# Tests

This directory contains all test files for the FastAPI application.

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user

# Run with coverage
pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_auth.py` - Authentication endpoint tests
- `test_users.py` - User CRUD endpoint tests

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test, ensuring test isolation.

