import pantab
from ipfabric import IPFClient
from pandas import json_normalize
from tableauhyperapi import TableName

from ..config import settings
from ..models import Event

IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


def process_event(event: Event):
    if event.type != 'snapshot' or event.action != 'discover' or event.status != 'completed':
        return
    IPF.update()

    # Set IPF.snapshot_id = '$last' during running webhook tests or this will fail.
    IPF.snapshot_id = event.snapshot.snapshot_id
    filename = 'IPFabric-' + IPF.snapshots[IPF.snapshot_id].end.strftime("%Y%m%d-%H%M%S") + '.hyper'
    devices = IPF.inventory.devices.all()

    # Single table hyper. Can be directly published to server using Tableau Server Client library for Python
    pantab.frame_to_hyper(json_normalize(devices), filename, table=TableName("ipfabric", "devices"))

    """
    # Multi-Table hyper file. Requires more processing to publish to Tableau.  See README
    dict_of_frames = {
        TableName("ipfabric", "devices"): json_normalize(devices),
        TableName("ipfabric", "eol"): json_normalize(IPF.fetch_all('tables/reports/eof/detail')),
    }
    pantab.frames_to_hyper(dict_of_frames, filename)
    """
