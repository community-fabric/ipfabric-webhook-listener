from models import Event
from ipfabric import IPFClient
from config import settings

IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


def process_event(event: Event):
    if event.type != 'snapshot' or event.action != 'discover' or event.status != 'completed':
        return
    IPF.update()
    IPF.snapshot_id = event.snapshot.id
