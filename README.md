# Submission of `Project 1`

## Overview
Summit Digest is a platform where members of Fenix can access to handle all the data points they collected during a sumimt / conference.

By simply uploading said datapoints (.pdf, .jpg, .png, .jpeg) in a .zip, the platform will go through each datapoint, and extract the most valuable insight, when finished it will provide a summary for the entire set of data.

## Features
- User authentication system (register, login, logout)
- Upload and process ZIP files containing conference materials
- Extract insights from documents and images using AI
- Generate comprehensive summaries of the materials
- Dashboard to manage and view digests
- Real-time processing status updates

## Technical Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 Templates, Bootstrap 5
- **AI Processing**: OpenAI GPT-4o
- **Authentication**: JWT-based authentication



```
summit_digest/
├── src/
│   └── app/
│       ├── db/                      # Database modules
│       │   ├── models/              # SQLAlchemy models
│       │   │   ├── Base.py
│       │   │   ├── Digests.py
│       │   │   └── User.py
│       │   ├── schemas/             # Pydantic schemas
│       │   │   ├── Digest.py
│       │   │   └── User.py
│       │   ├── dependencies.py      # Database dependencies
│       │   └── settings.py          # Database configuration
│       ├── routes/                  # API routes
│       │   ├── auth.py              # Authentication routes
│       │   ├── digest.py            # Digest management routes
│       │   └── home.py              # Home and dashboard routes
│       ├── services/                # Business logic services
│       │   ├── auth_service.py      # Authentication service
│       │   ├── digest_processor.py  # Digest processing service
│       │   ├── llm_service.py       # OpenAI integration service
│       │   └── task_manager.py      # Background task management
│       ├── static/                  # Static assets
│       │   ├── css/                 # Stylesheets
│       │   │   └── styles.css
│       ├── templates/               # Jinja2 HTML templates
│       │   ├── auth/                # Authentication templates
│       │   ├── digests/             # Digest templates
│       │   ├── home/                # Home and dashboard templates
│       │   └── base.html            # Base template layout
│       ├── main.py                  # Application entry point
│       └── utils.py                 # Utility functions
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/summit-digest.git
   cd summit-digest
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   export OPENAI_API_KEY="your-openai-api-key"
   export SECRET_KEY="your-secret-key-for-jwt"
   ```

5. Run the application:
   ```
   cd src/app
   python main.py
   ```

6. Access the application at `http://localhost:8000`

## Usage
1. Register an account or log in
2. Navigate to "Create Digest" page
3. Upload a ZIP file containing your conference materials
4. The system will process your files and generate insights
5. View the processed digest with AI-generated summaries

## Future Enhancements
- Redis queue with digests processor workers
- Micro Service orchestration (FastAPI Non-monolithic backend, MySQL, Redis)
- Parallelize insight extraction.
- AI generated title and sub-title when digest is finished.
- Serve and reference uploaded files.
- Fenix brand styling.
- Support for more file types (DOC, PPT, etc.)
- Export options for digests (PDF, DOC)
- Model Privacy: OpenAI stores data passed through the API, either use AzureOpenAI, other vendors, or local model serving.
