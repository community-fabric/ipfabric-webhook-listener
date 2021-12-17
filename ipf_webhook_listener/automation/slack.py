import logging
from urllib.parse import urljoin

from slack_sdk.webhook import WebhookClient
from ipfabric import IPFClient
from .notify import snapshot, SNAP_URL, IMAGE_URL, user_search

from ..config import settings
from ..models import Event

logger = logging.getLogger()

IPF = IPFClient(settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


FOOTER = {
    "type": "context",
    "elements": [
        {
            "type": "image",
            "image_url": IMAGE_URL,
            "alt_text": "IP Fabric"
        },
        {
            "type": "mrkdwn",
            "text": "*Automated IP Fabric Event*"
        }
    ]
}


def add_link(event: Event):
    actions = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Click Me",
                    "emoji": True
                },
                "value": "click_me_123",
                "url": "https://google.com",
                "action_id": "button-action"
            }
        ]
    }
    if event.type == 'snapshot':
        title = 'Snapshot: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        link = snapshot(event)
        actions['elements'][0]['text']['text'] = link.text
        actions['elements'][0]['url'] = link.url
    else:
        title = 'Intent Verification: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        actions['elements'][0]['text']['text'] = "Snapshot Management"
        actions['elements'][0]['url'] = urljoin(settings.ipf_url, SNAP_URL + event.snapshot_id)
    return title, actions


def add_facts(event: Event):
    text = ''
    user = user_search(IPF, event.requester)
    text += f"- Requester: {user}\n"
    text += f"- Time: {event.timestamp.strftime('%c')}\n"

    if event.snapshot:
        text += f"- Snapshot ID: {event.snapshot.snapshot_id}\n"
        if event.snapshot.clone_id:
            text += f"- Cloned ID: {event.snapshot.clone_id}\n"
        if event.snapshot.name:
            text += f"- Snapshot Name: {event.snapshot.name}\n"
    if event.snapshot_id:
        text += f"- Snapshot ID: {event.snapshot_id}\n"
    if event.test:
        text += "- Test: True\n"
    section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text.rstrip()
        }
    }
    return section


def add_snapshot_facts(snapshot_id: str):
    text = ''
    IPF.update()
    snap = IPF.snapshots[snapshot_id]
    text += f"- Device Count: {snap.count}\n"
    text += f"- Site Count: {len(snap.sites)}\n"
    text += f"- Start Time: {snap.start.strftime('%c')}\n"
    text += f"- End Time: {snap.end.strftime('%c')}\n"
    text += f"- Version: {snap.version}\n"
    for error in snap.errors:
        text += f"- {error.error_type}: {error.count}\n"

    section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text.rstrip()
        }
    }
    return section


def send_slack(event: Event):
    if not settings.ipf_alerts.check_event(event) or (event.test and not settings.ipf_test):
        return

    blocks = list()

    title, actions = add_link(event)
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": title,
            "emoji": True
        }
    })
    blocks.append(add_facts(event))
    blocks.append({"type": "divider"})

    if event.type == 'snapshot' and event.status == 'completed' and event.action in ['discover', 'load'] and \
            not event.test:
        try:
            blocks.append(add_snapshot_facts(event.snapshot.snapshot_id))
        except:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": 'Error collecting data from IP Fabric, check token and connectivity.'
                }
            })
            logger.error('Could not retrieve Snapshot information.')
        blocks.append({"type": "divider"})
    blocks.append(actions)
    blocks.append(FOOTER)
    webhook = WebhookClient(settings.slack_url)
    webhook.send(text=title, blocks=blocks)
