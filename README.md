# AI Chatbot Assistant

A full-stack AI chatbot application built with FastAPI backend and React frontend, featuring machine learning capabilities and modern UI.

## Features

- 🤖 Intelligent chatbot with ML-powered responses
- 💬 Real-time chat interface with dark/light mode
- 📱 Responsive design with Tailwind CSS
- 🗄️ SQLite database for conversation persistence
- 🐳 Docker containerization
- 🧪 Comprehensive testing (pytest for backend, Vitest for frontend)
- 🔄 RESTful API with FastAPI
- ⚡ Vite for fast frontend development

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **TensorFlow** - Machine learning framework
- **SQLAlchemy** - Database ORM
- **NLTK** - Natural language processing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **SQLite** - Database (easily switchable to PostgreSQL)

## Project Structure

```
ai-chatbot-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database models
│   │   └── model/
│   │       ├── chatbot_engine.py # ML inference engine
│   │       └── train_model.py   # Model training script
│   ├── tests/
│   │   └── test_main.py         # Backend tests
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles
│   ├── tests/
│   │   └── App.test.jsx         # Frontend tests
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # Tailwind configuration
│   └── Dockerfile               # Frontend Docker config
├── data/
│   └── intents.json             # Training data
├── docker/
│   └── Dockerfile               # Backend Docker config
├── docker-compose.yml           # Multi-service setup
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-chatbot-assistant
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Train the ML model (optional)**
   ```bash
   cd backend
   python -m app.model.train_model
   cd ..
   ```

6. **Start the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start the frontend (in a new terminal)**
   ```bash
   cd frontend
   npm run dev
   ```

8. **Open your browser**
   Visit `http://localhost:5173` to interact with the chatbot.

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Send message to chatbot
  - Request: `{"user_message": "string"}`
  - Response: `{"bot_response": "string"}`
- `POST /train` - Train the ML model

## Testing

### Backend Tests
```bash
cd backend
pytest -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Deployment

### Environment Variables
Create a `.env` file with:
```
DATABASE_URL=sqlite:///./chatbot.db
DEBUG=False
```

### Production Deployment
- Use Docker Compose for containerized deployment
- Configure reverse proxy (nginx) for production
- Set up CI/CD pipeline with GitHub Actions
- Deploy to cloud platforms (Render, AWS, Vercel)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

##Preview
<img width="1904" height="1065" alt="image" src="https://github.com/user-attachments/assets/a7282936-d2dd-4a29-9514-42125357bede" />



## Acknowledgments

- Built with FastAPI, React, and TensorFlow
- UI inspired by modern chat applications
- ML model based on intent classification
