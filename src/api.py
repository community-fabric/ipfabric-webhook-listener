import hmac
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from .config import settings
from .models import Event

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
async def redirect_root():
    return "/docs"


@app.get("/healthcheck", response_model=str)
async def root():
    return "Ok"


@app.post('/ipfabric', status_code=status.HTTP_204_NO_CONTENT)
async def webhook(data: Event, request: Request, x_ipf_signature: str = Header(None)):
    input_hmac = hmac.new(
        key=settings.ipf_secret.encode(),
        msg=await request.body(),
        digestmod="sha256"
    )
    if not hmac.compare_digest(input_hmac.hexdigest(), x_ipf_signature):
        raise HTTPException(status_code=400, detail="X-IPF-Signature does not match.")
    print(data.__dict__)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
