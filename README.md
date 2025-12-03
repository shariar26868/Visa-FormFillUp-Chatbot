<<<<<<< HEAD
# 🌍 Immigration Chatbot - AI-Powered Visa Application Assistant

An intelligent conversational AI system that helps users find, match, and fill visa application forms through natural language interactions. Built with FastAPI, OpenAI GPT-4, MongoDB, and AWS S3.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Key Features Explained](#-key-features-explained)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 Intelligent Conversational Flow
- **Natural Language Processing**: Understands user intent through casual conversation
- **Smart Form Matching**: AI-powered form recommendation based on 5-6 questions
- **Multi-State Management**: Handles complex conversation flows (chatting → matched → filling → completed)
- **Off-Topic Detection**: Politely redirects non-visa queries with 2-tier validation

### 📄 Advanced Form Processing
- **Unlimited Field Extraction**: OCR with PyMuPDF + OpenAI Vision API
- **Multi-Page Support**: Processes all pages of visa forms automatically
- **Intelligent Metadata Extraction**: Auto-detects visa type, country, and purpose
- **Bulk Upload**: Process multiple PDFs simultaneously with detailed progress

### 🔍 Smart Form Filling
- **Hybrid Validation**: Rule-based + AI validation for maximum accuracy
- **Context-Aware Help**: Users can type "help" anytime for field-specific guidance
- **Progress Tracking**: Shows field completion (e.g., Question 5/50)
- **Date Intelligence**: Context-aware validation (birth dates, expiry dates, travel dates)

### 🔒 Security & Storage
- **AWS S3 Integration**: Secure PDF storage with presigned URLs (2-hour validity)
- **MongoDB**: Efficient conversation and form data management with async operations
- **Session Management**: Persistent chat history with timestamps
- **CORS Protection**: Configurable cross-origin security

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **Python 3.9+** - Core programming language
- **Motor** - Async MongoDB driver for Python
- **OpenAI GPT-4o** - AI chat and vision capabilities
- **PyMuPDF (fitz)** - PDF processing and image extraction
- **Boto3** - AWS SDK for S3 integration
- **Pydantic** - Data validation using Python type hints

### Storage
- **MongoDB 7.0** - NoSQL document database
- **AWS S3** - Object storage for PDF files

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** (optional) - Reverse proxy and load balancer
- **Mongo Express** - Web-based MongoDB admin interface

---

## 🏗 Architecture
```
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
```

**Flow Diagram:**
```
User Question → AI Chat → Form Matching → Form Filling → Validation → Completion
                   ↓
              PDF Upload → OCR → Field Extraction → MongoDB Storage
                              ↓
                          AWS S3 Storage (Presigned URLs)
```

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** v20.10+ (recommended)
- **Python 3.9+** (for local development)
- **MongoDB 7.0+** (or use Docker)
- **AWS Account** with S3 access
- **OpenAI API Key** with GPT-4o access

---

## 🚀 Installation

### Option 1: Docker Compose (Recommended for Production)

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/immigration-chatbot.git
cd immigration-chatbot
```

**2. Create environment file**
```bash
cp .env.example .env
# Edit .env with your credentials (see Configuration section)
nano .env
```

**3. Build and start containers**
```bash
docker-compose up -d --build
```

**4. Verify deployment**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f app

# Check health endpoint
curl http://localhost:8000/health
```

**5. Access the services**
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Mongo Express**: http://localhost:8081 (admin/admin123)

### Option 2: Local Development

**1. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Start MongoDB (using Docker)**
```bash
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  --name mongodb mongo:7.0
```

**4. Create .env file**
```bash
cp .env.example .env
# Configure your environment variables
```
=======
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
>>>>>>> 2e9b9c08feea5e7b5de273c14ff9c9b3ddc81e38

**5. Run the application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**6. Access the application**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## ⚙️ Configuration

### Environment Variables (`.env`)

Create a `.env` file in the root directory with the following:
```bash
# ========================================
# MongoDB Configuration
# ========================================
MONGODB_URI=mongodb://admin:admin123@mongodb:27017
MONGODB_DB_NAME=immigration_chatbot

# ========================================
# AWS S3 Configuration
# ========================================
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# ========================================
# OpenAI Configuration
# ========================================
OPENAI_API_KEY=sk-your-openai-api-key-here

# ========================================
# Application Settings
# ========================================
CHAT_TEMPERATURE=0.7
CHAT_MAX_TOKENS=500
MIN_MESSAGES_FOR_MATCHING=6

# OCR Settings
IMAGE_ZOOM=2.0
MAX_PAGES_TO_PROCESS=10
OCR_MAX_TOKENS=4000

# ========================================
# CORS Settings (Production)
# ========================================
CORS_ORIGINS=["http://167.172.126.196:3031","https://immigrationai.app"]

# For local development:
# CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### AWS S3 Bucket Setup

**1. Create S3 Bucket**
```bash
# Using AWS CLI
aws s3 mb s3://your-immigration-chatbot-bucket --region us-east-1
```

**2. Configure Bucket Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {
        "StringEquals": {
          "aws:UserAgent": "presigned-url-access"
        }
      }
    }
  ]
}
```

**3. Create IAM User with Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### MongoDB Collections

The application automatically creates these collections:

| Collection | Purpose | Indexes |
|------------|---------|---------|
| `conversations` | Chat history and session state | `session_id` |
| `forms` | Extracted visa forms | `form_id` |
| `pdf_documents` | PDF metadata and S3 keys | `_id` |
| `summaries` | Completed form summaries | `session_id` |

---

## 🎮 Running the Application

### Production Deployment
```bash
# Start all services
docker-compose up -d

# View real-time logs
docker-compose logs -f app

# Check container status
docker-compose ps

# Restart a specific service
docker-compose restart app

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

### Development Mode
```bash
# Start with live reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with debug logging
uvicorn main:app --reload --log-level debug

# Run tests (if available)
pytest tests/ -v

# Format code
black app/ --line-length 100

# Lint code
flake8 app/
```

### Docker Commands
```bash
# View logs for specific service
docker-compose logs -f mongodb

# Execute commands inside container
docker-compose exec app bash

# Rebuild after code changes
docker-compose up -d --build

# View resource usage
docker stats
```

---

## 📚 API Documentation

### Base URL
```
Production: https://immigrationai.app/api
Development: http://localhost:8000/api
```

### Authentication
Currently, no authentication is required. **TODO**: Implement JWT tokens for production.

---

### Core Endpoints

#### 1. **Chat Endpoint**
Start or continue a conversation with the chatbot.
```http
POST /api/chat
Content-Type: application/json

{
  "session_id": "optional-uuid-here",
  "message": "I want to apply for a US tourist visa"
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Perfect! I found the right form for you...",
  "state": "form_matched",
  "is_form_ready": true,
  "matched_form": {
    "form_id": "abc123",
    "title": "DS-160 - US Tourist Visa",
    "visa_type": "Tourist",
    "country": "USA",
    "total_fields": 48
  }
}
```

**States:**
- `chatting` - Initial consultation
- `form_matched` - Form found, awaiting confirmation
- `filling_form` - Active form filling
- `completed` - All fields filled

---

#### 2. **Upload Forms (Bulk)**
Upload multiple PDF visa forms for OCR processing.
```http
POST /api/upload-forms-bulk
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf, file3.pdf]
```

**Response:**
```json
{
  "total_files": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "filename": "ds160.pdf",
      "success": true,
      "form_id": "abc123",
      "extracted_fields": 48
    },
    {
      "filename": "invalid.pdf",
      "success": false,
      "error": "Failed to extract fields"
    }
  ]
}
```

---

#### 3. **List All Forms**
Get all uploaded and processed forms.
```http
GET /api/forms
```

**Response:**
```json
{
  "forms": [
    {
      "form_id": "abc123",
      "title": "DS-160",
      "visa_type": "Tourist",
      "country": "USA",
      "total_fields": 48,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1,
  "status": "success"
}
```

---

#### 4. **List All PDFs**
Get all uploaded PDFs with presigned download URLs.
```http
GET /api/pdfs
```

**Response:**
```json
{
  "success": true,
  "total_pdfs": 5,
  "pdfs": [
    {
      "pdf_doc_id": "507f1f77bcf86cd799439011",
      "filename": "ds160.pdf",
      "s3_key": "uploads/20240115_abc123_ds160.pdf",
      "s3_url": "https://bucket.s3.amazonaws.com/...?X-Amz-Signature=...",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "form_id": "abc123",
      "form_title": "DS-160"
    }
  ]
}
```

---

#### 5. **Get Form PDF Link**
Get presigned URL for matched form's PDF.
```http
GET /api/form-pdf/{session_id}
```

**Response:**
```json
{
  "success": true,
  "form_id": "abc123",
  "title": "DS-160",
  "visa_type": "Tourist",
  "country": "USA",
  "pdf_url": "https://bucket.s3.amazonaws.com/...?X-Amz-Signature=...",
  "s3_key": "uploads/20240115_abc123_ds160.pdf",
  "filename": "ds160.pdf",
  "message": "PDF link retrieved successfully (valid for 2 hours)"
}
```

---

#### 6. **Get Chat History**
Retrieve full conversation history for a session.
```http
GET /api/chat-history/{session_id}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "filling_form",
  "total_messages": 12,
  "history": [
    {
      "role": "user",
      "content": "I want to visit USA",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Great! What's the purpose of your visit?",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "created_at": "2024-01-15T10:29:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

#### 7. **Clear Chat History**
Reset a session to start over.
```http
DELETE /api/chat-history/{session_id}
```

**Response:**
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Chat history cleared successfully"
}
```

---

#### 8. **Delete PDFs (Bulk)**
Delete multiple PDFs and their associated forms.
```http
POST /api/delete-pdfs
Content-Type: application/json

{
  "pdf_doc_ids": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
}
```

**Response:**
```json
{
  "success": true,
  "deleted_count": 2,
  "failed_count": 0,
  "details": [
    {
      "pdf_doc_id": "507f1f77bcf86cd799439011",
      "filename": "ds160.pdf",
      "success": true,
      "deleted_form": true,
      "message": "Deleted successfully"
    }
  ],
  "message": "Successfully deleted 2 PDF(s)"
}
```

---

#### 9. **Get Session Summary**
Get completed form summary with all answers.
```http
GET /api/summary/{session_id}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "form_title": "DS-160",
  "visa_type": "Tourist",
  "country": "USA",
  "personal_info": {},
  "answers": {
    "1": {
      "label": "Full Name",
      "answer": "John Doe",
      "field_type": "text"
    }
  },
  "completion_status": "completed"
}
```

---

### Interactive API Documentation

FastAPI provides built-in interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📁 Project Structure
```
immigration-chatbot/
│
<<<<<<< HEAD
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker container configuration
├── docker-compose.yml               # Multi-container orchestration
├── .env                            # Environment variables (not in git)
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore rules
│
├── app/
│   │
│   ├── api/                        # API route handlers
│   │   ├── __init__.py
│   │   ├── chat.py                 # Chat conversation logic
│   │   ├── forms.py                # Form upload/management
│   │   └── session.py              # Session & history APIs
│   │
│   ├── core/                       # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Settings & environment
│   │   ├── database.py             # MongoDB connection
│   │   ├── aws_config.py           # AWS S3 client
│   │   └── storage.py              # Data persistence layer
│   │
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic schemas
│   │
│   └── services/                   # Business logic
│       ├── __init__.py
│       ├── ai_service.py           # OpenAI integration
│       ├── ocr_service.py          # PDF extraction (Vision API)
│       ├── s3_service.py           # S3 operations
│       ├── form_matcher.py         # AI form matching
│       ├── conversation_manager.py # State management
│       ├── question_generator.py   # Dynamic questions
│       └── answer_validator.py     # Hybrid validation
│
├── storage/                        # Local fallback storage
│   └── (session files)
│
└── tests/                          # Test suite (TODO)
    ├── __init__.py
    ├── test_api.py
    ├── test_services.py
    └── test_integration.py
```

---

## 🎯 Key Features Explained

### 1. Conversational Flow State Machine

The chatbot uses a finite state machine with 5 states:
```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│CHATTING │────▶│ FORM_MATCHED │────▶│FILLING_FORM  │────▶│ COMPLETED │
└─────────┘     └──────────────┘     └──────────────┘     └───────────┘
     │                 │                      │                   │
     └─────────────────┴──────────────────────┴───────────────────┘
                    (reset to chatting)
```

**State Descriptions:**

| State | Description | User Actions |
|-------|-------------|--------------|
| **CHATTING** | Initial consultation (5-6 questions) | Answer questions about travel |
| **AWAITING_CONFIRMATION** | Multiple forms found | Choose preferred form |
| **FORM_MATCHED** | Single form matched | Confirm to start filling |
| **FILLING_FORM** | Active form filling with validation | Provide answers, ask for help |
| **COMPLETED** | All fields filled successfully | View summary, start new form |

---

### 2. AI Form Matching (2-Tier System)

**Tier 1: Fast Keyword Matching**
- Checks for visa-related keywords
- Instant response (< 100ms)
- 60+ keywords covering countries, visa types, travel terms

**Tier 2: AI Semantic Understanding**
- Uses GPT-4o for context analysis
- Handles ambiguous queries
- Confidence scoring (0-1)

**Example Flow:**
```
User: "I want to study in USA"
 ↓
Tier 1: Found keywords ["study", "usa"] → PASS
 ↓
AI Matching: "SINGLE match with 0.95 confidence"
 ↓
Result: US Student Visa (F-1)
```

---

### 3. Hybrid Answer Validation

**Rule-Based Validation** (runs first, < 50ms):
```python
# Date Fields
"12/09/2024" → ✅ Valid birth date
"2050-01-01" → ❌ Birth date in future

# Email Fields
"user@example.com" → ✅ Valid
"invalid.email" → ❌ Missing domain

# Phone Numbers
"+1-234-567-8900" → ✅ Valid (cleaned to digits)
"abc123" → ❌ Contains letters
```

**AI Validation** (fallback for complex fields):
- Text fields requiring judgment
- Multi-part answers
- Context-dependent validation

---

### 4. OCR with OpenAI Vision API

**Processing Pipeline:**
```
PDF File
  ↓
PyMuPDF (Convert to images at 2x zoom)
  ↓
OpenAI Vision API (Extract field labels)
  ↓
AI Analysis (Determine field types)
  ↓
Merge & Deduplicate (All pages combined)
  ↓
MongoDB Storage (Form ready for matching)
```

**Features:**
- **Unlimited fields**: No 50-field restriction
- **Multi-page support**: Processes entire form
- **Smart field typing**: Auto-detects text/date/email/select
- **Fallback extraction**: Manual regex parsing if AI fails

**Example Output:**
```json
{
  "form_id": "abc123",
  "title": "DS-160",
  "country": "USA",
  "visa_type": "Tourist",
  "fields": [
    {"id": "1", "label": "Full Name", "type": "text"},
    {"id": "2", "label": "Date of Birth", "type": "date"},
    {"id": "3", "label": "Email Address", "type": "email"}
  ],
  "total_fields_extracted": 48
}
```

---

### 5. Presigned URLs for Security

**Why Presigned URLs?**
- S3 bucket remains private (Block Public Access: ON)
- Temporary access (2 hours validity)
- No permanent public URLs
- Automatic expiration

**Generation:**
```python
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'bucket-name', 'Key': 's3-key'},
    ExpiresIn=7200  # 2 hours
)
```

**URL Format:**
```
https://bucket.s3.amazonaws.com/uploads/file.pdf?
  X-Amz-Algorithm=AWS4-HMAC-SHA256&
  X-Amz-Credential=...&
  X-Amz-Date=20240115T103000Z&
  X-Amz-Expires=7200&
  X-Amz-Signature=...&
  X-Amz-SignedHeaders=host
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. CORS Errors
**Symptom:** Browser console shows `CORS policy: No 'Access-Control-Allow-Origin'`

**Solution:**
```bash
# Update .env file
CORS_ORIGINS='["http://localhost:3000","https://yourfrontend.com"]'

# Restart Docker
docker-compose restart app
```

**Verify CORS settings:**
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/chat
```

---

#### 2. MongoDB Connection Failed
**Symptom:** `MongoServerError: Authentication failed`

**Solution:**
```bash
# Check MongoDB credentials in docker-compose.yml
environment:
  MONGODB_URL: mongodb://admin:admin123@mongodb:27017

# Reset MongoDB
docker-compose down -v  # CAUTION: Deletes all data
docker-compose up -d mongodb
```

**Test MongoDB connection:**
```bash
docker-compose exec mongodb mongosh \
  -u admin -p admin123 \
  --eval "db.adminCommand('ping')"
```

---

#### 3. S3 Upload/Download Errors
**Symptom:** `Access Denied` or `Invalid credentials`

**Diagnostics:**
```bash
# Test AWS credentials
aws s3 ls s3://your-bucket-name --profile your-profile

# Check IAM permissions
aws iam get-user-policy \
  --user-name your-iam-user \
  --policy-name S3AccessPolicy
```

**Solution:**
1. Verify AWS credentials in `.env`
2. Check IAM user has required permissions
3. Ensure S3 bucket exists and is in correct region
4. Test presigned URL generation:
```python
from app.services.s3_service import generate_presigned_url
url = generate_presigned_url("test-key")
print(url)
```

---

#### 4. OpenAI API Errors
**Symptom:** `Rate limit exceeded` or `Invalid API key`

**Solution:**
```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check usage limits
# Visit: https://platform.openai.com/account/usage

# Reduce temperature for consistency
CHAT_TEMPERATURE=0.5  # Lower = more deterministic
```

**Rate Limit Handling:**
```python
# Implement exponential backoff
import time
from openai import RateLimitError

for attempt in range(3):
    try:
        response = await call_openai_chat(...)
        break
    except RateLimitError:
        time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

---

#### 5. PDF Processing Fails
**Symptom:** `OCR extraction returns 0 fields`

**Diagnostics:**
```bash
# Check PDF file
docker-compose exec app python -c "
import fitz
doc = fitz.open('/tmp/test.pdf')
print(f'Pages: {len(doc)}')
print(f'Encrypted: {doc.is_encrypted}')
"
```

**Solution:**
1. Ensure PDF is not password-protected
2. Check file size (< 10MB recommended)
3. Verify OpenAI Vision API quota
4. Try with different PDF:
```bash
# Test with sample PDF
curl -X POST http://localhost:8000/api/upload-forms-bulk \
  -F "files=@sample.pdf"
```

---

#### 6. Docker Container Crashes
**Symptom:** Container exits with error code

**Diagnostics:**
```bash
# View container logs
docker-compose logs app

# Check container status
docker-compose ps

# Inspect container
docker inspect immigration-chatbot

# Check resource usage
docker stats
```

**Common Fixes:**
```bash
# Increase memory limit in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G

# Rebuild containers
docker-compose up -d --build --force-recreate
```

---

### Debug Mode

Enable detailed logging:
```bash
# Method 1: Environment variable
export LOG_LEVEL=DEBUG
uvicorn main:app --log-level debug

# Method 2: In docker-compose.yml
services:
  app:
    environment:
      LOG_LEVEL: DEBUG

# View specific service logs
docker-compose logs -f app | grep ERROR
docker-compose logs -f mongodb
```

**Python Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message here")
```

---

### Performance Monitoring
```bash
# Monitor API response times
docker-compose logs app | grep "Processing time"

# Check MongoDB queries
docker-compose exec mongodb mongosh -u admin -p admin123 \
  --eval "db.setProfilingLevel(2)"

# Monitor S3 operations
aws s3api list-objects-v2 --bucket your-bucket-name \
  --query 'Contents[].{Key:Key,Size:Size,Modified:LastModified}'
```

---

## 🔒 Security Best Practices

### 1. Environment Variables
```bash
# ✅ DO: Use .env file (in .gitignore)
OPENAI_API_KEY=sk-...

# ❌ DON'T: Hardcode in code
api_key = "sk-..."  # Never do this!
```

### 2. AWS S3 Security
```bash
# Enable bucket encryption
aws s3api put-bucket-encryption \
  --bucket your-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket your-bucket \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### 3. MongoDB Security
```bash
# Enable authentication (docker-compose.yml)
environment:
  MONGO_INITDB_ROOT_USERNAME: admin
  MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
=======
```
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
>>>>>>> 2e9b9c08feea5e7b5de273c14ff9c9b3ddc81e38
