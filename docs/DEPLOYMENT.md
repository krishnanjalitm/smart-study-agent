# Deployment Guide — Smart Study Generator Agent

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker Engine | 24.0+ | Container runtime |
| Docker Compose | v2+ | Service orchestration |
| IBM watsonx.ai | — | API key + Project ID |

---

## Step 1: Clone and Configure

```bash
git clone <your-repo> smart-study-agent
cd smart-study-agent
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:
```env
WATSONX_API_KEY=<your-ibm-api-key>
WATSONX_PROJECT_ID=<your-project-guid>
SECRET_KEY=<random-64-char-string>
JWT_SECRET_KEY=<another-random-64-char-string>
```

---

## Step 2: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build -d

# Check running containers
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

**Services started:**
| Service | Port | URL |
|---|---|---|
| React Frontend | 3000 | http://localhost:3000 |
| Flask Backend | 5000 | http://localhost:5000 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| Redis | 6379 | — |
| IBM Langflow | 7860 | http://localhost:7860 |

---

## Step 3: Import Langflow Flow

1. Open http://localhost:7860
2. Click **New Flow → Import**
3. Select `langflow/smart_study_flow.json`
4. Update node credentials (WATSONX_API_KEY, WATSONX_PROJECT_ID)
5. Click **Deploy**

---

## Step 4: Verify Health

```bash
# Backend health
curl http://localhost:5000/api/auth/me

# Register test user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"test1234"}'
```

---

## Manual Setup (Without Docker)

### Backend

```bash
# Install Tesseract (Ubuntu/Debian)
sudo apt-get install tesseract-ocr

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start Flask
python run.py
```

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:5000/api npm start
```

### MongoDB (Local)
```bash
# Ubuntu
sudo systemctl start mongod

# macOS
brew services start mongodb/brew/mongodb-community
```

---

## Cloud Deployment (IBM Cloud)

### Backend → IBM Code Engine
```bash
ibmcloud login
ibmcloud ce project create --name smart-study
ibmcloud ce app create \
  --name smart-study-backend \
  --image us.icr.io/smart-study/backend:latest \
  --port 5000 \
  --env-from-secret smart-study-secrets
```

### Frontend → IBM Cloud Object Storage + CDN
```bash
npm run build
# Upload build/ to IBM COS bucket with static website hosting
```

### MongoDB → MongoDB Atlas
Update `MONGO_URI` in secrets to your Atlas connection string.

---

## Environment-Specific Notes

### Production `.env`
```env
FLASK_ENV=production
# Use strong, randomly generated secrets
SECRET_KEY=<64+ char random string>
JWT_SECRET_KEY=<64+ char random string>
```

### Health Check Endpoint
Add to `run.py` for load balancer integration:
```python
@app.route("/health")
def health():
    return {"status": "ok"}, 200
```
