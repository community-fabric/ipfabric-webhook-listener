import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import RedirectResponse, Response

from config import settings
from models import Event
from time import sleep
from automation import process_event

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
async def redirect_root():
    return "/docs"


@app.get("/healthcheck", response_model=str)
async def root():
    return "Ok"


@app.post('/ipfabric')
async def webhook(event: Event, request: Request, bg_tasks: BackgroundTasks, x_ipf_signature: str = Header(None)):
    input_hmac = hmac.new(
        key=settings.ipf_secret.encode(),
        msg=await request.body(),
        digestmod="sha256"
    )
    if not hmac.compare_digest(input_hmac.hexdigest(), x_ipf_signature):
        raise HTTPException(status_code=400, detail="X-IPF-Signature does not match.")
    if not event.test or (settings.ipf_test and event.test):
        bg_tasks.add_task(process_event, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
