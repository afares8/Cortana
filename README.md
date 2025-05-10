# Cortana

A specialized internal tool for a company in the Zona Libre de Colón perfumery business to manage, track, and monitor departments and documents with AI-powered analysis and compliance automation that has the company.

## Features

### Core Features
- Upload contracts and legal documents with metadata
- Automatically track expiration dates with email reminders
- Search and filter contracts by various criteria
- Dashboard overview showing contract statistics
- Secure user authentication system
- Comprehensive user management with role-based access control
- DMCE portal automation for invoice processing

### Artur Autonomous Governance
- **Self-Aware System Core**: Observes, analyzes, restructures, and evolves Cortana continuously
- **Observation Layer**: Monitors department creation, function usage, rule execution, and AI consumption
- **Reasoning Layer**: Generates high-confidence suggestions using Mistral 7B
- **Intervention Layer**: Takes action automatically or after admin approval
- **Simulation Core**: Runs risk-free evaluations of interventions
- **Dashboard**: Health map by department, suggestions feed, simulation view, and KPI graphs

### AI-Powered Features
- Contract risk analysis using Mistral 7B LLM
- Automatic clause extraction and categorization
- Risk scoring for contract terms and conditions
- Natural language querying of contract database
- AI-assisted task generation based on contract content
- Spanish language preprocessing for legal documents
- Contextual AI generation with Retrieval-Augmented Generation (RAG)

### Compliance Automation
- Compliance manual integration with document embeddings
- Multi-level due diligence automation (Basic, Enhanced, Simplified)
- Risk classification matrices for client, geographic, product, channel, and transactional risk
- Suspicious activity detection with automated red flag identification
- PEP and sanctions screening via OpenSanctions integration
- UAF (Unidad de Análisis Financiero) report generation
- Document retention policy enforcement
- Comprehensive compliance dashboard

### Modular Architecture
- Legal Department module with client and contract management
- User Management module with role-based access control
- Workflow and task management system
- Audit and compliance tracking
- DMCE automation module for invoice processing and declaration creation
- Diagnostics module (Artur) for system health monitoring and issue resolution
- Business Administration module with departments, roles, and functions management
- Designed for future integration with Accounting, HR, and Procurement
- Microservice-based design with clear service boundaries

### Departments

The Cortana platform supports the following departments:

- **Legal** - Contract management and legal document processing
- **Accounting** - Financial operations and tax obligations
- **Compliance** - Regulatory compliance and reporting
- **Traffic** - Logistics and shipping operations
- **HR** - Human resources management
- **Marketing** - Marketing campaigns and analytics
- **Sales** - Sales operations and client management
- **IT** - Technical infrastructure and support

Each department has dedicated roles, functions, and AI profiles configured to support its specific operational needs.

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript and Tailwind CSS
- **Database**: PostgreSQL (In-memory database for development)
- **Authentication**: JWT-based login
- **Email notifications**: APScheduler for automated reminders
- **AI Integration**: Mistral 7B model via Text Generation Inference
- **Vector Database**: FAISS for document embeddings
- **Embeddings**: Sentence Transformers with multilingual support
- **Docker**: Multi-environment container setup with GPU support

## Project Structure

```
/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── ai/                   # Legacy AI service integration
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
│   │   ├── services/             # Business logic services (microservices)
│   │   │   ├── ai/               # AI services
│   │   │   │   ├── api/          # AI API endpoints
│   │   │   │   ├── models/       # AI data models
│   │   │   │   ├── schemas/      # AI Pydantic schemas
│   │   │   │   ├── services/     # AI business logic
│   │   │   │   └── utils/        # AI utilities
│   │   │   │       ├── mistral_client.py     # Mistral API client
│   │   │   │       ├── spanish_input_pipeline.py  # Spanish preprocessing
│   │   │   │       ├── intent_classifier.py  # Query intent classification
│   │   │   │       ├── context_retriever.py  # Context retrieval for RAG
│   │   │   │       └── prompt_builder.py     # AI prompt construction
│   │   │   ├── audit/            # Audit services
│   │   │   ├── clients/          # Client management services
│   │   │   ├── compliance/       # Compliance automation services
│   │   │   │   ├── api/          # Compliance API endpoints
│   │   │   │   ├── models/       # Compliance data models
│   │   │   │   ├── schemas/      # Compliance Pydantic schemas
│   │   │   │   ├── services/     # Compliance business logic
│   │   │   │   └── utils/        # Compliance utilities
│   │   │   │       ├── document_embeddings.py  # Document embedding system
│   │   │   │       └── open_sanctions.py       # Sanctions screening client
│   │   │   ├── contracts/        # Contract management services
│   │   │   ├── tasks/            # Task management services
│   │   │   ├── users/            # User management services
│   │   │   │   ├── api/          # User management API endpoints
│   │   │   │   ├── models/       # User data models
│   │   │   │   ├── schemas/      # User Pydantic schemas
│   │   │   │   ├── services/     # User management business logic
│   │   │   │   └── utils/        # User management utilities
│   │   │   └── workflows/        # Workflow management services
│   │   └── main.py               # Application entry point
│   ├── Dockerfile                # Backend container definition
│   └── pyproject.toml            # Python dependencies
│
├── frontend/                     # React frontend
│   ├── public/                   # Static assets
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── ai/               # AI-specific components
│   │   │   │   ├── AIContractAnalysis.tsx  # Contract analysis component
│   │   │   │   └── AIContextualChat.tsx    # Contextual AI chat component
│   │   │   ├── compliance/       # Compliance components
│   │   │   │   ├── ComplianceDashboardWidget.tsx  # Dashboard widget
│   │   │   │   └── ComplianceManualUploader.tsx   # Manual uploader
│   │   │   └── ui/               # UI components
│   │   ├── lib/                  # Utility functions and API client
│   │   ├── modules/              # Module-specific code
│   │   │   ├── legal/            # Legal department module
│   │   │   │   ├── api/          # Legal API client
│   │   │   │   ├── pages/        # Legal-specific pages
│   │   │   │   └── types/        # Legal-specific types
│   │   │   └── users/            # User management module
│   │   │       ├── api/          # User management API client
│   │   │       ├── components/   # User-specific components
│   │   │       │   ├── PermissionMatrix.tsx  # Permission management component
│   │   │       │   ├── DateRangePicker.tsx   # Date range selection component
│   │   │       │   └── AuditLogView.tsx      # User audit log component
│   │   │       ├── pages/        # User management pages
│   │   │       │   ├── UserList.tsx          # User listing page
│   │   │       │   └── UserForm.tsx          # User creation/editing form
│   │   │       └── types/        # User-specific types
│   │   ├── pages/                # Page components
│   │   │   ├── ComplianceDashboard.tsx  # Compliance dashboard
│   │   │   ├── UAFReportForm.tsx        # UAF report generation
│   │   │   └── SanctionsScreeningForm.tsx  # Sanctions screening
│   │   ├── types/                # TypeScript type definitions
│   │   └── App.tsx               # Main application component
│   └── package.json              # JavaScript dependencies
│
├── docker-compose.yml            # Docker Compose configuration
├── AI_SETUP.md                   # AI setup documentation
├── ARCHITECTURE.md               # Architecture documentation
└── IMPLEMENTATION_PLAN.md        # Implementation plan
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (for production)
- Docker and Docker Compose (for containerized setup)
- NVIDIA GPU with CUDA support (optional, for AI features)
- At least 8GB RAM (16GB recommended for AI features)
- 20GB free disk space

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

### Compliance Module Setup

For the compliance automation features to work properly:

1. Upload a compliance manual PDF through the ComplianceManualUploader component
2. Configure OpenSanctions API key (if available) in the environment variables:
   ```
   OPENSANCTIONS_API_KEY=your_api_key
   ```
3. If no API key is provided, the system will use the public API with rate limiting

## Default Admin Account

- Email: admin@legalcontracttracker.com
- Password: admin

## API Endpoints

### Authentication Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### User Management Endpoints

- `GET /api/v1/users` - List all users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/{user_id}/reset-password` - Reset user password
- `PUT /api/v1/users/{user_id}/lock` - Lock user account
- `PUT /api/v1/users/{user_id}/unlock` - Unlock user account
- `GET /api/v1/roles` - List all roles
- `POST /api/v1/roles` - Create a new role
- `GET /api/v1/roles/{role_id}` - Get role details
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `GET /api/v1/permissions` - List all permissions
- `POST /api/v1/permissions` - Create a new permission
- `GET /api/v1/permissions/{permission_id}` - Get permission details
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission

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

### Business Administration Endpoints

- `POST /api/v1/admin/departments` - Create a new department
- `GET /api/v1/admin/departments` - List all departments
- `PUT /api/v1/admin/departments/{id}` - Update department
- `DELETE /api/v1/admin/departments/{id}` - Delete department
- `POST /api/v1/admin/roles` - Create a new role
- `POST /api/v1/admin/roles/assign` - Assign role to user in department
- `GET /api/v1/admin/roles/by-department/{id}` - Get roles for department
- `POST /api/v1/admin/functions` - Create a new function
- `GET /api/v1/admin/functions/by-department/{id}` - Get functions for department
- `POST /api/v1/automation/rules` - Create a new automation rule
- `GET /api/v1/automation/rules/by-department/{id}` - Get automation rules for department
- `POST /api/v1/admin/departments/from-template` - Create department from template
- `POST /api/v1/users/{user_id}/assign-to-department` - Assign user to department
- `GET /api/v1/admin/audit/logs` - Get audit logs

### Compliance Endpoints

- `POST /api/v1/compliance/manual/upload` - Upload compliance manual for embedding
- `POST /api/v1/compliance/uaf-reports` - Generate UAF report
  ```json
  {
    "client_id": 123,
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-03-31T23:59:59"
  }
  ```

### Artur Endpoints

- `GET /api/v1/artur/observation/insights` - List system insights
- `GET /api/v1/artur/evaluation/suggestions` - List improvement suggestions
- `POST /api/v1/artur/intervention/execute` - Execute an approved suggestion
- `POST /api/v1/artur/simulation/run` - Run a simulation for a suggestion
- `GET /api/v1/artur/dashboard/department-health` - Get department health metrics
- `GET /api/v1/compliance/dashboard` - Get compliance dashboard data
- `POST /api/v1/compliance/pep-screening` - Screen client against PEP lists
  ```json
  {
    "client_id": 123,
    "name": "John Doe",
    "country": "PA",
    "birth_date": "1980-01-01"
  }
  ```
- `POST /api/v1/compliance/sanctions-screening` - Screen entity against sanctions lists
  ```json
  {
    "entity_id": 123,
    "name": "Acme Corp",
    "entity_type": "Company",
    "country": "PA"
  }
  ```
- `POST /api/v1/compliance/manual/query` - Query compliance manual with natural language
  ```json
  {
    "query": "What are the requirements for enhanced due diligence?",
    "max_context_chunks": 5
  }
  ```
- `POST /api/v1/compliance/due-diligence/requirements` - Get due diligence requirements
  ```json
  {
    "client_risk_level": "high",
    "client_type": "legal_entity",
    "is_pep": true
  }
  ```
- `POST /api/v1/compliance/verify-customer` - Verify customer against PEP and sanctions lists
  ```json
  {
    "customer": { 
      "name": "John Doe",
      "dob": "1970-01-01",
      "country": "US",
      "type": "natural"
    },
    "directors": [], 
    "ubos": []
  }
  ```
- `GET /api/v1/compliance/country-risk` - Get country risk matrix data
- `GET /api/v1/compliance/monitoring/tasks` - Get status of all scheduled compliance tasks
- `POST /api/v1/compliance/force-update/risk-matrix` - Force update of risk matrix
- `POST /api/v1/compliance/force-update/sanctions` - Force update of all sanctions lists

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

### Docker Deployment

For production deployment with Docker:

```bash
# Build and tag the images
docker build -t legal-contract-tracker-backend ./backend
docker build -t legal-contract-tracker-frontend ./frontend

# Push to your container registry
docker push your-registry/legal-contract-tracker-backend
docker push your-registry/legal-contract-tracker-frontend

# Deploy using docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Configuration

The application supports different environments through environment variables:

### Backend Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration (default: 30)
- `MISTRAL_API_URL` - URL for Mistral API service (default: http://ai-service:80)
- `AI_FALLBACK_MODE` - Force fallback mode for AI features (auto-detected by default)
- `AI_LANGUAGE_MODE` - Set to "es" to force Spanish language processing for all inputs
- `OPENSANCTIONS_API_KEY` - API key for OpenSanctions (optional)
- `COMPLIANCE_MANUAL_PATH` - Path to pre-loaded compliance manual (optional)
- `DOCUMENT_EMBEDDINGS_MODEL` - Model name for document embeddings (default: paraphrase-multilingual-MiniLM-L12-v2)
- `ENABLE_2FA` - Enable two-factor authentication (default: false)
- `ENCRYPTION_KEY` - Key for document encryption (required if ENABLE_ENCRYPTION=true)
- `ENABLE_ENCRYPTION` - Enable document encryption (default: false)

### Frontend Environment Variables

- `VITE_API_URL` - Backend API URL
- `VITE_ENABLE_AI_FEATURES` - Enable/disable AI features in UI
- `VITE_ENABLE_COMPLIANCE_FEATURES` - Enable/disable compliance features in UI
- `VITE_DEFAULT_LANGUAGE` - Default language for UI (en/es)

## AI Integration

The system integrates with the Mistral 7B language model for contract analysis and compliance automation:

- **Hardware Requirements**: NVIDIA GPU with CUDA support (recommended)
- **Fallback Mode**: Automatically uses fallback responses in CPU-only environments
- **Docker Integration**: Uses Docker Compose profiles to select appropriate services
- **Environment Detection**: Automatically detects GPU availability
- **Spanish Language Support**: Comprehensive preprocessing pipeline for Spanish legal documents
- **Retrieval-Augmented Generation (RAG)**: Contextual AI responses based on application data
- **Document Embeddings**: Vector database for semantic search of compliance manuals

For detailed AI setup instructions, see [AI_SETUP.md](./AI_SETUP.md).

## Microservice Architecture

The application follows a modular microservice architecture designed for future expansion:

### Contracts Service

- **Contract Registry**: Manage contract information and metadata
- **Document Storage**: Handle document uploads and versioning
- **Expiration Tracking**: Monitor contract deadlines and send notifications
- **Contract Analysis**: Integrate with AI for clause extraction and risk assessment
- **E-Signature Integration**: Prepare for future digital signature capabilities

### Clients/Providers Service

- **Client Registry**: Manage client information and relationships
- **KYC Documents**: Store and manage Know Your Client documentation
- **Risk Ratings**: Calculate and track client risk levels
- **Relationship Management**: Track client interactions and history

### User Management Service

- **User Registry**: Manage user accounts with roles and permissions
- **Role-Based Access Control**: Define granular permissions for system features
- **Permission Matrix**: Configure feature-level access with time-bound constraints
- **Audit Trail**: Track user actions and permission changes
- **Account Settings**: Handle password resets, account locking/unlocking
- **Time-Bound Permissions**: Set start/end dates for temporary access
- **Notifications**: Send emails for account creation and permission changes

### Compliance Service

- **Manual Integration**: Process compliance manuals with document embeddings
- **Due Diligence Automation**: Implement Basic, Enhanced, and Simplified due diligence
- **Risk Assessment**: Calculate risk across multiple dimensions with comprehensive country coverage
- **Suspicious Activity Detection**: Identify and report suspicious activities
- **PEP/Sanctions Screening**: Screen entities against PEP and sanctions lists (OpenSanctions, UN, OFAC, EU)
- **UAF Reporting**: Generate regulatory reports for Panamanian authorities with automated PDF generation
- **Document Retention**: Enforce document retention policies
- **Unified Verification**: Single API endpoint for complete customer verification
- **High-Risk Alerts**: Dashboard alerts for high-risk entities requiring enhanced due diligence
- **Scheduled Updates**: Automated updates of sanctions lists and risk matrices
- **Task Monitoring**: Comprehensive monitoring of scheduled tasks with status reporting

### Diagnostics Service (Artur)

- **Real-time Health Checks**: Continuous monitoring of all system components including CPU, memory, disk usage
- **Docker Container Monitoring**: Track the health and status of Docker containers, especially AI service containers
- **Intelligent Issue Explanations**: Use Mistral AI to provide clear, human-readable explanations of system issues
- **Corrective Action Suggestions**: Generate specific, actionable suggestions to resolve detected issues
- **Predictive Maintenance**: Analyze historical data to predict potential future issues before they occur
- **Trend Analysis**: Identify deteriorating or improving trends in system health over time
- **Historical Data Logging**: Maintain comprehensive logs of all diagnostic runs for analysis
- **Component-specific Diagnostics**: Targeted checks for AI services, database connections, and system resources
- **Comprehensive Dashboard**: Visual representation of system health with detailed component status
- **API Integration**: RESTful API endpoints for running diagnostics and retrieving statistics
- **Configurable Depth**: Adjust the level of detail in diagnostics based on needs
### Business Administration Service

- **Department Management**: Create and manage business departments with AI capabilities
- **Role & Permission System**: Define roles with granular permissions per department
- **Function Registry**: Create and manage business functions with input/output schemas
- **Workflow Automation**: Configure event-driven automation rules with conditions and actions
- **AI Profile Management**: Configure AI models and parameters per department
- **Department Templates**: Create and apply predefined department configurations
- **User-Department-Role Assignment**: Assign users to departments with specific roles
- **Audit Logging**: Comprehensive logging of administrative actions and system events

### Accounting Service

- **Obligation Management**: Track and manage financial obligations with accurate date logic
- **Payment Execution**: Process payments for obligations directly from the frontend
- **Email Generation**: Automatically generate and send email notifications for payments
- **Obligation Templates**: Pre-configured templates for common obligations (DGI, Municipio de Chitré, CSS, etc.)
- **Date Logic**: Smart date validation for upcoming and overdue obligations
- **Obligation Scraping**: Simulated web scraping to populate obligations for companies
- **AI Integration**: Uses Mistral AI for intelligent email drafting and analysis
- **Audit Logging**: Comprehensive logging of all payment activities
- **Company Management**: Complete company profiles with fiscal information

### Workflow Service

- **Workflow Templates**: Define approval and review workflows
- **Workflow Instances**: Track active workflow processes
- **Approval Chains**: Manage sequential and parallel approvals
- **Notifications**: Alert users of pending actions

### Tasks Service

- **Task Management**: Create and assign tasks
- **Reminders**: Send notifications for upcoming deadlines
- **Task Dependencies**: Define relationships between tasks
- **Task Templates**: Create reusable task patterns

### Audit Service

- **Action Logging**: Record all user actions
- **System Events**: Track system-generated events
- **Compliance Tracking**: Monitor compliance-related activities
- **Report Generation**: Create audit reports for regulatory purposes

### AI Service

- **Contract Intelligence**: Extract and analyze contract clauses
- **Risk Assessment**: Score contracts based on risk factors
- **Natural Language Interface**: Query application data using natural language
- **Task Suggestions**: Generate tasks based on contract content
- **Spanish Language Support**: Preprocess Spanish legal documents for AI analysis
- **Contextual Generation**: Provide context-aware responses using RAG

### Spanish Language Support

The system includes a comprehensive Spanish language preprocessing pipeline for Mistral AI integration:

- **Automatic Language Detection**: Identifies Spanish inputs using langdetect
- **Accent Normalization**: Restores missing accents in Spanish text (e.g., "clausula" → "cláusula")
- **Punctuation Balancing**: Adds missing opening punctuation marks (e.g., "Como estas?" → "¿Como estas?")
- **Legal Terminology Standardization**: Corrects common legal terms (e.g., "rescision" → "rescisión")
- **Error Handling**: Gracefully falls back to original input if preprocessing fails
- **Debug Mode**: Provides detailed preprocessing information for troubleshooting

#### Usage

The Spanish language support can be enabled in two ways:

1. **Automatic Detection**: The system automatically detects Spanish language inputs
2. **Environment Variable**: Set `AI_LANGUAGE_MODE=es` to force Spanish processing for all inputs

#### API Integration

Enable debug mode to get detailed preprocessing information:

```json
POST /api/v1/ai/mistral/generate
{
  "inputs": "La clausula de terminacion requiere notificacion previa.",
  "debug": true
}
```

Response includes preprocessing details:

```json
{
  "generated_text": "...",
  "is_fallback": false,
  "model": "OpenHermes-2.5-Mistral-7B",
  "debug_info": {
    "original_text": "La clausula de terminacion requiere notificacion previa.",
    "processed_text": "La cláusula de terminación requiere notificación previa.",
    "is_spanish": true,
    "language_detected": "es",
    "changes_made": true
  }
}
```

### Internationalization (i18n)

Cortana supports multiple languages using i18next and react-i18next. The default fallback language is Spanish, with English also supported.

#### Translation Files
- English: `frontend/src/i18n/locales/en.json`
- Spanish: `frontend/src/i18n/locales/es.json`

#### Translation Keys Structure
- `common`: Shared components and general UI elements
  - `navigation`: Navigation items and menu labels
  - `labels`: Form labels and general UI labels
  - `enterpriseManagement`: Application subtitle
  - `logout`: Logout text
  - `openMenu`: Accessibility text for menu button
  - `recentActivity`: Section headers for activity lists
- `dashboard`: Dashboard-specific content
  - `welcomeMessage`: Welcome text
  - `quickActions`: Quick action section headers
  - `systemStatus`: System status information
  - `lastUpdated`: Timestamp labels
- `contracts`: Contract module content
- `legal`: Legal module content
- `compliance`: Compliance module content
- `accounting`: Accounting module content
- `traffic`: Traffic module content
- `ai`: AI module content
- `users`: User management module content
  - `roles`: Role-related labels and messages
  - `permissions`: Permission-related labels and messages
  - `audit`: Audit log labels and messages
  - `account`: Account settings labels and messages
  - `notifications`: User notification messages

#### Best Practices
1. **Never hardcode text** directly in components. Always use the translation function:
   ```tsx
   const { t } = useTranslation();
   return <div>{t('common.navigation.dashboard')}</div>;
   ```
   
2. **Add new keys** to both language files when adding new UI text
3. **Follow the existing namespace structure** for consistency
4. **Use concise business-appropriate terms** for Spanish translations
5. **Test both languages** before submitting changes
6. **Use interpolation** for dynamic content:
   ```tsx
   {t('traffic.sentDaysAgo', { days: 2 })}
   ```

### Compliance Automation

The compliance automation system integrates with Mistral 7B to provide context-aware compliance guidance:

#### Document Embeddings

The system uses Sentence Transformers and FAISS to create embeddings of compliance manuals:

- **Multilingual Support**: Works with both Spanish and English compliance documents
- **Intelligent Chunking**: Breaks documents into semantic chunks for better retrieval
- **Vector Search**: Finds relevant sections based on semantic similarity
- **Context Retrieval**: Provides relevant context for AI responses

#### Due Diligence Automation

The system automates different levels of due diligence based on risk factors:

- **Basic Due Diligence**: Standard KYC for low-risk clients
- **Enhanced Due Diligence**: Additional checks for high-risk clients and PEPs
- **Simplified Due Diligence**: Streamlined process for very low-risk scenarios
- **Dynamic Requirements**: Adjusts requirements based on client risk profile

#### Risk Assessment

Comprehensive risk assessment across multiple dimensions:

- **Client Risk**: Based on client type, location, and business activity
- **Geographic Risk**: Country and region-specific risk factors
- **Product/Service Risk**: Risk associated with specific financial products
- **Channel Risk**: Risk based on delivery channels
- **Transactional Risk**: Patterns and anomalies in transactions

#### Sanctions Screening

Integration with OpenSanctions and local databases for comprehensive screening:

- **PEP Screening**: Identifies politically exposed persons
- **Sanctions Lists**: Checks against OFAC, UN, EU, and other sanctions lists
- **Local Database**: Maintains a local database of known sanctioned entities for faster matching
- **Fuzzy Matching**: Uses partial name matching to identify potential sanctions matches
- **Intelligent Caching**: 24-hour caching to reduce API calls
- **Detailed Results**: Provides match scores and entity details
- **Robust Error Handling**: Gracefully handles API failures with fallback mechanisms
- **Multiple Data Sources**: Parallel screening against OpenSanctions, UN, OFAC, and EU lists
- **Unified API**: Single endpoint for comprehensive verification

#### Risk Matrix

Comprehensive country risk assessment using multiple authoritative sources:

- **Basel AML Index**: Incorporates Basel AML Index scores and rankings
- **FATF Lists**: Includes FATF Blacklist and Greylist status
- **EU High-Risk Countries**: Incorporates EU high-risk third countries list
- **Comprehensive Coverage**: Includes 190+ countries with ISO codes
- **Fallback Mechanism**: Uses last known data if external sources are unavailable
- **Validation System**: Ensures data integrity and completeness
- **Automatic Updates**: Weekly scheduled updates with error handling
- **Heatmap Visualization**: Interactive global risk heatmap in the frontend

#### Monitoring Scheduled Tasks

The compliance module includes a comprehensive monitoring system for all scheduled tasks:

##### Monitoring Endpoints

- `GET /api/v1/compliance/monitoring/tasks` - Get status of all scheduled compliance tasks
  ```json
  {
    "tasks": {
      "risk_matrix": {"status": "success", "last_run": "2025-05-08T12:00:00", "next_run": "2025-05-15T12:00:00", "error": null},
      "ofac": {"status": "success", "last_run": "2025-05-08T00:00:00", "next_run": "2025-05-09T00:00:00", "error": null},
      "eu_sanctions": {"status": "success", "last_run": "2025-05-08T00:00:00", "next_run": "2025-05-09T00:00:00", "error": null},
      "un_sanctions": {"status": "success", "last_run": "2025-05-08T00:00:00", "next_run": "2025-05-09T00:00:00", "error": null},
      "opensanctions": {"status": "success", "last_run": "2025-05-08T00:00:00", "next_run": "2025-05-09T00:00:00", "error": null}
    },
    "last_updated": "2025-05-08T12:34:56"
  }
  ```

##### Task Schedule

- **Risk Matrix**: Updated weekly (every Sunday at midnight)
- **Sanctions Lists** (OFAC, EU, UN, OpenSanctions): Updated daily (at midnight)

##### Monitoring Dashboard

The compliance dashboard includes a section showing the status of all scheduled tasks with their last update time and next scheduled run. The dashboard also displays alerts for any failed tasks that require attention.

##### Command Line Monitoring

You can also monitor task status from the command line:

```bash
# Check all task statuses
curl -X GET http://localhost:8000/api/v1/compliance/monitoring/tasks

# Force update a specific task
curl -X POST http://localhost:8000/api/v1/compliance/force-update/risk-matrix

# View logs for scheduled tasks
tail -f ~/repos/Cortana/backend/logs/scheduler.log
```

## Recent Updates

### May 10, 2025
- Fixed ImportError in accounting module by implementing `generate_email_draft` function
- Fixed Artur Dashboard loading and added it to the sidebar under Admin section
- Fixed System Settings loading issue
- Fixed Compliance Dashboard by implementing proper API endpoint with required JSON structure
- Added missing frontend dependency (react-toastify) for ObligationTable component

- **May 2025**:
  - Implemented Artur diagnostics module for system health monitoring and issue resolution
  - Added real-time health checks for system resources, Docker containers, and services
  - Integrated Mistral AI for intelligent issue explanations and corrective action suggestions
  - Implemented predictive maintenance through trend analysis of system health data
  - Created comprehensive diagnostics dashboard with component status visualization
  - Added RESTful API endpoints for running diagnostics and retrieving statistics
  - Implemented historical data logging for system performance tracking
  - Added diagnostics module to sidebar navigation for easy access
  - Implemented comprehensive User Management module with role-based access control
  - Added granular permission system with time-bound constraints
  - Created user audit trail for tracking permission changes
  - Implemented account management features (creation, password reset, lock/unlock)
  - Fixed navigation issues for User Management module in sidebar
  - Resolved environment variable compatibility issues with Vite
  - Implemented comprehensive compliance verification system for customer screening
  - Added new endpoint for verifying customers against PEP and sanctions lists
  - Integrated with multiple data sources (UN, OFAC, EU, Wikidata)
  - Added entity enrichment with aliases, IDs & metadata
  - Implemented parallel screening against multiple databases
  - Created end-to-end testing scripts for verification
  - Fixed Mistral AI integration unexpectedly falling back to CPU mode
  - Improved health-check logic to better handle DNS resolution errors
  - Enhanced error handling in Spanish language pipeline
  - Added comprehensive test script (`app.scripts.test_mistral_integration`) for validating Mistral AI endpoints
  - Implemented CI configuration with GitHub Actions for automated testing
  - Updated AI_SETUP.md with improved troubleshooting information
  - Added detailed logging for connection attempts and failures
  - Made fallback mode logic more selective to only trigger on persistent server errors
  - Explicitly set `AI_FALLBACK_MODE=false` in docker-compose.yml for GPU profile
  - Fixed OFAC integration to correctly identify sanctioned entities
  - Implemented local database of known sanctioned entities for faster matching
  - Added robust error handling in compliance verification service
  - Integrated Customer Verification with Compliance Dashboard
  - **Accounting Module Enhancements**:
    - Fixed the "Pay" button functionality in the frontend to process payments
    - Implemented email generation for obligations with HTML templates
    - Added proper date logic for upcoming and overdue obligations
    - Created obligation templates for DGI, Municipio de Chitré, CSS, and more
    - Implemented obligation scraping simulation for Magnate Spes company
    - Added new endpoints for payment processing and obligation scraping
    - Integrated Mistral AI for email content generation
    - Enhanced frontend with proper error handling and success notifications
    - Implemented automatic data refresh after payment processing

- **Previous Updates**:
  - Implemented comprehensive compliance automation with Mistral 7B integration
  - Added document embeddings for compliance manual integration
  - Integrated OpenSanctions for PEP and sanctions screening
  - Implemented contextual AI generation with RAG capabilities
  - Enhanced Spanish language support pipeline for legal document preprocessing
  - Refactored architecture into microservices for better scalability
  - Added compliance dashboard with comprehensive metrics
  - Implemented UAF report generation for regulatory compliance
  - Added document retention policy enforcement
  - Enhanced security with encryption capabilities

## Future Enhancements

- Digital signatures integration
- Automated contract renewals
- Advanced document versioning with diff visualization
- Enhanced analytics dashboard with predictive capabilities
- Integration with other departments (Accounting, HR, Procurement)
- Mobile application for on-the-go access
- Expanded AI capabilities with fine-tuned models
- Integration with Risk 365 platform for enhanced risk management
- SAP Business One integration for real-time financial data
- Blockchain-based document verification
- Advanced anomaly detection using machine learning

## DMCE Module

The DMCE (Declaración de Movimiento Comercial Electrónico) module provides automation for the DMCE portal processes. See [DMCE documentation](dmce/reports/README_DMCE_UPDATE.md) for details.

### Directory Structure

- `dmce/scripts/`: Contains all automation scripts
- `dmce/reports/`: Contains documentation and test reports
- `dmce/screenshots/`: Contains screenshots from automation runs
- `dmce/videos/`: Contains video recordings from automation runs
- `dmce/logs/`: Contains logs from automation runs
- `dmce/downloads/`: Contains downloaded files from automation runs
