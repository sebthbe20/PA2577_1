import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="token-service")

class TokenValidate(BaseModel):
    token: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/validate")
def validate_token(payload: TokenValidate):
    if payload.token != os.environ["TOKEN"]:
        raise HTTPException(status_code=401, detail="invalid token")
    return {"status": "ok"}

if __name__ == "__main__":
    pass