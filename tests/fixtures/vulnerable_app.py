"""Sample vulnerable FastAPI app for testing Antidote scanner."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/users")
def list_users():
    return [{"id": 1, "name": "Alice"}]


@app.post("/users")
def create_user():
    return {"id": 2, "name": "Bob"}


@app.get("/admin/dashboard")
@login_required
def admin_dashboard():
    return {"admin": True}
