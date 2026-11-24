from fastapi import FastAPI

# Initialize FastAPI application
app = FastAPI()

# Home endpoint
@app.get("/")
def home():
    return {"message": "FastAPI is running"}

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}