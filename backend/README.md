# Legal Contract Tracker - Backend

This is the backend API for the Legal Contract Tracker application, built with FastAPI and featuring AI-powered contract analysis using the Mistral 7B language model.

## Features

- JWT-based authentication
- Contract management and storage
- Automated email notifications for contract expiration
- RESTful API for contract operations
- In-memory database for development (can be switched to PostgreSQL)
- AI-powered contract analysis with Mistral 7B
- Spanish language preprocessing for legal documents
- Contextual AI generation with Retrieval-Augmented Generation (RAG)
- Compliance automation with document embeddings
- Microservice-based architecture for scalability

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Contracts

- `GET /api/v1/contracts` - List all contracts (with filtering)
- `POST /api/v1/contracts` - Create a new contract
- `GET /api/v1/contracts/{id}` - Get contract details
- `PUT /api/v1/contracts/{id}` - Update a contract
- `DELETE /api/v1/contracts/{id}` - Delete a contract
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### AI Endpoints

- `POST /api/v1/ai/mistral/generate` - Generate text with Mistral 7B model
  ```json
  {
    "inputs": "Analyze the following contract clause: ...",
    "max_new_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9,
    "debug": false
  }
  ```
- `POST /api/v1/ai/contextual-generate` - Generate context-aware responses
  ```json
  {
    "query": "What contracts are expiring this month?",
    "context_retrieval": true,
    "max_new_tokens": 500,
    "temperature": 0.7
  }
  ```
- `GET /api/v1/test-mistral` - Test Mistral model connection and environment
- `POST /api/v1/ai/analyze-contract` - Analyze contract for risks and clauses
- `POST /api/v1/ai/extract-clauses` - Extract clauses from contract text

### Legal Module Endpoints

- `GET /api/v1/legal/clients` - List all clients
- `POST /api/v1/legal/clients` - Create a new client
- `GET /api/v1/legal/workflows` - List all workflows
- `GET /api/v1/legal/tasks` - List all tasks

### Compliance Endpoints

- `POST /api/v1/compliance/manual/upload` - Upload compliance manual for embedding
- `POST /api/v1/compliance/uaf-reports` - Generate UAF report
- `GET /api/v1/compliance/dashboard` - Get compliance dashboard data
- `POST /api/v1/compliance/pep-screening` - Screen client against PEP lists
- `POST /api/v1/compliance/sanctions-screening` - Screen entity against sanctions lists

## Setup Instructions

### Prerequisites

- Python 3.12+
- Poetry (Python package manager)
- Docker and Docker Compose (for containerized setup)
- NVIDIA GPU with CUDA support (optional, for AI features)

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
MISTRAL_API_URL=http://ai-service:80  # URL for Mistral API service
AI_FALLBACK_MODE=false  # Force GPU mode (set to true for CPU-only environments)
AI_LANGUAGE_MODE=es  # Force Spanish language processing (optional)
```

## Database

The application uses an in-memory database by default for development. To switch to PostgreSQL:

1. Update the database connection in `app/core/config.py`
2. Install PostgreSQL dependencies:
   ```
   poetry add psycopg[binary]
   ```

## AI Integration

The backend integrates with the Mistral 7B language model for contract analysis and compliance automation:

### Testing AI Integration

Use the provided test script to validate the Mistral AI integration:

```bash
python -m app.scripts.test_mistral_integration
```

This script tests three endpoints:
- `/api/v1/test-mistral` - Tests the health of the Mistral service
- `/api/v1/ai/mistral/generate` - Tests text generation
- `/api/v1/ai/contextual-generate` - Tests contextual generation

For testing in environments without GPU:

```bash
python -m app.scripts.test_mistral_integration --mock
```

### Troubleshooting AI Integration

If the Mistral AI integration is unexpectedly falling back to CPU mode:

1. Check if `AI_FALLBACK_MODE` is explicitly set in your environment
2. Verify GPU detection is working correctly with `nvidia-smi`
3. Examine the logs for connection errors to the AI service
4. Use the test endpoint to diagnose issues: `curl http://localhost:8000/api/v1/test-mistral`

## Email Notifications

Email notifications are handled by the APScheduler background task. To enable:

1. Set `EMAIL_ENABLED=True` in your `.env` file
2. Configure SMTP settings in `app/core/config.py`

## Testing

Run tests with pytest:

```
poetry run pytest
```

### CI Configuration

The project includes GitHub Actions CI configuration for automated testing:

- Runs on Python 3.12
- Installs dependencies via Poetry
- Creates required directories and environment files
- Runs Mistral integration tests in mock mode
- Performs smoke tests for backend service health

## Deployment

The backend can be deployed to Fly.io:

```
fly launch
```

For Docker deployment with GPU support:

```bash
export COMPOSE_PROFILES=gpu
docker-compose up --build -d
```

For CPU-only environments:

```bash
export COMPOSE_PROFILES=cpu
docker-compose up --build -d
```

## Default Admin Account

- Email: admin@legalcontracttracker.com
- Password: admin

## Recent Updates

- **May 2025**:
  - Fixed Mistral AI integration unexpectedly falling back to CPU mode
  - Improved health-check logic to better handle DNS resolution errors
  - Enhanced error handling in Spanish language pipeline
  - Added comprehensive test script for validating Mistral AI endpoints
  - Implemented CI configuration with GitHub Actions for automated testing
  - Added detailed logging for connection attempts and failures
  - Made fallback mode logic more selective to only trigger on persistent server errors
