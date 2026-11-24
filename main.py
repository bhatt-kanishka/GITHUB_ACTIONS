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

# Newly added route
@app.get("/new")
def new_route():
    return {
        "message": "Updated automatically using GitHub Actions!"
    }