# Legal Contract Tracker - Frontend

This is the frontend application for the Legal Contract Tracker, built with React, TypeScript, and Vite. It provides a modern, responsive user interface for managing legal contracts, clients, and workflows with AI-powered features.

## Features

- Modern React application with TypeScript
- Responsive UI with Tailwind CSS
- AI-powered contract analysis dashboard
- Natural language query interface for contracts
- Comprehensive client and contract management
- Workflow and task tracking
- Compliance automation dashboard
- Spanish language support
- Dark and light mode support

## Key Components

### AI Components

- **AIContractAnalysis**: Analyzes contracts using Mistral 7B model
- **AIContextualChat**: Provides context-aware responses to natural language queries
- **AICommandCenter**: Central hub for AI-powered features

### Legal Module Components

- **ContractList**: Displays and manages contracts
- **ClientManagement**: Handles client information
- **WorkflowTracker**: Tracks approval workflows
- **TaskManager**: Manages and assigns tasks

### Compliance Components

- **ComplianceDashboard**: Overview of compliance metrics
- **SanctionsScreening**: Screens entities against sanctions lists
- **UAFReportGenerator**: Generates regulatory reports

## Setup Instructions

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

1. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```
   or
   ```
   pnpm install
   ```

2. Create a `.env` file with the following content:
   ```
   VITE_API_URL=http://localhost:8000
   VITE_ENABLE_AI_FEATURES=true
   VITE_ENABLE_COMPLIANCE_FEATURES=true
   VITE_DEFAULT_LANGUAGE=en
   ```

3. Run the development server:
   ```
   npm run dev
   ```
   or
   ```
   yarn dev
   ```
   or
   ```
   pnpm dev
   ```

4. The frontend will be available at http://localhost:5173

## Building for Production

```
npm run build
```
or
```
yarn build
```
or
```
pnpm build
```

The built files will be in the `dist` directory, which can be deployed to any static hosting service.

## API Integration

The frontend integrates with the backend API using Axios. The main API client is configured in `src/lib/api.ts`.

### AI Endpoints

The frontend interacts with the following AI endpoints:

- `POST /api/v1/ai/mistral/generate`: Generate text with Mistral 7B model
- `POST /api/v1/ai/contextual-generate`: Generate context-aware responses
- `GET /api/v1/test-mistral`: Test Mistral model connection and environment
- `POST /api/v1/ai/analyze-contract`: Analyze contract for risks and clauses
- `POST /api/v1/ai/extract-clauses`: Extract clauses from contract text

Example usage in components:

```tsx
// Example for Mistral endpoint
const response = await axios.post(`${API_URL}/api/v1/ai/mistral/generate`, {
  inputs: query,
  max_new_tokens: 100,
});

// Update state with the response
setQueryResponse(response.data.generated_text);
setIsFallback(response.data.is_fallback || false);
```

### Fallback Mode Handling

The frontend handles AI fallback mode by checking the `is_fallback` flag in API responses:

```tsx
// Display fallback warning if needed
{isFallback && (
  <Alert severity="warning">
    Using fallback mode. The Mistral 7B model requires GPU hardware.
  </Alert>
)}
```

## Testing

Run tests with Jest and React Testing Library:

```
npm test
```
or
```
yarn test
```
or
```
pnpm test
```

## Recent Updates

- **May 2025**:
  - Updated AI components to handle improved Mistral AI integration
  - Added fallback mode indicators in the UI
  - Enhanced error handling for AI service connection issues
  - Updated API client to use new endpoint structure
  - Improved Spanish language support in the UI
  - Added debug mode for AI responses to show preprocessing details
