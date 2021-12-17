import logging
from urllib.parse import urljoin

import pymsteams
from ipfabric import IPFClient
from .notify import snapshot, SNAP_URL, IMAGE_URL, user_search

from ..config import settings
from ..models import Event

logger = logging.getLogger()

IPF = IPFClient(settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


def add_link(message: pymsteams.connectorcard, event: Event):
    if event.type == 'snapshot':
        title = 'Snapshot: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        link = snapshot(event)
        message.addLinkButton(link.text, link.url)

    else:
        title = 'Intent Verification: ' + event.action.capitalize() + ' - ' + event.status.capitalize()
        message.addLinkButton("Snapshot Management", urljoin(settings.ipf_url, SNAP_URL + event.snapshot_id))
    return title


def add_facts(section: pymsteams.cardsection, event: Event):
    user = user_search(IPF, event.requester)
    section.addFact("Requester", user)
    section.addFact("Time", event.timestamp.strftime("%c"))
    if event.snapshot:
        section.addFact("Snapshot ID", event.snapshot.id)
        if event.snapshot.clone_id:
            section.addFact("Cloned ID", event.snapshot.clone_id)
        if event.snapshot.name:
            section.addFact("Snapshot Name", event.snapshot.name)
    if event.snapshot_id:
        section.addFact("Snapshot ID", event.snapshot_id)
    if event.test:
        section.addFact("Test", "True")


def add_snapshot_facts(snapshot_id: str):
    section = pymsteams.cardsection()
    IPF.update()
    snap = IPF.snapshots[snapshot_id]
    section.addFact("Device Count", snap.count)
    section.addFact("Site Count", len(snap.sites))
    section.addFact("Start Time", snap.start.strftime("%c"))
    section.addFact("End Time", snap.end.strftime("%c"))
    section.addFact("Version", snap.version)
    for error in snap.errors:
        section.addFact(error.error_type, error.count)
    return section


def send_teams(event: Event):
    if not settings.ipf_alerts.check_event(event) or (event.test and not settings.ipf_test):
        return
    message = pymsteams.connectorcard(settings.teams_url)
    message.color("01214A")
    message.summary("IP Fabric Event")
    title = add_link(message, event)
    message.title(title)
    section = pymsteams.cardsection()
    section.activityImage(IMAGE_URL)
    add_facts(section, event)
    message.addSection(section)

    if event.type == 'snapshot' and event.status == 'completed' and event.action in ['discover', 'load'] and \
            not event.test:
        try:
            message.addSection(add_snapshot_facts(event.snapshot.id))
        except:
            section = pymsteams.cardsection()
            section.text('Error collecting data from IP Fabric, check token and connectivity.')
            message.addSection(section)
            logger.error('Could not retrieve Snapshot information.')
    message.send()
