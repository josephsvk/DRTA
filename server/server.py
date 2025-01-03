from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyotp

app = FastAPI()

# TOTP shared secret (toto by malo byť uložené bezpečne)
SHARED_SECRET = "JBSWY3DPEHPK3PXP"  # Zmeň na svoj tajný kľúč

class TOTPRequest(BaseModel):
    code: str

@app.post("/verify-totp")
async def verify_totp(request: TOTPRequest):
    totp = pyotp.TOTP(SHARED_SECRET)
    if totp.verify(request.code):
        return {"status": "valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
