import os
import openai
import logging
import base64
from typing import Dict
from openai import OpenAI
import mimetypes

logger = logging.getLogger(__name__)

client = OpenAI()

def encode_image(image_path):
    """Encode an image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def is_pdf(file_path):
    """Check if the file is a PDF"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type == 'application/pdf'

def is_image(file_path):
    """Check if the file is an image"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('image/')

async def get_file_insight(filename: str) -> str:
    """Extract insights from a single file using an LLM"""
    try:
        if not os.path.exists(filename):
            return f"Error: File {filename} does not exist"

        if is_pdf(filename):
            # Handle PDF
            file = client.files.create(
                file=open(filename, "rb"),
                purpose="user_data"
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You extract the main most valuable insight from the file. Summarize this insight in one or two lines, try to reference to the content as much as possible. Be factual"},
                    {"role": "user",
                     "content": [
                         {
                             "type": "file",
                             "file": {
                                 "file_id": file.id,
                             }
                         },
                         {
                             "type": "text",
                             "text": "Extract the main insights from this file.",
                         }
                     ]
                    }
                ]
            )
        elif is_image(filename):
            # Handle image
            base64_image = encode_image(filename)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You extract the main most valuable insight from the image. Summarize this insight in one or two lines, try to reference to the content as much as possible. Be factual"},
                    {"role": "user",
                     "content": [
                         {"type": "text", "text": "Extract the main insights from this image."},
                         {
                             "type": "image_url",
                             "image_url": {
                                 "url": f"data:image/jpeg;base64,{base64_image}",
                             },
                         }
                     ]
                    }
                ]
            )
        else:
            return f"Error: File {filename} is not a supported format (PDF or image)"

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting insight from LLM: {str(e)}")
        return f"Error extracting insight: {str(e)}"

async def get_summary_from_insights(insights: Dict[str, str]) -> str:
    """Generate a comprehensive summary from all file insights"""
    try:
        files_and_insights = "\n\n".join([f"File: {filename}\nInsight: {insight}"
                                         for filename, insight in insights.items()])

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that creates comprehensive summaries from multiple document insights."},
                {"role": "user", "content": f"Create a detailed summary report based on these file insights:\n\n{files_and_insights}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting summary from LLM: {str(e)}")
        return f"Error generating summary: {str(e)}"
