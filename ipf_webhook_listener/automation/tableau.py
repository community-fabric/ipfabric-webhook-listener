import logging
import os

from ipfabric import IPFClient


from ..config import settings
from ..models import Event

logger = logging.getLogger()
IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


def process_snapshot(event: Event):
    snapshot_id = event.snapshot.snapshot_id if not event.test else '$last'
    os.environ['CRON_SNAPSHOT_ID'] = snapshot_id
    IPF.update()

    # This will set IPF.snapshot_id = '$last' during running webhook tests, or it will fail.
    IPF.snapshot_id = snapshot_id

def process_intent(event: Event):
    os.unsetenv('CRON_SNAPSHOT_ID')
    snapshot_id = event.snapshot_id if not event.test else '$last'


def process_event(event: Event):
    if event.type == 'snapshot' and event.action == 'discover' and \
            event.status == 'completed' and event.requester == 'cron':
        process_snapshot(event)
    elif event.type == 'intent-verification' and event.status == 'completed' \
            and event.requester == 'snapshot:discover' and event.snapshot_id == os.getenv('CRON_SNAPSHOT_ID'):
        process_intent(event)

    # try:
    #     os.remove(TABLEAU_LOG)
    # except FileNotFoundError:
    #     pass
