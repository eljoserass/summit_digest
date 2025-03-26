from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from db.dependencies import get_db
from db.models.User import User
from db.models.Digests import Digest
from utils import get_current_user_from_cookie

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

import markdown
templates.env.filters["markdown"] = lambda text: markdown.markdown(text) if text else ""

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home/index.html",
        {"request": request, "title": "Summit Digest - Home"}
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    # get user fmro cookie
    try:
        current_user = await get_current_user_from_cookie(request, db)
        digests = db.query(Digest).filter(Digest.user_id == current_user.id).all()
        return templates.TemplateResponse(
            "home/dashboard.html",
            {"request": request, "title": "Dashboard", "user": current_user, "digests": digests}
        )
    except HTTPException:
        # Redirect to login if not authenticated
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
