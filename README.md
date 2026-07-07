# Smart Home API

A RESTful backend API for a Smart Home system built with **FastAPI** and **MongoDB**.

## Overview

This project is a learning-oriented backend application designed to practice modern Python web development using FastAPI. It includes user authentication, device management, and secure access to user-owned resources.

## Features

* User registration
* User login
* JWT Authentication
* Password hashing with bcrypt
* Protected API endpoints
* User profile endpoint
* Device management (Create, List, Delete)
* Ownership-based access control (users can only access their own devices)
* MongoDB integration using Motor (Async Driver)
* Automatic API documentation with Swagger UI

## Technologies

* Python 3
* FastAPI
* MongoDB
* Motor
* Pydantic
* JWT (python-jose)
* Passlib + bcrypt
* Uvicorn

## Project Structure

```text
smart_home_api/
│
├── core/
│   ├── deps.py
│   └── security.py
│
├── database/
│   └── mongodb.py
│
├── routers/
│   ├── auth.py
│   ├── users.py
│   └── devices.py
│
├── schemas/
│   ├── user.py
│   └── device.py
│
├── main.py
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint         | Description                    |
| ------ | ---------------- | ------------------------------ |
| POST   | `/auth/register` | Register a new user            |
| POST   | `/auth/login`    | Login and receive JWT token    |
| GET    | `/auth/me`       | Get current authenticated user |

### Devices

| Method | Endpoint               | Description                |
| ------ | ---------------------- | -------------------------- |
| POST   | `/devices/`            | Create a new device        |
| GET    | `/devices/`            | Get current user's devices |
| DELETE | `/devices/{device_id}` | Delete a device            |

## Security

* Passwords are hashed using bcrypt.
* JWT tokens are used for authentication.
* Protected endpoints require a valid Bearer Token.
* Users can only access their own devices.

## Running the Project

1. Clone the repository.

2. Create a virtual environment.

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start MongoDB.

5. Run the application:

```bash
uvicorn main:app --reload
```

6. Open the API documentation:

```
http://127.0.0.1:8000/docs
```

## Future Improvements

* Update device endpoint
* Refresh Tokens
* Role-Based Access Control (Admin/User)
* Logging
* Docker support
* Unit tests
* Deployment
