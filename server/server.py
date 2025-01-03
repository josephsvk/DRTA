import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyotp

app = FastAPI()

# Načítanie tajného kľúča z prostredia
SHARED_SECRET = os.getenv("TOTP_SECRET")
if not SHARED_SECRET:
    raise ValueError("TOTP_SECRET environment variable not set")


class TOTPRequest(BaseModel):
    code: str

@app.post("/verify-totp")
async def verify_totp(request: TOTPRequest):
    totp = pyotp.TOTP(SHARED_SECRET)
    if totp.verify(request.code):
        return {"status": "valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
