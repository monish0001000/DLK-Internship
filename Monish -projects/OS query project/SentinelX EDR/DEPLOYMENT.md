# 🚀 Deployment Guide

This guide covers deploying SentinelX EDR for development, testing, and production environments.

## 🐳 Docker Deployment (Recommended)

The easiest way to run the entire stack (Frontend, Backend, Database) is via Docker Compose.

### Requirements
- Docker
- Docker Compose

### Steps
1. Clone the repository.
2. Copy the example environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```
3. Update the `.env` file with your secure `SECRET_KEY` and any AI API keys.
4. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```
5. Access the application:
   - **Frontend Dashboard**: `http://localhost:5173`
   - **Backend API Docs**: `http://localhost:8000/docs`

---

## 💻 Local Development

To run the application locally without Docker for active development:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🏭 Production Considerations

Before deploying SentinelX to a production network, ensure the following:

1. **Database**: Swap the local SQLite database for a robust **PostgreSQL** instance. Update `DATABASE_URL` in your `.env`.
2. **Reverse Proxy**: Place the application behind an Nginx or Traefik reverse proxy.
3. **SSL/TLS**: All OSQuery traffic and UI traffic *must* be secured via HTTPS (e.g., using Let's Encrypt).
4. **Secret Keys**: Generate a strong cryptographic key for `SECRET_KEY` (e.g., using `openssl rand -hex 32`). Do not use the default key.
5. **Firewall**: Restrict access to port 8000 (Backend API) to only your OSQuery fleet IPs and your frontend servers.
