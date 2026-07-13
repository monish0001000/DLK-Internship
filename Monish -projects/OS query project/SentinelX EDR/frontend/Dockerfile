# ============================================
# SentinelX EDR - Frontend Dockerfile
# ============================================
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy application code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run development server (use nginx for production)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
