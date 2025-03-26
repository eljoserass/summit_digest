import os
import zipfile
import asyncio
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from db.models.Digests import Digest, DigestStatus
from services.llm_service import get_file_insight, get_summary_from_insights
from db.settings import SessionLocal

logger = logging.getLogger(__name__)

async def process_digest(digest_id: int):
    """Process a digest asynchronously"""
    db = SessionLocal()

    try:
        digest = db.query(Digest).filter(Digest.id == digest_id).first()
        if not digest or not digest.media_path:
            logger.error(f"Digest {digest_id} not found or has no media file")
            return

        try:
            # update digest status
            digest.status = DigestStatus.PROCESSING.value
            db.commit()

            # get the full path to the zip file
            zip_path = Path(__file__).parent.parent / "static" / digest.media_path.lstrip("/static/")

            # create extraction directory
            extract_dir = Path(__file__).parent.parent / "static" / "extracts" / str(digest.id)
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # filter __MACOSX folders
                files_to_extract = [f for f in zip_ref.namelist() if not f.startswith('__MACOSX/') and not f.endswith('/')]
                for file in files_to_extract:
                    zip_ref.extract(file, extract_dir)

                all_files = files_to_extract
                digest.total_files = len(all_files)
                db.commit()

            insights = {}
            for i, file_path in enumerate(all_files):
                try:
                    full_path = extract_dir / file_path
                    if not os.path.exists(full_path):
                        logger.warning(f"File {full_path} does not exist")
                        continue

                    insight = await get_file_insight(str(full_path))
                    insights[file_path] = insight

                    digest.processed_files = i + 1
                    digest.insights = insights
                    db.commit()

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    insights[file_path] = f"Error: {str(e)}"

            if insights:
                summary = await get_summary_from_insights(insights)
                digest.resolution_summary = summary

            digest.status = DigestStatus.COMPLETED.value
            db.commit()

        except Exception as e:
            logger.error(f"Error processing digest {digest_id}: {str(e)}")
            digest.status = DigestStatus.FAILED.value
            digest.resolution_summary = f"Processing failed: {str(e)}"
            db.commit()
    finally:
        db.close()
