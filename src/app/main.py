from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# initialize db models
from db.settings import engine
from db.models.Base import Base
from db.models.User import User
from db.models.Digests import Digest

# import routes
from routes.auth import router as auth_router
from routes.home import router as home_router
from routes.digest import router as digest_router

# create FastAPI app
app = FastAPI(
    title="Summit Digest",
    description="A full-stack application for Summit Digest",
    version="1.0.0"
)

# configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static files
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static"
)

# initialize templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# initialize database on startup
@app.on_event("startup")
def startup_event():
    # create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if they didn't exist)")

# include web page routers
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(digest_router)

# run the app if executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
