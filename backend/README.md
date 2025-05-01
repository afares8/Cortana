# Legal Contract Tracker - Backend

This is the backend API for the Legal Contract Tracker application, built with FastAPI.

## Features

- JWT-based authentication
- Contract management and storage
- Automated email notifications for contract expiration
- RESTful API for contract operations
- In-memory database for development (can be switched to PostgreSQL)

## API Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Contracts

- `GET /api/contracts` - List all contracts (with filtering)
- `POST /api/contracts` - Create a new contract
- `GET /api/contracts/{id}` - Get contract details
- `PUT /api/contracts/{id}` - Update a contract
- `DELETE /api/contracts/{id}` - Delete a contract
- `GET /api/dashboard/stats` - Get dashboard statistics

## Setup Instructions

### Prerequisites

- Python 3.12+
- Poetry (Python package manager)

### Installation

1. Install dependencies:
   ```
   poetry install
   ```

2. Activate the virtual environment:
   ```
   poetry shell
   ```

3. Run the development server:
   ```
   uvicorn app.main:app --reload
   ```

4. The API will be available at http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EMAIL_ENABLED=False  # Set to True to enable email notifications
```

## Database

The application uses an in-memory database by default for development. To switch to PostgreSQL:

1. Update the database connection in `app/core/config.py`
2. Install PostgreSQL dependencies:
   ```
   poetry add psycopg[binary]
   ```

## Email Notifications

Email notifications are handled by the APScheduler background task. To enable:

1. Set `EMAIL_ENABLED=True` in your `.env` file
2. Configure SMTP settings in `app/core/config.py`

## Testing

Run tests with pytest:

```
poetry run pytest
```

## Deployment

The backend can be deployed to Fly.io:

```
fly launch
```

## Default Admin Account

- Email: admin@legalcontracttracker.com
- Password: admin
