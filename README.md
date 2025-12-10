# 🌍 Immigration Chatbot API

AI-powered visa application assistant that helps users find the right visa form and guides them through the application process.

## 📋 Features

- **Intelligent Conversation Flow**: Natural chat-based visa consultation
- **AI Form Matching**: Automatically matches users with appropriate visa forms
- **PDF Form Processing**: Extract fields from PDF forms using OpenAI Vision
- **Step-by-Step Guidance**: Interactive form filling with validation
- **Document Management**: Upload, store, and manage visa forms in AWS S3
- **MongoDB Storage**: Persistent conversation history and form data
- **RESTful API**: Clean API endpoints for frontend integration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- MongoDB
- AWS S3 Account
- OpenAI API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Visa-FormFillUp-Chatbot
```

2. **Create `.env` file**
```bash
# MongoDB
MONGODB_URI=mongodb://admin:admin123@mongodb:27017
MONGODB_DB_NAME=immigration_chatbot

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# CORS
CORS_ORIGINS=["https://ai.immigrationai.app","https://immigrationai.app"]
```

3. **Run with Docker Compose**
```bash
docker-compose up -d --build
```

4. **Check status**
```bash
docker-compose logs -f app
```

---

## 📡 API Endpoints

### Base URL
```
Production: https://ai.immigrationai.app
Local: http://localhost:8000
```

### 🗨️ Chat Endpoints

#### POST `/api/chat`
Start or continue a conversation with the chatbot.

**Request:**
```json
{
  "session_id": "optional-session-id",
  "message": "I want to apply for a US student visa"
}
```

**Response:**
```json
{
  "session_id": "generated-session-id",
  "message": "Great! Let's help you with the US student visa...",
  "state": "chatting",
  "is_form_ready": false,
  "matched_form": null
}
```

**States:**
- `chatting`: Initial consultation phase
- `form_matched`: Form found, waiting for confirmation
- `filling_form`: User is filling form fields
- `completed`: Form completed

---

### 📄 Form Management

#### POST `/api/upload-forms-bulk`
Upload multiple PDF visa forms for processing.

**Request:**
```bash
curl -X POST "https://ai.immigrationai.app/api/upload-forms-bulk" \
  -F "files=@form1.pdf" \
  -F "files=@form2.pdf"
```

**Response:**
```json
{
  "total_files": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "filename": "us-student-visa.pdf",
      "success": true,
      "form_id": "uuid-here",
      "extracted_fields": 45
    }
  ]
}
```

#### GET `/api/forms`
List all uploaded forms.

**Response:**
```json
{
  "forms": [
    {
      "form_id": "uuid",
      "title": "US Student Visa Application",
      "visa_type": "Student",
      "country": "USA",
      "total_fields": 45
    }
  ],
  "count": 1
}
```

#### GET `/api/pdfs`
Get list of all uploaded PDFs with presigned URLs.

**Response:**
```json
{
  "success": true,
  "total_pdfs": 3,
  "pdfs": [
    {
      "pdf_doc_id": "doc-id",
      "filename": "us-student-visa.pdf",
      "s3_url": "https://s3.amazonaws.com/...",
      "form_id": "form-uuid",
      "form_title": "US Student Visa"
    }
  ]
}
```

#### DELETE `/api/pdf/{pdf_doc_id}`
Delete a single PDF and its associated form.

#### POST `/api/delete-pdfs`
Delete multiple PDFs at once.

**Request:**
```json
{
  "pdf_doc_ids": ["id1", "id2", "id3"]
}
```

---

### 📊 Session Management

#### GET `/api/summary/{session_id}`
Get form completion summary.

**Response:**
```json
{
  "session_id": "session-id",
  "form_title": "US Student Visa Application",
  "visa_type": "Student",
  "country": "USA",
  "answers": {
    "field_1": {
      "label": "Full Name",
      "answer": "John Doe"
    }
  }
}
```

#### GET `/api/form-pdf/{session_id}`
Get PDF download link for matched form.

**Response:**
```json
{
  "success": true,
  "form_id": "uuid",
  "title": "US Student Visa",
  "pdf_url": "https://presigned-url...",
  "message": "PDF link retrieved (valid for 2 hours)"
}
```

#### GET `/api/chat-history/{session_id}`
Get complete chat history with timestamps.

**Response:**
```json
{
  "success": true,
  "session_id": "session-id",
  "state": "filling_form",
  "total_messages": 15,
  "history": [
    {
      "role": "user",
      "content": "I want a US visa",
      "timestamp": "2025-12-10T10:30:00Z"
    }
  ]
}
```

#### DELETE `/api/chat-history/{session_id}`
Clear/reset chat history for a session.

---

## 🏗️ Architecture

```
immigration-chatbot/
│
├── main.py                          # FastAPI application entry
│
├── app/
│   ├── api/
│   │   ├── chat.py                 # Chat conversation endpoints
│   │   ├── forms.py                # Form upload/management
│   │   └── session.py              # Session & history management
│   │
│   ├── core/
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # MongoDB connection
│   │   ├── aws_config.py           # AWS S3 configuration
│   │   └── storage.py              # Data persistence layer
│   │
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   │
│   └── services/
│       ├── ai_service.py           # OpenAI API integration
│       ├── s3_service.py           # AWS S3 operations
│       ├── ocr_service.py          # PDF extraction (Vision API)
│       ├── form_matcher.py         # AI form matching
│       ├── conversation_manager.py # State management
│       ├── question_generator.py   # Question generation
│       └── answer_validator.py     # Answer validation
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB connection string | Yes |
| `MONGODB_DB_NAME` | Database name | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes |
| `AWS_REGION` | AWS region | Yes |
| `S3_BUCKET_NAME` | S3 bucket name | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `CORS_ORIGINS` | Allowed origins (JSON array) | Yes |

### Optional Settings

```python
OPENAI_MODEL = "gpt-4o"
OPENAI_VISION_MODEL = "gpt-4o"
IMAGE_ZOOM = 2.0
MAX_PAGES_TO_PROCESS = 10
CHAT_TEMPERATURE = 0.7
CHAT_MAX_TOKENS = 500
MIN_MESSAGES_FOR_MATCHING = 6
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Restart specific service
docker-compose restart app
```

### Container Health Checks

```bash
# Check all containers
docker-compose ps

# Check app health
curl http://localhost:8000/health

# Access MongoDB (via Mongo Express)
http://localhost:8081
# Username: admin
# Password: admin123
```

---

## 🌐 Production Deployment

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name ai.immigrationai.app;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d ai.immigrationai.app
```

---

## 🧪 Testing

### Health Check

```bash
curl https://ai.immigrationai.app/health
```

### Test Chat

```bash
curl -X POST "https://ai.immigrationai.app/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to study in USA"
  }'
```

### Test Form Upload

```bash
curl -X POST "https://ai.immigrationai.app/api/upload-forms-bulk" \
  -F "files=@sample-visa-form.pdf"
```

---

## 📚 Usage Example

### Frontend Integration

```javascript
// Initialize conversation
const chatWithBot = async (message, sessionId = null) => {
  const response = await fetch('https://ai.immigrationai.app/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message
    })
  });
  
  const data = await response.json();
  return data;
};

// Start conversation
const result = await chatWithBot("I want a US student visa");
console.log(result.message);
console.log(result.session_id); // Save this for next messages
```

---

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` to version control
2. **API Keys**: Rotate keys regularly
3. **CORS**: Only allow trusted domains
4. **SSL**: Always use HTTPS in production
5. **S3 Presigned URLs**: Limited validity (2 hours default)
6. **MongoDB**: Use strong passwords and authentication

---

## 🐛 Troubleshooting

### Container keeps restarting

```bash
# Check logs
docker-compose logs app

# Common issues:
# - MongoDB connection failed
# - OpenAI API key invalid
# - AWS credentials incorrect
```

### MongoDB connection error

```bash
# Verify MongoDB is running
docker-compose ps mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

### S3 upload fails

```bash
# Verify AWS credentials
# Check S3 bucket permissions
# Ensure bucket exists in specified region
```

---

## 📊 Performance

- **Average Response Time**: < 2 seconds
- **Form Extraction**: 5-10 seconds per PDF
- **Concurrent Users**: Supports 100+ simultaneous connections
- **Database**: MongoDB with connection pooling
- **Caching**: S3 presigned URLs cached for 2 hours

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is proprietary software.

---

## 👥 Support

For issues or questions:
- Email: support@immigrationai.app
- Documentation: https://docs.immigrationai.app

---

## 🔄 Version History

### v1.0.0 (Current)
- ✅ AI-powered conversation flow
- ✅ PDF form extraction with Vision API
- ✅ MongoDB persistence
- ✅ AWS S3 integration
- ✅ RESTful API
- ✅ Docker deployment
- ✅ Chat history with timestamps
- ✅ Presigned URLs for secure downloads

---

**Built with ❤️ using FastAPI, OpenAI, MongoDB, and AWS**