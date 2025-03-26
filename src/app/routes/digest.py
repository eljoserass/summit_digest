from fastapi import APIRouter, Request, Depends, HTTPException, Form, UploadFile, File, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from db.dependencies import get_db
from db.models.User import User
from db.models.Digests import Digest, DigestStatus
from utils import get_current_user_from_cookie
from typing import Optional
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

import markdown
templates.env.filters["markdown"] = lambda text: markdown.markdown(text) if text else ""


@router.get("/digests", response_class=HTMLResponse)
async def list_digests(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)
        digests = db.query(Digest).filter(Digest.user_id == current_user.id).all()
        return templates.TemplateResponse(
            "digests/list.html",
            {"request": request, "title": "My Digests", "digests": digests, "user": current_user}
        )
    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/digests/new", response_class=HTMLResponse)
async def new_digest_page(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)
        return templates.TemplateResponse(
            "digests/create.html",
            {"request": request, "title": "Create Digest", "user": current_user}
        )
    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/digests/new", response_class=HTMLResponse)
async def create_digest(
    request: Request,
    summary: str = Form(...),
    media_file: Optional[UploadFile] = File(None),
    insights: str = Form("{}"),
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Process the uploaded file if any
        media_path = None
        if media_file and media_file.filename:
            # Create uploads directory if it doesn't exist
            uploads_dir = Path(__file__).parent.parent / "static" / "uploads"
            os.makedirs(uploads_dir, exist_ok=True)

            # Generate a safe filename
            safe_filename = f"{current_user.id}_{media_file.filename.replace(' ', '_')}"
            file_path = uploads_dir / safe_filename

            # Save the file
            with open(file_path, "wb") as f:
                content = await media_file.read()
                f.write(content)

            # Store the relative path
            media_path = f"/static/uploads/{safe_filename}"
            logger.info(f"File saved at {media_path}")

        # Process the insights
        try:
            insights_dict = json.loads(insights)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON insights: {insights}")
            insights_dict = {}

        # Create the digest
        new_digest = Digest(
            user_id=current_user.id,
            resolution_summary=summary,
            media_path=media_path,
            insights=insights_dict
        )

        db.add(new_digest)
        db.commit()
        db.refresh(new_digest)
        logger.info(f"Created new digest with ID {new_digest.id}")

        # Redirect to the digest list
        return RedirectResponse(url="/digests", status_code=status.HTTP_303_SEE_OTHER)

    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error creating digest: {str(e)}")
        # In case of error, return to the form with error message
        current_user = await get_current_user_from_cookie(request, db)
        return templates.TemplateResponse(
            "digests/create.html",
            {
                "request": request,
                "title": "Create Digest",
                "user": current_user,
                "error": f"Error creating digest: {str(e)}",
                "form_data": {"summary": summary, "insights": insights}
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.get("/digests/{digest_id}", response_class=HTMLResponse)
async def view_digest(
    request: Request,
    digest_id: int,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)
        digest = db.query(Digest).filter(
            Digest.id == digest_id,
            Digest.user_id == current_user.id
        ).first()

        if not digest:
            logger.warning(f"Digest {digest_id} not found or not owned by user {current_user.id}")
            return templates.TemplateResponse(
                "digests/not_found.html",
                {"request": request, "title": "Digest Not Found", "user": current_user},
                status_code=status.HTTP_404_NOT_FOUND
            )

        return templates.TemplateResponse(
            "digests/detail.html",
            {"request": request, "title": "Digest Details", "digest": digest, "user": current_user}
        )
    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/digests/{digest_id}/delete", response_class=HTMLResponse)
async def confirm_delete_digest(
    request: Request,
    digest_id: int,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)
        digest = db.query(Digest).filter(
            Digest.id == digest_id,
            Digest.user_id == current_user.id
        ).first()

        if not digest:
            logger.warning(f"Digest {digest_id} not found or not owned by user {current_user.id}")
            return RedirectResponse(url="/digests", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse(
            "digests/confirm_delete.html",
            {"request": request, "title": "Confirm Delete", "digest": digest, "user": current_user}
        )
    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/digests/{digest_id}/delete", response_class=HTMLResponse)
async def delete_digest(
    request: Request,
    digest_id: int,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)
        digest = db.query(Digest).filter(
            Digest.id == digest_id,
            Digest.user_id == current_user.id
        ).first()

        if not digest:
            logger.warning(f"Digest {digest_id} not found or not owned by user {current_user.id}")
            return RedirectResponse(url="/digests", status_code=status.HTTP_303_SEE_OTHER)

        if digest.media_path:
            try:
                file_path = Path(__file__).parent.parent / "static" / digest.media_path.lstrip("/static/")
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted file {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file: {str(e)}")

        # Delete the digest
        db.delete(digest)
        db.commit()
        logger.info(f"Deleted digest {digest_id}")

        return RedirectResponse(url="/digests", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/digests/upload", response_class=HTMLResponse)
async def upload_digest(
    request: Request,
    title: str = Form(...),
    media_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user_from_cookie(request, db)

        # Validate the file is a zip
        if not media_file.filename.endswith('.zip'):
            return templates.TemplateResponse(
                "digests/create.html",
                {
                    "request": request,
                    "title": "Create Digest",
                    "user": current_user,
                    "error": "Please upload a zip file"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        uploads_dir = Path(__file__).parent.parent / "static" / "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        # replace filename
        safe_filename = f"{current_user.id}_{title.replace(' ', '_')}_{media_file.filename.replace(' ', '_')}"
        file_path = uploads_dir / safe_filename

        # Save the file
        with open(file_path, "wb") as f:
            content = await media_file.read()
            f.write(content)

        media_path = f"/static/uploads/{safe_filename}"

        new_digest = Digest(
            user_id=current_user.id,
            title=title,
            media_path=media_path,
            status="pending",
        )

        db.add(new_digest)
        db.commit()
        db.refresh(new_digest)

        from services.task_manager import start_background_task
        from services.digest_processor import process_digest

        # process digest by id TODO this is currently blocking execution
        start_background_task(
            f"digest_{new_digest.id}",
            process_digest,
            new_digest.id
        )

        # digest view
        return RedirectResponse(
            url=f"/digests/{new_digest.id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except HTTPException:
        logger.info("User not authenticated, redirecting to login")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error uploading digest: {str(e)}")
        return templates.TemplateResponse(
            "digests/create.html",
            {
                "request": request,
                "title": "Create Digest",
                "user": current_user,
                "error": f"Error uploading digest: {str(e)}"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
