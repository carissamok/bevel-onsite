# Bevel Backend Onsite Check-ins - Take Home Assessment

This is a monorepo containing a Next.js frontend and two backend services (FastAPI and Express/TypeScript).

## Project Structure

```
.
├── frontend/          # Next.js application (TypeScript, Tailwind CSS)
├── backend-python/   # FastAPI backend (Python)
├── backend-node/     # Express backend (TypeScript/Node.js)
└── README.md
```

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (for the chat functionality)

## Setup

### Install Dependencies

```bash
# Install all dependencies
npm run install:all

# Or install individually:
cd frontend && npm install
cd backend-node && npm install
cd backend-python && pip install -r requirements.txt
```

### Environment Variables

**Backend Node.js:**
Create a `.env` file in `backend-node/`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Backend Python:**
Create a `.env` file in `backend-python/`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Frontend (Optional):**
Create a `.env.local` file in `frontend/` if you need to customize the API URL:
```bash
NEXT_PUBLIC_API_URL=http://localhost:3001
```
The frontend defaults to `http://localhost:3001` if not specified. To use the Python backend, change this to `http://localhost:8000`.

## Running the Applications

### Development Mode

Run each service in a separate terminal:

**Frontend (Next.js):**
```bash
npm run dev:frontend
# or
cd frontend && npm run dev
```
Runs on http://localhost:3000

**Python Backend (FastAPI):**
```bash
npm run dev:backend-python
# or
cd backend-python && uvicorn main:app --reload --port 8000
```
Runs on http://localhost:8000
API docs available at http://localhost:8000/docs

**Node.js Backend (Express/TypeScript):**
```bash
npm run dev:backend-node
# or
cd backend-node && npm run dev
```
Runs on http://localhost:3001

## API Endpoints

### FastAPI Backend (Port 8000)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `POST /api/chat/{chat_id}/send` - Send a chat message and get AI response
  - Request body: `{ message: string, conversation: { messages: Array<{text, sender, timestamp}> } }`
  - Returns: `{ message: {text, sender, timestamp}, conversation: { messages: [...] } }`

### Express Backend (Port 3001)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/chat/:id/send` - Send a chat message and get AI response
  - Request body: `{ message: string, conversation: { messages: Array<{text, sender, timestamp}> } }`
  - Returns: `{ message: {text, sender, timestamp}, conversation: { messages: [...] } }`

## Technologies Used

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend (Python)**: FastAPI, Uvicorn, OpenAI SDK
- **Backend (Node.js)**: Express, TypeScript, Node.js, Vercel AI SDK, OpenAI

## Development Notes

- CORS is configured on both backends to allow requests from the Next.js frontend (localhost:3000)
- Both backends include health check endpoints for monitoring
- TypeScript is used in both the frontend and Node.js backend for type safety

