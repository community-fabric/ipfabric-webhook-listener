from urllib.parse import urljoin

from pydantic.dataclasses import dataclass

from ..config import settings
from ..models import Event
from ipfabric import IPFClient
from ipfabric.settings import UserMgmt
import re


SNAP_URL = 'snapshot-management/'
IMAGE_URL = 'https://ipfabric.atlassian.net/wiki/download/attachments/13369347/ND?version=1&amp;' \
            'modificationDate=1527757876293&amp;cacheVersion=1&amp;api=v2'
JOB_REGEX = re.compile(r"/home/autoboss/files/snapshotDownload-(\d*)\.tar")


@dataclass
class Link:
    text: str
    url: str


def snapshot(event: Event):
    if event.status == 'completed':
        if event.action == 'clone':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.clone_id)
            return Link('Snapshot Cloned', url)
        elif event.action == 'download':
            job = JOB_REGEX.match(event.snapshot.file)
            url = urljoin(settings.ipf_url, 'api/v1/jobs/' + job.group(1) + '/download')
            return Link('Download Snapshot', url)
        elif event.action == 'load':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Snapshot Loaded', url)
        elif event.action == 'unload':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Snapshot Unloaded', url)
        elif event.action == 'delete':
            url = urljoin(settings.ipf_url, SNAP_URL)
            return Link('Snapshot Deleted', url)
        elif event.action == 'discover':
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
            return Link('Discovery Completed', url)
    else:
        if event.snapshot and event.snapshot.id:
            url = urljoin(settings.ipf_url, SNAP_URL + event.snapshot.id)
        else:
            url = urljoin(settings.ipf_url, SNAP_URL)
        return Link('Snapshot Management', url)


def user_search(ipf: IPFClient, user: str):
    if 'user:' in user:
        user_id = user.split(':')[1]
        try:
            users = UserMgmt(ipf)
            return users.get_user_by_id(user_id).username
        except:
            pass
    return user
