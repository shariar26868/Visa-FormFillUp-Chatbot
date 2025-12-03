🌍 Immigration Chatbot - AI-Powered Visa Application Assistant
An intelligent conversational AI system that helps users find, match, and fill visa application forms through natural language interactions. Built with FastAPI, OpenAI GPT-4, MongoDB, and AWS S3.

📋 Table of Contents

Features
Tech Stack
Architecture
Prerequisites
Installation
Configuration
Running the Application
API Documentation
Project Structure
Key Features Explained
Troubleshooting
Contributing
License


✨ Features
🤖 Intelligent Conversational Flow

Natural Language Processing: Understands user intent through casual conversation
Smart Form Matching: AI-powered form recommendation based on 5-6 questions
Multi-State Management: Handles complex conversation flows (chatting → matched → filling → completed)
Off-Topic Detection: Politely redirects non-visa queries

📄 Advanced Form Processing

Unlimited Field Extraction: OCR with PyMuPDF + OpenAI Vision API
Multi-Page Support: Processes all pages of visa forms
Intelligent Metadata Extraction: Auto-detects visa type, country, and purpose
Bulk Upload: Process multiple PDFs simultaneously

🔍 Smart Form Filling

Hybrid Validation: Rule-based + AI validation for accuracy
Context-Aware Help: Users can type "help" for field-specific guidance
Progress Tracking: Shows field completion (e.g., Question 5/50)
Date Intelligence: Validates dates based on field context (birth dates, expiry dates, etc.)

🔒 Security & Storage

AWS S3 Integration: Secure PDF storage with presigned URLs
MongoDB: Efficient conversation and form data management
Session Management: Persistent chat history with timestamps
CORS Protection: Configurable cross-origin security


🛠 Tech Stack
Backend

FastAPI - Modern, fast web framework
Python 3.9+ - Core language
Motor - Async MongoDB driver
OpenAI GPT-4o - AI chat and vision capabilities
PyMuPDF (fitz) - PDF processing and OCR
Boto3 - AWS S3 integration

Storage

MongoDB 7.0 - Document database
AWS S3 - PDF file storage

DevOps

Docker & Docker Compose - Containerization
Nginx (optional) - Reverse proxy
Mongo Express - Database management UI


🏗 Architecture
┌─────────────────┐
│   Frontend      │
│  (React/Next)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────┐
│      FastAPI Backend        │
│  ┌──────────────────────┐   │
│  │  Chat Engine         │   │
│  │  - State Management  │   │
│  │  - AI Orchestration  │   │
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │  Form Processing     │   │
│  │  - OCR (Vision API)  │   │
│  │  - Field Extraction  │   │
│  └──────────────────────┘   │
└─────────┬───────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌──────────┐
│MongoDB │  │   AWS S3 │
│        │  │  (PDFs)  │
└────────┘  └──────────┘

📦 Prerequisites

Docker & Docker Compose (recommended)
Python 3.9+ (for local development)
MongoDB 7.0+
AWS Account (for S3 storage)
OpenAI API Key (GPT-4o access)


🚀 Installation
Option 1: Docker Compose (Recommended)

Clone the repository

bashgit clone https://github.com/yourusername/immigration-chatbot.git
cd immigration-chatbot

Create .env file

bashcp .env.example .env

Configure environment variables (see Configuration)
Start the application

bashdocker-compose up -d

Verify deployment

bash# Check containers
docker-compose ps

# View logs
docker-compose logs -f app

Access the application


API: http://localhost:8000
API Docs: http://localhost:8000/docs
Mongo Express: http://localhost:8081

Option 2: Local Development

Install dependencies

bashpip install -r requirements.txt

Start MongoDB

bash# Using Docker
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  --name mongodb mongo:7.0

Run the application

bashuvicorn main:app --reload --host 0.0.0.0 --port 8000

⚙️ Configuration
Environment Variables (.env)
bash# MongoDB Configuration
MONGODB_URI=mongodb://admin:admin123@mongodb:27017
MONGODB_DB_NAME=immigration_chatbot

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# API Settings
CHAT_TEMPERATURE=0.7
CHAT_MAX_TOKENS=500
MIN_MESSAGES_FOR_MATCHING=6

# CORS Settings (Production)
CORS_ORIGINS=["http://yourfrontend.com","https://yourfrontend.com"]
AWS S3 Bucket Setup

Create an S3 bucket in AWS Console
Set bucket permissions:

Block Public Access: ON (for security)
Bucket Policy: Allow presigned URL access


Create IAM user with S3 permissions:

s3:PutObject
s3:GetObject
s3:DeleteObject
s3:ListBucket



MongoDB Setup
The application automatically creates required collections:

conversations - Chat history
forms - Extracted visa forms
pdf_documents - PDF metadata
summaries - Completed form summaries


🎮 Running the Application
Production Deployment
bash# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart app
Development Mode
bash# Start with live reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest tests/

# Format code
black app/

📚 API Documentation
Core Endpoints
1. Chat Endpoint
httpPOST /api/chat
Content-Type: application/json

{
  "session_id": "optional-session-id",
  "message": "I want to apply for a US tourist visa"
}
Response:
json{
  "session_id": "uuid-here",
  "message": "Perfect! I found the right form for you...",
  "state": "form_matched",
  "is_form_ready": true,
  "matched_form": {
    "form_id": "form-uuid",
    "title": "DS-160",
    "visa_type": "Tourist",
    "country": "USA"
  }
}
2. Upload Forms
httpPOST /api/upload-forms-bulk
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf, ...]
3. List All PDFs
httpGET /api/pdfs
4. Get Form PDF Link
httpGET /api/form-pdf/{session_id}
5. Get Chat History
httpGET /api/chat-history/{session_id}
6. Delete PDFs
httpPOST /api/delete-pdfs
Content-Type: application/json

{
  "pdf_doc_ids": ["id1", "id2"]
}
Interactive API Docs
Visit http://localhost:8000/docs for full Swagger UI documentation.

📁 Project Structure
immigration-chatbot/
│
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image config
├── docker-compose.yml           # Multi-container setup
├── .env                         # Environment variables
│
├── app/
│   ├── api/                     # API route handlers
│   │   ├── chat.py             # Chat conversation logic
│   │   ├── forms.py            # Form upload/management
│   │   └── session.py          # Session & history APIs
│   │
│   ├── core/                    # Core configuration
│   │   ├── config.py           # Settings & environment
│   │   ├── database.py         # MongoDB connection
│   │   ├── aws_config.py       # AWS S3 client
│   │   └── storage.py          # Data persistence layer
│   │
│   ├── models/                  # Data models
│   │   └── schemas.py          # Pydantic schemas
│   │
│   └── services/                # Business logic
│       ├── ai_service.py       # OpenAI integration
│       ├── ocr_service.py      # PDF extraction (Vision API)
│       ├── s3_service.py       # S3 operations
│       ├── form_matcher.py     # AI form matching
│       ├── conversation_manager.py  # State management
│       ├── question_generator.py    # Dynamic questions
│       └── answer_validator.py      # Hybrid validation
│
└── storage/                     # Local fallback storage

🎯 Key Features Explained
1. Conversational Flow States
The chatbot uses a finite state machine:
CHATTING → FORM_MATCHED → FILLING_FORM → COMPLETED
     ↓           ↓              ↓
     └───────────┴──────────────┘
          (can reset anytime)

CHATTING: Initial consultation (5-6 questions)
FORM_MATCHED: Form found, awaiting confirmation
FILLING_FORM: Active form filling with validation
COMPLETED: All fields filled, summary available

2. AI Form Matching
2-Tier Approach:

Tier 1 (Fast): Keyword matching for common terms
Tier 2 (Smart): AI semantic understanding for complex queries

Handles:

Single exact matches
Multiple form choices (user selects)
Missing information (asks follow-up questions)
Off-topic detection (polite redirection)

3. Hybrid Answer Validation
Rule-Based Validation (runs first):

Dates: Context-aware (birth dates, expiry dates, travel dates)
Email: RFC-compliant regex
Phone: International format support
Numbers: Range validation

AI Validation (fallback):

Text fields requiring judgment
Complex field types
Natural language answers

4. OCR with Vision API
Process:

PyMuPDF converts PDF pages to high-res images
OpenAI Vision API extracts field labels
AI determines field types (text, date, email, select)
Merges multi-page forms into single field list

Advantages:

No field limit (extracts all fields)
Works with handwritten or scanned forms
Handles complex layouts


🐛 Troubleshooting
Common Issues
1. CORS Errors
Problem: Frontend can't connect to API
Solution: Update CORS_ORIGINS in .env
bashCORS_ORIGINS='["http://localhost:3000","https://yourfrontend.com"]'
2. MongoDB Connection Failed
Problem: MongoServerError: Authentication failed
Solution: Check MongoDB credentials
bash# In docker-compose.yml
MONGODB_URL: mongodb://admin:admin123@mongodb:27017
3. S3 Upload Errors
Problem: Access Denied or Invalid credentials
Solution:

Verify AWS credentials in .env
Check IAM user permissions
Ensure bucket exists and is in correct region

4. OpenAI API Errors
Problem: Rate limit exceeded or Invalid API key
Solution:

Verify API key is correct
Check OpenAI account usage limits
Reduce CHAT_TEMPERATURE for more consistent results

5. PDF Processing Fails
Problem: OCR extraction returns 0 fields
Solution:

Ensure PDF is not encrypted
Check file size (< 10MB recommended)
Verify OpenAI Vision API quota

Debug Mode
Enable detailed logging:
bash# In docker-compose.yml
environment:
  LOG_LEVEL: DEBUG

# View logs
docker-compose logs -f app | grep ERROR

🔒 Security Best Practices

Never commit .env file - Add to .gitignore
Use presigned URLs - S3 files remain private
Rotate API keys regularly
Enable MongoDB authentication in production
Use HTTPS for production deployments
Implement rate limiting (e.g., with Nginx)
Sanitize user inputs before AI processing
