# Legal Contract Tracker

A specialized internal tool for the Legal Department to manage, track, and monitor legal contracts and documents.

## Features

- Upload contracts and legal documents with metadata
- Automatically track expiration dates with email reminders
- Search and filter contracts by various criteria
- Dashboard overview showing contract statistics
- Secure user authentication system

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL (In-memory database for development)
- **Authentication**: JWT-based login
- **Email notifications**: APScheduler for automated reminders

## Project Structure

```
/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── auth/          # Authentication logic
│   │   ├── core/          # Core configurations
│   │   ├── db/            # Database models and connections
│   │   ├── models/        # Data models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic services
│   │   └── main.py        # Application entry point
│   └── pyproject.toml     # Python dependencies
│
└── frontend/              # React frontend
    ├── public/            # Static assets
    ├── src/
    │   ├── components/    # Reusable UI components
    │   ├── lib/           # Utility functions and API client
    │   ├── pages/         # Page components
    │   ├── types/         # TypeScript type definitions
    │   └── App.tsx        # Main application component
    └── package.json       # JavaScript dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (for production)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Run the development server:
   ```
   poetry run uvicorn app.main:app --reload
   ```

4. The API will be available at http://localhost:8000
   - API documentation: http://localhost:8000/docs

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the following content:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Run the development server:
   ```
   npm run dev
   ```

5. The frontend will be available at http://localhost:5173

## Default Admin Account

- Email: admin@legalcontracttracker.com
- Password: admin

## Deployment

### Backend Deployment

The backend can be deployed to Fly.io:

```
cd backend
fly launch
```

### Frontend Deployment

Build the frontend for production:

```
cd frontend
npm run build
```

The built files will be in the `dist` directory, which can be deployed to any static hosting service.

## Future Enhancements

- Digital signatures
- Automated contract renewals
- Document versioning
- Advanced analytics
- Integration with other legal tools
