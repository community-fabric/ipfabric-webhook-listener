import logging
import os

from ipfabric import IPFClient

from ..config import settings
from ..models import Event
from automation.models import Snapshot, Device, Errors, Site, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger()
IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)


def add_snapshot(session, snapshot):
    snap = Snapshot(
        snapshot_id=snapshot.snapshot_id,
        name=snapshot.name,
        start=snapshot.start,
        end=snapshot.end,
        version=snapshot.version,
        total_devices=snapshot.count,
        licensed_devices=snapshot.licensed_count,
        status=snapshot.status
    )
    session.add(snap)


def add_errors(session, snapshot):
    for err in snapshot.errors:
        error = Errors(
            snapshot_id=snapshot.snapshot_id,
            error_type=err.error_type,
            error_count=err.count
        )
        session.add(error)


def add_site(session, sites, snapshot_id):
    for site in sites:
        s = Site(
            site_key=int(site.get('siteKey')),
            snapshot_id=snapshot_id,
            site_name=site.get('siteName'),
            site_id=int(site.get('id')),
            site_uid=site.get('siteUid'),
            devices=site.get('devicesCount'),
            networks=site.get('networksCount'),
            routers=site.get('routersCount'),
            switches=site.get('switchesCount'),
            users=site.get('usersCount'),
            vlans=site.get('vlanCount'),
            stp_domains=site.get('stpDCount'),
            routing_domains=site.get('rDCount')
        )
        session.add(s)


def add_device(session, devices, snapshot_id):
    for dev in devices:
        device = Device(
            device_id=int(dev.get('id')),
            snapshot_id=snapshot_id,
            site_key=int(dev.get('siteKey')),
            device_type=dev.get('devType'),
            family=dev.get('family'),
            hostname=dev.get('hostname'),
            task_key=dev.get('taskKey'),
            login_ip=dev.get('loginIp'),
            login_type=dev.get('loginType'),
            mac=dev.get('mac'),
            total_memory=dev.get('memoryTotalBytes'),
            used_memory=dev.get('memoryUsedBytes'),
            memory_utilization=dev.get('memoryUtilization'),
            model=dev.get('model'),
            platform=dev.get('platform'),
            processor=dev.get('processor'),
            serial_number=dev.get('sn'),
            hw_serial_number=dev.get('snHw'),
            uptime=dev.get('uptime'),
            vendor=dev.get('vendor'),
            version=dev.get('version'),
            reload=dev.get('reload'),
            config_reg=dev.get('configReg'),
        )
        session.add(device)


def process_snapshot(event: Event):
    IPF.update()
    snapshot_id = event.snapshot.snapshot_id if not event.test else IPF.snapshots['$last'].snapshot_id
    os.environ['CRON_SNAPSHOT_ID'] = snapshot_id

    # This will set IPF.snapshot_id = '$last' during running webhook tests, or it will fail.
    IPF.snapshot_id = snapshot_id
    engine = create_engine('postgresql://' + settings.postgres_user + ':' + settings.postgres_pass + '@' +
                           settings.postgres_host + ':' + str(settings.postgres_port) + '/' + settings.postgres_db)

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    with Session() as session:
        add_snapshot(session, IPF.snapshots[snapshot_id])
        session.commit()

    with Session() as session:
        add_errors(session, IPF.snapshots[snapshot_id])
        add_site(session, IPF.inventory.sites.all(), snapshot_id)
        session.flush()
        add_device(session, IPF.inventory.devices.all(), snapshot_id)
        session.commit()


def process_intent(event: Event):
    os.unsetenv('CRON_SNAPSHOT_ID')
    snapshot_id = event.snapshot_id if not event.test else IPF.snapshots['$last'].snapshot_id


def process_event(event: Event):
    if event.type == 'snapshot' and event.action == 'discover' and \
            event.status == 'completed' and event.requester == 'cron':
        process_snapshot(event)
    elif event.type == 'intent-verification' and event.status == 'completed' \
            and event.requester == 'snapshot:discover' and event.snapshot_id == os.getenv('CRON_SNAPSHOT_ID'):
        process_intent(event)

    process_snapshot(event)

    # try:
    #     os.remove(TABLEAU_LOG)
    # except FileNotFoundError:
    #     pass
