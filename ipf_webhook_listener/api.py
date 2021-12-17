import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import RedirectResponse, Response

from .config import settings
from .models import Event
from .automation.teams import send_teams
from .automation.slack import send_slack

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
        if settings.teams_url:
            bg_tasks.add_task(send_teams, event)
        if settings.slack_url:
            bg_tasks.add_task(send_slack, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
