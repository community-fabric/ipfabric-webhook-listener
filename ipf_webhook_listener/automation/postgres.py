import json
import logging
import os
from datetime import datetime
from urllib.parse import urljoin

from ipfabric import IPFClient
from pytz import UTC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from automation.models import Snapshot, Device, Errors, Site, Intent, Group, IntentMapping, IntentResult, Part, \
    EoL
from ..config import settings
from ..models import Event

logger = logging.getLogger()
IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)
COLORDICT = {0: 'green', 10: 'blue', 20: 'amber', 30: 'red', None: None}


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


def add_parts(session, parts, snapshot_id):
    for p in parts:
        part = Part(
            part_id=int(p.get('id')),
            snapshot_id=snapshot_id,
            serial_number=p.get('sn'),
            device_serial_number=p.get('deviceSn'),
            description=p.get('dscr'),
            hostname=p.get('hostname'),
            model=p.get('model'),
            platform=p.get('platform'),
            name=p.get('name'),
            vendor=p.get('vendor'),
            part_number=p.get('pid'),
            part_version_id=p.get('vid')
        )
        session.add(part)


def add_eol(session, eols, snapshot_id):
    for e in eols:
        eol = EoL(
            eol_id=int(e.get('id')),
            snapshot_id=snapshot_id,
            part_number=e.get('pid'),
            replacement=e.get('replacement'),
            vendor=e.get('vendor'),
            description=e.get('dscr'),
            url=e.get('url'),
            end_maintenance=datetime.fromtimestamp(e.get('endMaintenance') / 1000, UTC) if
            e.get('endMaintenance') else None,
            end_sale=datetime.fromtimestamp(e.get('endSale') / 1000, UTC) if e.get('endSale') else None,
            end_support=datetime.fromtimestamp(e.get('endSupport') / 1000, UTC) if e.get('endSupport') else None,
        )
        session.add(eol)


def intent_url(intent):
    options = '?options={"f":{"'
    check_url = dict(
        green=options + str(intent.column) + '":["color","eq","0"]}}' if intent.checks.green else None,
        blue=options + str(intent.column) + '":["color","eq","10"]}}' if intent.checks.green else None,
        amber=options + str(intent.column) + '":["color","eq","20"]}}' if intent.checks.green else None,
        red=options + str(intent.column) + '":["color","eq","30"]}}' if intent.checks.green else None,
    )
    if intent.default_color and check_url[COLORDICT[intent.default_color]] is None:
        check_url[COLORDICT[intent.default_color]] = options + str(intent.column) + \
                                                     '":["color","eq","' + str(intent.default_color) + '"]}}'
    return check_url


def add_intent(session, intents, snapshot_id):
    results = list()
    mappings = list()
    for i in intents:
        intent_db = (session.query(Intent).filter(Intent.intent_id == i.intent_id).one_or_none())
        web = urljoin(settings.ipf_url, i.web_endpoint)
        check_url = intent_url(i)
        intent = Intent(
            intent_id=int(i.intent_id),
            name=i.name,
            api_endpoint=urljoin(settings.ipf_url, 'api' + i.api_endpoint),
            web_endpoint=web,
            column=i.column,
            custom=i.custom,
            default_color=i.default_color,
            default_color_str=COLORDICT[i.default_color],
            description=i.descriptions.general,
            green_description=i.descriptions.checks.green,
            blue_description=i.descriptions.checks.blue,
            amber_description=i.descriptions.checks.amber,
            red_description=i.descriptions.checks.red,
            green_check=json.dumps(i.checks.green) if i.checks.green else None,
            blue_check=json.dumps(i.checks.blue) if i.checks.blue else None,
            amber_check=json.dumps(i.checks.amber) if i.checks.amber else None,
            red_check=json.dumps(i.checks.red) if i.checks.red else None,
            green_url=web + check_url['green'] if check_url['green'] else None,
            blue_url=web + check_url['blue'] if check_url['blue'] else None,
            amber_url=web + check_url['amber'] if check_url['amber'] else None,
            red_url=web + check_url['red'] if check_url['red'] else None
        )
        if intent_db is None:
            session.add(intent)
        else:
            intent.update(session)
        for g in i.groups:
            mappings.append(IntentMapping(group_id=int(g.group_id), intent_id=int(i.intent_id)))
        result = IntentResult(
            intent_id=int(i.intent_id),
            snapshot_id=snapshot_id,
            total=i.result.count,
            green=i.result.checks.green,
            blue=i.result.checks.blue,
            amber=i.result.checks.amber,
            red=i.result.checks.red,
        )
        results.append(result)
    session.flush()
    session.execute("TRUNCATE TABLE intent_mapping")
    for m in mappings:
        session.add(m)
    for r in results:
        session.add(r)


def add_group(session, groups):
    for g in groups:
        group_db = (session.query(Group).filter(Group.group_id == g.group_id).one_or_none())
        group = Group(
            group_id=int(g.group_id),
            name=g.name,
            custom=g.custom
        )
        if group_db is None:
            session.add(group)
        else:
            group.update(session)


def process_snapshot(event: Event):
    IPF.update()
    snapshot_id = event.snapshot.snapshot_id if not event.test else IPF.snapshots['$last'].snapshot_id
    os.environ['CRON_SNAPSHOT_ID'] = snapshot_id

    # This will set IPF.snapshot_id = '$last' during running webhook tests, or it will fail.
    IPF.snapshot_id = snapshot_id
    engine = create_engine(settings.postgres_con)

    Session = sessionmaker()
    Session.configure(bind=engine)
    with Session() as session:
        add_snapshot(session, IPF.snapshots[snapshot_id])
        session.commit()

    with Session() as session:
        add_errors(session, IPF.snapshots[snapshot_id])
        add_site(session, IPF.inventory.sites.all(snapshot_id=snapshot_id), snapshot_id)
        session.flush()
        add_device(session, IPF.inventory.devices.all(snapshot_id=snapshot_id), snapshot_id)
        session.flush()
        add_parts(session, IPF.inventory.pn.all(snapshot_id=snapshot_id), snapshot_id)
        session.flush()
        add_eol(session, IPF.fetch_all('tables/reports/eof/summary', snapshot_id=snapshot_id), snapshot_id)
        session.commit()


def process_intent(event: Event):
    os.unsetenv('CRON_SNAPSHOT_ID')
    snapshot_id = event.snapshot_id if not event.test else IPF.snapshots['$last'].snapshot_id

    engine = create_engine(settings.postgres_con)

    Session = sessionmaker()
    Session.configure(bind=engine)
    with Session() as session:
        IPF.intent.load_intent(snapshot_id=snapshot_id)
        add_group(session, IPF.intent.groups)
        session.flush()
        add_intent(session, IPF.intent.intent_checks, snapshot_id)
        session.commit()


def process_event(event: Event):
    if event.type == 'snapshot' and \
            (event.test or (event.action == 'discover' and event.status == 'completed' and event.requester == 'cron')):
        process_snapshot(event)
    elif event.type == 'intent-verification' and \
            (event.test or (event.status == 'completed' and event.requester == 'snapshot:discover' and
                            event.snapshot_id == os.getenv('CRON_SNAPSHOT_ID'))):
        process_intent(event)
