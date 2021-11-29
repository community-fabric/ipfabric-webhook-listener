import hmac
import importlib
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from configurations import settings

app = FastAPI()


@app.get("/", response_class=RedirectResponse)
async def redirect_root():
    return "/docs"


@app.get("/healthcheck", response_model=str)
async def root():
    return "Ok"


class Snapshot(BaseModel):
    id: str
    name: Optional[str]


class Event(BaseModel):
    type: str
    action: str
    status: str
    test: Optional[bool] = False
    requester: str
    snapshot: Optional[Snapshot] = None
    timestamp: datetime


@app.post('/webhook', status_code=status.HTTP_204_NO_CONTENT)
async def webhook(data: Event, request: Request, x_ipf_signature: str = Header(None)):
    input_hmac = hmac.new(
        key=settings.ipf_secret.encode(),
        msg=await request.body(),
        digestmod="sha256"
    )
    if not hmac.compare_digest(input_hmac.hexdigest(), x_ipf_signature):
        raise HTTPException(status_code=400, detail="X-IPF-Signature does not match.")
    print(data.__dict__)


for plugin_name in settings.PLUGINS:
    # Import plugin module
    try:
        plugin = importlib.import_module('plugins.' + plugin_name)
    except ModuleNotFoundError as e:
        if getattr(e, 'name') == plugin_name:
            raise SyntaxError(
                "Unable to import plugin {}: Module not found. "
                "Check that the plugin module has been installed within the plugins directory".format(plugin_name)
            )
        raise e

    # Determine plugin config
    try:
        plugin_config = plugin.config
    except AttributeError:
        raise SyntaxError(
            "Plugin {} does not provide a 'config' variable. "
            "This should be defined in the plugin's __init__.py file ".format(plugin_name)
        )

    app.mount('/' + plugin_config.name, plugin.api.app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
