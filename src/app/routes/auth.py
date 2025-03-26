from fastapi import APIRouter, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from db.dependencies import get_db
from db.models.User import User
from services.auth_service import verify_password, get_password_hash, create_access_token
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "title": "Login", "error": error}
    )

@router.post("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "title": "Login",
                "error": "Invalid credentials",
                "username": username
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Create access token and set cookie
    access_token = create_access_token(data={"sub": user.username})

    # Create response with redirect
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    # Set cookie properly
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,  # 30 minutes
        expires=1800,
    )
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "title": "Register", "error": error}
    )

@router.post("/register", response_class=HTMLResponse)
async def register_form(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "title": "Register",
                "error": "Passwords do not match",
                "username": username,
                "email": email
            }
        )

    # Check if user exists
    user_exists = db.query(User).filter(User.username == username).first()
    if user_exists:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "title": "Register",
                "error": "Username already exists",
                "username": username,
                "email": email
            }
        )

    # Create user
    hashed_password  = get_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()

    # Redirect to login page
    return RedirectResponse(url="/login?registered=true", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response
