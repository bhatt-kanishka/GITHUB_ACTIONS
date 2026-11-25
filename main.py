import logging
import time
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, Field

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("student-api")

# Initialize FastAPI application
app = FastAPI(
    title="Student API - FastAPI",
    description="Student Management API with Observability, Structured Logging, and Health Checks",
    version="1.0.0"
)

# Pydantic Schemas for validation
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Student's full name")
    course: str = Field(..., min_length=1, description="Course enrolled in")

class Student(StudentCreate):
    id: int = Field(..., description="Unique student ID")

# In-memory student store
students_db: List[dict] = [
    {"id": 1, "name": "Aarav", "course": "Backend Development"},
    {"id": 2, "name": "Diya", "course": "Backend Development"},
]

# Structured HTTP request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "method=%s path=%s status=500 duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

# Root endpoint
@app.get("/", tags=["General"])
def root():
    return {
        "application": "Student API",
        "framework": "FastAPI",
        "status": "running",
        "version": "1.0.0",
        "message": "Welcome to Student API with CI/CD and Containerization!"
    }

# Health check endpoint (for monitoring, Docker & Kubernetes probes)
@app.get("/health", tags=["Monitoring"])
def health():
    return {"status": "healthy"}

# List all students
@app.get("/students", response_model=List[Student], tags=["Students"])
def list_students():
    return students_db

# Get student by ID
@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
def get_student(student_id: int):
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    return student

# Create a new student
@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    new_id = max([s["id"] for s in students_db], default=0) + 1
    new_student = {"id": new_id, "name": student.name, "course": student.course}
    students_db.append(new_student)
    return new_student

# Delete a student
@app.delete("/students/{student_id}", tags=["Students"])
def delete_student(student_id: int):
    global students_db
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    students_db = [s for s in students_db if s["id"] != student_id]
    return {"message": f"Student with id {student_id} deleted successfully"}

# Maintained for CI/CD demonstration route
@app.get("/new", tags=["General"])
def new_route():
    return {
        "message": "Updated automatically using GitHub Actions!"
    }
