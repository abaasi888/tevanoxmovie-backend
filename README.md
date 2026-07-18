🎬 TEVANOXMOVIE Backend API
https://img.shields.io/badge/FastAPI-0.139.0-009688?style=flat&logo=fastapi
https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python
https://img.shields.io/badge/MongoDB-6.0+-47A248?style=flat&logo=mongodb
https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat&logo=render

Complete backend API for the TEVANOXMOVIE platform - Movie Streaming, Music, Series, Shareholder Management, and Commission System.

📋 Table of Contents
Overview

Features

Tech Stack

Project Structure

Installation

Environment Variables

API Documentation

Database Schema

Deployment

Testing

Contributing

License

🎯 Overview
TEVANOXMOVIE Backend is a production-ready FastAPI application that powers the entire TEVANOXMOVIE ecosystem. It serves as the central API for:

Web Application - Shareholder Portal

Admin Dashboard - Management panel

Mobile Application - iOS/Android app

Sales Agent App - Agent commission tracking

✨ Features
🔐 Authentication & Authorization
JWT-based authentication

Role-based access control (Admin, User, Agent)

Password hashing with bcrypt

Email verification

Password reset flow

👤 User Management
User registration and login

Profile management

Referral system

User activity tracking

💰 Shareholder Management
Share purchase and tracking

Portfolio management

ROI calculations

Shareholder tier system (Bronze, Silver, Gold, Platinum)

Dividend distribution

📊 Financial Management
Dividend declarations and payments

Profit tracking and distribution

Transaction history

Commission calculations

🎬 Content Management
Movies, Music, and Series

Content metadata management

Streaming support

Genre and category management

Ratings and reviews

🤝 Agent System
Agent registration and tracking

Commission management

Referral tracking

Agent performance analytics

💳 Payment Integration
Paystack payment processing

Subscription management

Payment verification

Webhook handling

📱 Mobile Support
Optimized API for mobile clients

Offline content support

Push notification ready

🛠️ Tech Stack
Technology	Version	Purpose
FastAPI	0.139.0	Web framework
Python	3.11+	Programming language
MongoDB	6.0+	Database
Motor	3.7.1	Async MongoDB driver
PyMongo	4.17.0	MongoDB driver
JWT	-	Authentication
Bcrypt	5.0.0	Password hashing
Celery	5.6.3	Background tasks
Redis	8.0.1	Task queue
Boto3	1.43.48	S3/MinIO storage
Uvicorn	0.51.0	ASGI server
📁 Project Structure
text
tevanoxmovie-backend/
├── app/
│   ├── api/v1/              # API routes
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── shareholders.py  # Shareholder management
│   │   ├── dividends.py     # Dividend management
│   │   ├── movies.py        # Movie management
│   │   ├── music.py         # Music management
│   │   ├── series.py        # Series management
│   │   ├── agents.py        # Agent management
│   │   ├── payments.py      # Payment processing
│   │   ├── subscriptions.py # Subscription management
│   │   └── streaming.py     # Streaming endpoints
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # Security utilities
│   │   └── logging.py       # Logging configuration
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── shareholder.py
│   │   ├── dividend.py
│   │   ├── movie.py
│   │   └── ...
│   ├── schemas/             # Pydantic schemas
│   │   ├── user_schema.py
│   │   ├── shareholder_schema.py
│   │   └── ...
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── shareholder_service.py
│   │   ├── dividend_service.py
│   │   └── ...
│   ├── middleware/          # Custom middleware
│   │   └── auth.py          # Authentication middleware
│   ├── tasks/               # Celery tasks
│   │   ├── celery_app.py
│   │   └── commission_tasks.py
│   └── utils/               # Utility functions
│       ├── constants.py
│       └── helpers.py
├── tests/                   # Unit tests
│   ├── test_auth.py
│   └── test_movies.py
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── render.yaml              # Render deployment
├── .env.example             # Environment variables template
└── README.md               # This file
🚀 Installation
Prerequisites
Python 3.11+

MongoDB 6.0+

Redis (for Celery tasks)

Git

Local Setup
bash
# 1. Clone the repository
git clone https://github.com/abaasi888/tevanox.com.git
cd tevanox.com/apps/tevanoxmovie-backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment variables
cp .env.example .env

# 6. Edit .env with your configuration
nano .env

# 7. Start MongoDB (if running locally)
net start MongoDB
# or
mongod --dbpath C:\data\db

# 8. Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
🔐 Environment Variables
Create a .env file with the following variables:

env
# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=tevanoxmovie

# Security
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Domain
DOMAIN=tevanox.com
API_URL=http://localhost:8000
WEB_URL=http://localhost:3000
ADMIN_URL=http://localhost:3001
MOBILE_URL=http://localhost:3002
AGENT_URL=http://localhost:3003

# Storage (MinIO/S3)
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=tevanoxmovie

# Payment (Paystack)
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxx

# Commission Rates
TEVANOX_SHARE=0.60
NETWORK_TOTAL=0.40
LEVEL_1_COMMISSION=0.25
LEVEL_2_COMMISSION=0.10
LEVEL_3_COMMISSION=0.05
📚 API Documentation
Once the server is running, access the interactive API documentation:

Documentation	URL
Swagger UI	http://localhost:8000/api/docs
ReDoc	http://localhost:8000/api/redoc
Health Check	http://localhost:8000/health
Main API Endpoints
Method	Endpoint	Description
POST	/api/v1/auth/register	Register new user
POST	/api/v1/auth/login	Login user
GET	/api/v1/auth/me	Get current user
GET	/api/v1/users	List all users (admin)
GET	/api/v1/shareholders	List all shareholders (admin)
GET	/api/v1/shareholders/my	Get my shareholder info
POST	/api/v1/shareholders/purchase	Purchase shares
GET	/api/v1/dividends	List all dividends (admin)
GET	/api/v1/dividends/my	Get my dividends
POST	/api/v1/dividends/declare	Declare dividend (admin)
GET	/api/v1/movies	List all movies
GET	/api/v1/movies/{id}	Get movie by ID
GET	/api/v1/streaming/{id}	Stream content
GET	/api/v1/agents/my	Get agent info
GET	/api/v1/agents/commissions	Get agent commissions
POST	/api/v1/payments/initiate	Initiate payment
🚀 Deployment
Deploy to Render
Push code to GitHub:

bash
git add -A
git commit -m "Deploy to Render"
git push origin main
Connect to Render:

Go to https://render.com

Click "New +" → "Web Service"

Connect your GitHub repository

Select the backend directory

Configure:

Build Command: pip install -r requirements.txt

Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000

Add Environment Variables:

Add all variables from .env.example

Deploy!

Deploy using Docker
bash
# Build Docker image
docker build -t tevanoxmovie-backend .

# Run container
docker run -p 8000:8000 --env-file .env tevanoxmovie-backend
🧪 Testing
bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
This project is proprietary and confidential. Unauthorized copying, distribution, or use of this software is strictly prohibited.

📞 Contact
Domain: tevanox.com

Email: support@tevanox.com

GitHub: abaasi888

<p align="center"> <strong>Built with ❤️ for TEVANOXMOVIE</strong> </p>
🙏 Acknowledgments
FastAPI framework

MongoDB community

Render.com for hosting

All contributors

🎯 Quick Commands
bash
# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black .

# Lint code
flake8
