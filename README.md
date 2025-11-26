🤖 AI Immigration Chatbot
Intelligent visa form filling assistant with OCR and conversational AI.

✨ Features
💬 Natural conversation for visa requirements
📄 PDF form upload with OCR extraction
🧠 AI-powered form matching
✅ Smart answer validation
📊 Progress tracking
🔄 Multi-step form filling
🚀 Quick Start
1. Install Dependencies
bash
pip install -r requirements.txt
2. Setup Environment
Create .env file:

OPENAI_API_KEY=your-api-key-here
3. Run Server
bash
python main.py
Or with uvicorn:

bash
uvicorn main:app --reload
API will be available at: http://localhost:8000

📁 Project Structure
immigration-chatbot/
├── main.py                    # Entry point
├── app/
│   ├── api/                   # API endpoints
│   ├── core/                  # Config & storage
│   ├── models/                # Pydantic schemas
│   └── services/              # Business logic
└── data/                      # Data storage
🔄 Conversation Flow
Initial Chat - User describes their visa needs
Form Matching - AI matches best form (after 4-5 messages)
Form Filling - Step-by-step question answering
Validation - AI validates each answer
Completion - Generate summary
📝 API Endpoints
Chat
POST /api/chat - Send message
POST /api/start-form-filling - Begin form filling
POST /api/answer - Submit field answer
Forms
POST /api/upload-pdf - Upload single PDF
POST /api/upload-pdfs-batch - Upload multiple PDFs
GET /api/forms - List all forms
GET /api/forms/{form_id} - Get form details
DELETE /api/forms/{form_id} - Delete form
Session
GET /api/session/{session_id} - Get session status
GET /api/summary/{session_id} - Get completion summary
GET /api/stats - System statistics
🧪 Testing
bash
# Upload a form
curl -X POST http://localhost:8000/api/upload-pdf \
  -F "file=@visa_form.pdf"

# Start chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to visit USA for tourism"}'
📦 Data Storage
data/conversations/ - User sessions (JSON)
data/uploaded_pdfs/ - Uploaded forms
data/forms_db.json - Forms metadata
🛠 Tech Stack
FastAPI - Web framework
OpenAI GPT-4o - AI & OCR
PyMuPDF - PDF processing
Pydantic - Data validation
📄 License
MIT License

