# Nymalay Clinic - Full Stack Application

A clinic website and management backend built with a statically exported Next.js frontend and FastAPI backend.

## Project Structure

```
nymalaya-fullstack/
├── backend/              # FastAPI backend
│   ├── app/              # Main application code
│   │   ├── auth.py       # Authentication
│   │   ├── config.py     # Configuration
│   │   ├── crud.py       # Database operations
│   │   ├── database.py   # Database setup
│   │   ├── main.py       # API endpoints
│   │   ├── models.py     # Database models
│   │   └── schemas.py    # Pydantic schemas
│   ├── clinic.db         # SQLite development database
│   ├── Dockerfile        # Backend container
│   ├── requirements.txt  # Production dependencies
│   ├── requirements-dev.txt # Development dependencies
│   ├── pytest.ini        # Test configuration
│   └── scripts/
│       └── seed_demo.py  # Demo data seeder
│   └── tests/            # Backend tests
├── frontend/             # Next.js frontend
│   ├── components/       # React components
│   │   └── sections/     # Page sections
│   ├── lib/              # Utility functions
│   ├── pages/            # Next.js pages
│   │   ├── _document.js  # Custom document (with favicon)
│   │   ├── _app.js       # Custom app
│   │   ├── index.js      # Home page
│   │   └── ...           # Other pages
│   ├── public/           # Static assets
│   │   └── images/       # Clinic images (logo, textures, photos)
│   ├── scripts/          # Development scripts
│   │   └── dev.mjs       # Next.js dev server script
│   ├── styles/           # CSS styles
│   ├── next.config.js    # Next.js configuration
│   ├── package.json      # Frontend dependencies
│   ├── tailwind.config.js # Tailwind CSS config
│   └── vitest.config.js  # Vitest testing config
├── docs/                 # Documentation
│   └── reference/        # Reference documents
│       └── Nymalay_Implementation.md
├── .github/              # GitHub workflows
│   └── workflows/
│       └── ci-cd.yml     # CI/CD pipeline
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Container orchestration
└── README.md             # This file
```

## Features

### Backend (FastAPI)
- RESTful API for clinic management
- Patient registration and management
- Appointment scheduling
- Doctor management
- Secure authentication (JWT-based)
- SQLite development database
- Comprehensive test suite
- Docker support

### Frontend (Next.js)
- Modern, responsive UI with Tailwind CSS
- Static HTML export for Cloudflare Pages
- Direct WhatsApp contact for consultation requests and clinic communication
- Clinic information display
- Nymalay branding with custom favicon
- Optimized asset loading

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.12+
- Docker (optional, for containerized deployment)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Configuration
Copy the example environment files:
```bash
cp backend/.env.example backend/.env
```

The public frontend needs no environment variables. Edit the backend `.env`
only for local backend development.

### Database Initialization
```bash
# From backend directory
python -m app.database  # Initializes the database
python scripts/seed_demo.py  # Seeds demo data (optional)
```

### Running the Application

#### Development Mode
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev  # Or: PORT=3000 npm run dev
```

#### Production Mode (Docker)
```bash
docker-compose up --build
```

The application will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Key Features Implemented

1. **Branding**: Nymalay logo appears as favicon in browser tab
2. **Direct contact**: Consultation requests and clinic communication go through WhatsApp
3. **Optimized Assets**: Extracted and optimized images from design prototype
4. **Responsive Design**: Mobile-friendly interface
5. **Secure Authentication**: JWT-based auth system
6. **RESTful API**: Well-documented endpoints
7. **Comprehensive Testing**: Backend test suite included
8. **Docker Ready**: Containerized deployment support
9. **Documentation**: Implementation details and deployment guide

## Development Guidelines

- Backend follows FastAPI best practices
- Frontend uses Next.js Pages Router and static export
- Styling with Tailwind CSS
- State management with React hooks
- Public frontend pages make no backend/API calls
- WhatsApp opens a direct chat without a prefilled message or form data
- Python type hints for backend

## License

MIT License - see LICENSE file for details.