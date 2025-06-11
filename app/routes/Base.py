from fastapi import APIRouter, Depends, HTTPException, status, Request

router = APIRouter()

@router.get("/")
def home(request: Request):
    return {
        "status": "ok",
        "api_version": "0.1.0-dev+local"
    }