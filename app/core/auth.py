from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY_NAME = "x-api-key"
API_KEY_VALUE = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY_VALUE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )