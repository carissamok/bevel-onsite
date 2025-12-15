from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat

app = FastAPI(title="Bevel Backend API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup
    print(f"Server starting on port {os.getenv('PORT', 3000)}")

    yield
    # Shutdown
    await close_pool()

# Include routers
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

