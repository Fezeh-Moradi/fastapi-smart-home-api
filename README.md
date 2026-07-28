# Smart Home API

A RESTful backend API for a Smart Home system built with **FastAPI** and **MongoDB**.

This project is a learning-oriented backend application focused on practicing modern Python backend development, asynchronous programming, authentication, database integration, testing, and CI/CD with GitHub Actions.

---

## Features

* User registration
* User login
* JWT authentication
* Password hashing with bcrypt
* Protected API endpoints
* Current authenticated user endpoint
* User management
* User search and filtering
* User pagination and sorting
* Phone number validation
* Device management
* Device creation, listing, updating, and deletion
* Device filtering and sorting
* Ownership-based access control
* Protected device operations
* MongoDB integration using Motor Async Driver
* Custom HTTP exception handling
* Custom validation exception handling
* Application logging
* Request/response middleware logging
* Automatic API documentation with Swagger UI
* Unit tests
* Integration tests
* MongoDB service for CI integration tests
* Automated test execution with GitHub Actions

---

## Technologies

* Python 3.14
* FastAPI
* MongoDB
* Motor
* PyMongo
* Pydantic
* JWT
* python-jose
* Passlib
* bcrypt
* Uvicorn
* Pytest
* pytest-asyncio
* pytest-cov
* GitHub Actions

---

## Project Structure

```text
smart_home_api/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── core/
│   ├── deps.py
│   ├── logger.py
│   ├── middleware.py
│   └── security.py
│
├── database/
│   ├── mongodb.py
│   └── mongodb_test_config.py
│
├── handlers/
│   └── exceptions.py
│
├── routers/
│   ├── auth.py
│   ├── devices.py
│   └── users.py
│
├── schemas/
│   ├── device.py
│   └── user.py
│
├── services/
│   ├── __init__.py
│   ├── device_service.py
│   └── user_service.py
│
├── tests/
│   ├── integration/
│   │   ├── conftest.py
│   │   ├── test_auth_integration.py
│   │   ├── test_devices_integration.py
│   │   └── test_users_integration.py
│   │
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_database.py
│   ├── test_devices.py
│   ├── test_exceptions.py
│   └── test_users.py
│
├── config.py
├── main.py
├── pytest.ini
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Architecture

The project follows a layered structure:

```text
Client
   │
   ▼
FastAPI Routers
   │
   ▼
Services
   │
   ▼
MongoDB / Motor
```

Supporting components include:

* `core/` for authentication dependencies, security, logging, and middleware
* `handlers/` for custom exception handling
* `schemas/` for Pydantic request and response models
* `tests/` for unit and integration testing
* `.github/workflows/` for continuous integration

---

## Authentication

The API uses JWT-based authentication.

### Authentication Flow

```text
Register
   │
   ▼
Password Hashing
   │
   ▼
MongoDB
   │
   ▼
Login
   │
   ▼
JWT Access Token
   │
   ▼
Protected Endpoints
```

Passwords are hashed using **bcrypt** before being stored in the database.

Protected endpoints require a valid Bearer token.

---

## API Endpoints

### Authentication

| Method | Endpoint         | Description                          |
| ------ | ---------------- | ------------------------------------ |
| POST   | `/auth/register` | Register a new user                  |
| POST   | `/auth/login`    | Login and receive a JWT access token |
| GET    | `/auth/me`       | Get the currently authenticated user |

---

### Users

| Method | Endpoint           | Description         |
| ------ | ------------------ | ------------------- |
| GET    | `/users/`          | Get users           |
| GET    | `/users/{user_id}` | Get a specific user |
| POST   | `/users/`          | Create a new user   |
| PUT    | `/users/{user_id}` | Update a user       |
| DELETE | `/users/{user_id}` | Delete a user       |

The users endpoint supports features such as:

* Filtering by name
* Filtering by phone
* Pagination
* Sorting by name
* Sorting by phone
* Ascending and descending sorting
* ObjectId validation
* Phone number validation

---

### Devices

| Method | Endpoint               | Description           |
| ------ | ---------------------- | --------------------- |
| POST   | `/devices/`            | Create a new device   |
| GET    | `/devices/`            | Get devices           |
| GET    | `/devices/{device_id}` | Get a specific device |
| PUT    | `/devices/{device_id}` | Update a device       |
| DELETE | `/devices/{device_id}` | Delete a device       |

Device operations include:

* Device creation
* Device listing
* Device filtering by status
* Device sorting
* Device updates
* Device deletion
* Device ownership validation
* Protected access to user-owned devices

---

## Security

The project implements several security mechanisms:

* JWT authentication
* Password hashing with bcrypt
* Bearer token authentication
* Protected endpoints
* User authentication dependencies
* Ownership-based authorization
* Input validation with Pydantic
* Phone number validation
* MongoDB ObjectId validation

Users can only access or modify resources they are authorized to access.

---

## Testing

The project uses **Pytest** for automated testing.

Testing is divided into two main categories.

### Unit Tests

Unit tests cover:

* Authentication
* User services
* Device services
* Database configuration
* Exception handlers
* Security and authentication dependencies

### Integration Tests

Integration tests verify the application against a real MongoDB service.

Integration tests cover:

* Authentication flows
* User operations
* Device operations
* MongoDB interactions

### Running Tests

Install the test dependencies and run:

```bash
python -m pytest -v -s
```

To run tests with coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

The test suite currently contains **86 tests**.

---

## Test Coverage

The project has achieved approximately **98% overall test coverage**.

Example local coverage result:

```text
TOTAL    1461    27    98%
```

The coverage includes:

* Authentication
* User management
* Device management
* Services
* Database configuration
* Exception handlers
* Middleware
* Security dependencies
* Integration tests

---

## Continuous Integration

The project uses **GitHub Actions** to automatically run the test suite.

The CI workflow:

1. Checks out the repository
2. Sets up Python 3.14
3. Starts a MongoDB 7 service
4. Installs project dependencies
5. Configures test environment variables
6. Runs the complete Pytest suite

The workflow is triggered on:

* Pushes to `main`
* Pull requests targeting `main`

This ensures that changes are automatically tested before being merged.

---

## Environment Variables

The application uses environment variables for configuration.

Example:

```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=smart_home
TEST_DATABASE_NAME=smart_home_test
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For local development, create a `.env` file in the project root.

> Never commit real secrets or `.env` files to the repository.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Fezeh-Moradi/fastapi-smart-home-api.git
```

### 2. Enter the Project Directory

```bash
cd fastapi-smart-home-api
```

### 3. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Linux/macOS:

```bash
python3 -m venv venv
```

### 4. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Make sure MongoDB is running and the required environment variables are configured.

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

## Development Status

The project currently includes:

* FastAPI REST API
* MongoDB integration
* JWT authentication
* User management
* Device management
* Authorization and ownership checks
* Service layer
* Custom exception handling
* Logging and middleware
* Unit tests
* Integration tests
* Automated CI testing with GitHub Actions

---

## Future Improvements

Potential future improvements include:

* Refresh token support
* Role-Based Access Control (RBAC)
* Admin/User roles
* Docker and Docker Compose support
* Production deployment
* API rate limiting
* Improved API versioning
* Advanced device management
* Background tasks
* More comprehensive API documentation
* Test coverage reporting in CI

---

## License

This project is licensed under the terms described in the `LICENSE` file.
