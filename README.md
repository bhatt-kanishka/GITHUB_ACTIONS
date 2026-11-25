# Student Management API — Docker, CI/CD, Monitoring & Scaling

A production-ready **FastAPI** backend application featuring **structured observability logging**, **health checks**, **Docker containerization**, **multi-instance horizontal scaling with Nginx**, and an **automated CI/CD pipeline with GitHub Actions**.

---

## 📌 Architecture & Features

```
Developer → Git Push → GitHub Actions CI/CD → Automated Tests (automationTesting.py)
                            ↓ (Pass)
                   Docker Build & Push → Docker Hub Repository
                            ↓
     Deploy: Multi-Instance Containers (Horizontal Scaling)
                            ↓
               [ Nginx Load Balancer (Port 8080) ]
                      ├── student-api-1 (Port 8001 -> 8000)
                      └── student-api-2 (Port 8002 -> 8000)
```

- **FastAPI Backend**: Clean, typed REST API for student management.
- **Observability & Structured Logging**: HTTP middleware recording timestamp, method, path, HTTP status, and precise latency (`duration_ms`).
- **Health Check Endpoint**: `/health` for container orchestration and uptime monitoring.
- **Automated Testing**: Comprehensive test suite in `automationTesting.py` covering all routes, status codes, and validation.
- **Containerization**: Optimized `Dockerfile` based on `python:3.12-slim` with built-in `HEALTHCHECK`.
- **Horizontal Scaling & Load Balancing**: `docker-compose.yml` and `nginx.conf` supporting round-robin load balancing across multiple API instances.
- **CI/CD Pipeline**: Multi-stage GitHub Actions workflow that executes automated testing before building and publishing images to Docker Hub.

---

## 📋 API Endpoints

| Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `GET` | `/` | Application metadata and status | `200 OK` |
| `GET` | `/health` | Health check endpoint for probes | `200 OK` |
| `GET` | `/students` | List all students | `200 OK` |
| `GET` | `/students/{id}` | Get a specific student by ID | `200 OK` / `404 Not Found` |
| `POST` | `/students` | Create a new student (JSON body) | `201 Created` / `422 Unprocessable` |
| `DELETE` | `/students/{id}` | Remove a student by ID | `200 OK` / `404 Not Found` |
| `GET` | `/new` | CI/CD automation verification route | `200 OK` |
| `GET` | `/docs` | Interactive Swagger API documentation | `200 OK` |

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.12+
- Docker and Docker Compose (optional for containerized runs)

### 2. Setup Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run FastAPI Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access API:
- Root: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Swagger Docs: `http://localhost:8000/docs`

---

## 🧪 Automated Testing

Run the automated test suite directly:

```bash
# In-process testing (no external server required)
python automationTesting.py

# Or test against a running server
python automationTesting.py --url http://localhost:8000
```

The test runner tests:
1. Root application metadata (`GET /`)
2. Health check endpoint status (`GET /health`)
3. CI/CD test endpoint (`GET /new`)
4. Student list retrieval (`GET /students`)
5. Single student lookup (`GET /students/1`)
6. Student creation with valid payload (`POST /students`)
7. Verification of newly created student (`GET /students/{id}`)
8. Student deletion (`DELETE /students/{id}`)
9. 404 response for non-existent IDs (`GET /students/99999`)
10. 422 response for malformed JSON (`POST /students`)

---

## 🐳 Docker Containerization

### Build Image Manually
```bash
docker build -t <your_docker_username>/fastapi-app:v0.1 .
```

### Run Image
```bash
docker run -d --name fastapi-app -p 8000:8000 <your_docker_username>/fastapi-app:v0.1
```

Verify:
```bash
curl http://localhost:8000/health
```

---

## ⚖️ Horizontal Scaling & Load Balancing (Docker Compose + Nginx)

### Run Single Service:
```bash
docker compose up student-api
```

### Run Multi-Instance Scaled Setup with Nginx Load Balancer:
```bash
docker compose --profile scaled up -d
```

This starts:
- `student-api-1` on port 8001
- `student-api-2` on port 8002
- `student-nginx-lb` on port 8080 (balancing requests across both instances)

Test the load balancer:
```bash
# Send 10 requests through load balancer
for i in {1..10}; do curl -s http://localhost:8080/health; echo ""; done
```

View the balanced logs across instances:
```bash
docker logs student-api-1
docker logs student-api-2
```

Stop containers:
```bash
docker compose --profile scaled down
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Workflow file: `.github/workflows/docker-publish.yml`

### Pipeline Stages:
1. **`test` Job**:
   - Runs on Ubuntu VM with Python 3.12.
   - Installs project dependencies.
   - Executes `python automationTesting.py`.
2. **`build-and-push` Job** *(Runs only after `test` passes)*:
   - Sets up Docker Buildx.
   - Authenticates against Docker Hub using GitHub Repository Secrets.
   - Builds image with multi-platform support.
   - Pushes image with tags `:latest` and `:v0.1`.

### Configuring GitHub Secrets:
In your GitHub repository:
1. Navigate to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Add:
   - `DOCKERHUB_USERNAME` (or `DOCKERUSERNAME`): Your Docker Hub username.
   - `DOCKERHUB_TOKEN` (or `DOCKERTOKEN`): Personal Access Token created from [Docker Hub Security Settings](https://hub.docker.com/settings/security).

---

## 📊 Observability & Structured Logging

The application middleware logs every HTTP request in structured format:

```
2026-11-25 12:53:57,147 INFO method=GET path=/health status=200 duration_ms=1.07
2026-11-25 12:53:57,171 INFO method=POST path=/students status=201 duration_ms=1.44
2026-11-25 12:53:57,181 INFO method=GET path=/students/99999 status=404 duration_ms=0.56
```

### Observability Checklist:
- **Logs**: Discrete event with method, path, status, latency.
- **Metrics**: Response time measurement with high-precision `time.perf_counter()`.
- **Health**: `/health` endpoint returning `{"status": "healthy"}`.
- **Safety**: No sensitive parameters, auth tokens, or PII logged.

---

## 🛠️ Troubleshooting Cheat Sheet

| Issue | Cause | Solution |
|---|---|---|
| `docker login` fails in Action | Missing or incorrect Docker Hub token | Re-generate Access Token on Docker Hub and verify secret `DOCKERHUB_TOKEN` |
| Tests fail in CI | Dependency mismatch or syntax error | Run `python automationTesting.py` locally and verify `requirements.txt` |
| Load Balancer returns 502 | Upstream container not responding | Check `docker ps` and `docker logs student-api-1` |
| Port already in use (8000/8080) | Another service is using the port | Stop conflicting process or change port mapping in `docker-compose.yml` |
