from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import database initialization
from db.settings import engine
from db.models.Base import Base
from db.models.User import User
from db.models.Digests import Digest
# Import routers
from api.router_users import router as users_router



# Create FastAPI app
app = FastAPI(
    title="Summit Digest API",
    description="API for Summit Digest application",
    version="1.0.0"
)



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist)")

# Include routers
app.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

# Root endpoint
@app.get("/", tags=["root"])
async def read_root():
    return {
        "message": "Welcome to Summit Digest API",
        "documentation": "/docs"
    }

# Run the app if executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
