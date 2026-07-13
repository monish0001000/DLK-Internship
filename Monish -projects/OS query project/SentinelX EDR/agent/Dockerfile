# ============================================
# SentinelX EDR - Agent Dockerfile
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Run agent in simulate mode by default
CMD ["python", "sentinelx_agent.py", "--mode", "simulate", "--url", "http://backend:8000", "--interval", "60"]
