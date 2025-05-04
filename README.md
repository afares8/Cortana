# Legal Contract Tracker

A specialized internal tool for the Legal Department of the Zona Libre de Colón perfumery business to manage, track, and monitor legal contracts and documents with AI-powered analysis.

## Features

### Core Features
- Upload contracts and legal documents with metadata
- Automatically track expiration dates with email reminders
- Search and filter contracts by various criteria
- Dashboard overview showing contract statistics
- Secure user authentication system

### AI-Powered Features
- Contract risk analysis using Mistral 7B LLM
- Automatic clause extraction and categorization
- Risk scoring for contract terms and conditions
- Natural language querying of contract database
- AI-assisted task generation based on contract content

### Modular Architecture
- Legal Department module with client and contract management
- Workflow and task management system
- Audit and compliance tracking
- Designed for future integration with Accounting, HR, and Procurement

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript and Tailwind CSS
- **Database**: PostgreSQL (In-memory database for development)
- **Authentication**: JWT-based login
- **Email notifications**: APScheduler for automated reminders
- **AI Integration**: Mistral 7B model via Text Generation Inference
- **Docker**: Multi-environment container setup with GPU support

## Project Structure

```
/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── ai/                   # AI service integration
│   │   ├── auth/                 # Authentication logic
│   │   ├── core/                 # Core configurations
│   │   ├── db/                   # Database models and connections
│   │   ├── legal/                # Legal department module
│   │   │   ├── models.py         # Legal-specific data models
│   │   │   ├── routers.py        # Legal-specific API endpoints
│   │   │   ├── schemas.py        # Legal-specific Pydantic schemas
│   │   │   └── services.py       # Legal-specific business logic
│   │   ├── models/               # Shared data models
│   │   ├── routers/              # API endpoints
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic services
│   │   │   └── ai/               # AI services
│   │   │       ├── contract_intelligence.py  # Contract analysis
│   │   │       └── mistral_client.py         # Mistral API client
│   │   └── main.py               # Application entry point
│   ├── Dockerfile                # Backend container definition
│   └── pyproject.toml            # Python dependencies
│
├── frontend/                     # React frontend
│   ├── public/                   # Static assets
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   └── ai/               # AI-specific components
│   │   ├── lib/                  # Utility functions and API client
│   │   ├── modules/              # Module-specific code
│   │   │   └── legal/            # Legal department module
│   │   │       ├── api/          # Legal API client
│   │   │       ├── pages/        # Legal-specific pages
│   │   │       └── types/        # Legal-specific types
│   │   ├── pages/                # Page components
│   │   ├── types/                # TypeScript type definitions
│   │   └── App.tsx               # Main application component
│   └── package.json              # JavaScript dependencies
│
├── docker-compose.yml            # Docker Compose configuration
└── AI_SETUP.md                   # AI setup documentation
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (for production)
- Docker and Docker Compose (for containerized setup)
- NVIDIA GPU with CUDA support (optional, for AI features)

### Local Development Setup

#### Backend Setup

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

#### Frontend Setup

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

### Docker Setup

The application can be run in Docker with different profiles for GPU and CPU environments:

#### For GPU Environments (with NVIDIA GPU)

```bash
# Set the COMPOSE_PROFILES environment variable to 'gpu'
export COMPOSE_PROFILES=gpu

# Start services with GPU support
docker compose down
docker compose up --build -d
```

#### For CPU-only Environments

```bash
# Set the COMPOSE_PROFILES environment variable to 'cpu'
export COMPOSE_PROFILES=cpu

# Start services in CPU-only mode
docker compose up --build -d
```

If you don't specify a profile, the system will default to CPU mode with fallback AI responses.

## Default Admin Account

- Email: admin@legalcontracttracker.com
- Password: admin

## API Endpoints

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Contract Management Endpoints

- `GET /api/v1/contracts` - List all contracts
- `POST /api/v1/contracts` - Create a new contract
- `GET /api/v1/contracts/{contract_id}` - Get contract details
- `PUT /api/v1/contracts/{contract_id}` - Update contract
- `DELETE /api/v1/contracts/{contract_id}` - Delete contract

### Legal Module Endpoints

- `GET /api/v1/legal/clients` - List all clients
- `POST /api/v1/legal/clients` - Create a new client
- `GET /api/v1/legal/workflows` - List all workflows
- `GET /api/v1/legal/tasks` - List all tasks

### AI Endpoints

- `POST /api/v1/ai/mistral/generate` - Generate text with Mistral 7B model
  ```json
  {
    "inputs": "Analyze the following contract clause: ...",
    "max_new_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9
  }
  ```
- `GET /api/v1/test-mistral` - Test Mistral model connection and environment
- `POST /api/v1/ai/analyze-contract` - Analyze contract for risks and clauses
- `POST /api/v1/ai/extract-clauses` - Extract clauses from contract text

## Deployment

### Backend Deployment

The backend can be deployed to Fly.io or Render:

```
cd backend
fly launch
```

Or using the provided `render.yaml` configuration for Render.com.

### Frontend Deployment

Build the frontend for production:

```
cd frontend
npm run build
```

The built files will be in the `dist` directory, which can be deployed to any static hosting service.

## Environment Configuration

The application supports different environments through environment variables:

### Backend Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration (default: 30)
- `MISTRAL_API_URL` - URL for Mistral API service (default: http://ai-service:80)
- `AI_FALLBACK_MODE` - Force fallback mode for AI features (auto-detected by default)

### Frontend Environment Variables

- `VITE_API_URL` - Backend API URL
- `VITE_ENABLE_AI_FEATURES` - Enable/disable AI features in UI

## AI Integration

The system integrates with the Mistral 7B language model for contract analysis:

- **Hardware Requirements**: NVIDIA GPU with CUDA support (recommended)
- **Fallback Mode**: Automatically uses fallback responses in CPU-only environments
- **Docker Integration**: Uses Docker Compose profiles to select appropriate services
- **Environment Detection**: Automatically detects GPU availability

For detailed AI setup instructions, see [AI_SETUP.md](./AI_SETUP.md).

## Module Architecture

The application follows a modular architecture designed for future expansion:

### Legal Department Module

- **Client Registry**: Manage client information and relationships
- **Contract Management**: Handle contracts with versioning and history
- **Workflow System**: Define and track approval workflows
- **Task Management**: Assign and track legal tasks
- **Audit Logging**: Track all changes for compliance

### AI Module

- **Contract Intelligence**: Extract and analyze contract clauses
- **Risk Assessment**: Score contracts based on risk factors
- **Natural Language Interface**: Query contracts using natural language
- **Task Suggestions**: Generate tasks based on contract content

## Recent Updates

- Enhanced AI integration with Mistral 7B model
- Added Docker support for both GPU and CPU environments
- Implemented modular architecture for future department integration
- Created comprehensive legal department module
- Fixed fallback detection logic between frontend and backend
- Updated AIDashboard to use dedicated Mistral endpoint for consistent behavior

## Future Enhancements

- Digital signatures integration
- Automated contract renewals
- Advanced document versioning with diff visualization
- Enhanced analytics dashboard
- Integration with other departments (Accounting, HR, Procurement)
- Mobile application for on-the-go access
- Expanded AI capabilities with fine-tuned models
