import logging
import os

import pantab
import tableauserverclient as TSC
from ipfabric import IPFClient
from pandas import json_normalize
from tableau_tools.tableau_documents import TableauFileManager
from tableau_tools.logger import Logger
from tableauhyperapi import TableName

from ..config import settings
from ..models import Event

logger = logging.getLogger()
IPF = IPFClient(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify)
DEVICES_TDSX = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'IPFabric-Devices.tdsx')
INTENT_TDSX = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'IPFabric-Intent.tdsx')
DEVICES_FILE = 'Devices.hyper'
INTENT_FILE = 'Intent.hyper'
TABLEAU_LOG = 'hyperd.log'


def swap_hyper(hyper_name, tdsx_name):
    """Uses tableau_tools to open a local .tdsx file and replace the hyperfile."""
    # Uses tableau_tools to replace the hyper file in the TDSX.
    local_tds = TableauFileManager.open(filename=tdsx_name, logger_obj=Logger(TABLEAU_LOG))
    filenames = local_tds.get_filenames_in_package()
    for filename in filenames:
        if filename.find('.hyper') != -1:
            logger.info("Overwritting Hyper in original TDSX.")
            local_tds.set_file_for_replacement(filename_in_package=filename, replacement_filname_on_disk=hyper_name)
            break

    tdsx_name_before_extension, tdsx_name_extension = os.path.splitext(tdsx_name)
    tdsx_updated_name = tdsx_name_before_extension + '_updated' + tdsx_name_extension
    local_tds.save_new_file(new_filename_no_extension=tdsx_updated_name)
    os.remove(tdsx_name)
    os.rename(tdsx_updated_name, tdsx_name)


def publish_to_server(tdsx_name):
    """Publishes updated, local .tdsx to Tableau, overwriting the original file."""

    # Creates the auth object based on the config file.
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=settings.tableau_token_name, personal_access_token=settings.tableau_token,
        site_id=settings.tableau_site
    )
    server = TSC.Server(settings.tableau_server)
    logger.info(f"Signing into to site: {settings.tableau_site}.")

    # Signs in and find the specified project.
    with server.auth.sign_in(tableau_auth):
        all_projects, pagination_item = server.projects.get()
        for project in TSC.Pager(server.projects):
            if project.name == settings.tableau_project:
                project_id = project.id
        if project_id is None:
            logger.error(f"Could not find project '{settings.tableau_project}'. Please update your configuration.")
            return
        logger.info(f"Publishing to {settings.tableau_project}.")

        # Publishes the data source.
        overwrite_true = TSC.Server.PublishMode.Overwrite
        datasource = TSC.DatasourceItem(project_id)
        datasource = server.datasources.publish(datasource, tdsx_name, overwrite_true)
        logger.info(f"Publishing of datasource complete.")


def intent_tables(snapshot_id):
    color = {0: 'green', 10: 'blue', 20: 'amber', 30: 'red'}
    intents = list()
    intent_groups = list()
    for intent in IPF.intent.get_intent_checks(snapshot_id):
        intents.append(dict(
            id=intent.intent_id,
            rule=intent.name,
            description=intent.descriptions.general,
            custom=intent.custom,
            default=color[intent.default_color] if intent.default_color else None,
            green=intent.result.checks.green,
            blue=intent.result.checks.blue,
            amber=intent.result.checks.amber,
            red=intent.result.checks.red,
            green_desc=intent.descriptions.checks.green if intent.descriptions.checks else None,
            blue_desc=intent.descriptions.checks.blue if intent.descriptions.checks else None,
            amber_desc=intent.descriptions.checks.amber if intent.descriptions.checks else None,
            red_desc=intent.descriptions.checks.red if intent.descriptions.checks else None
        ))
        for group in intent.groups:
            intent_groups.append(dict(intent_id=intent.intent_id, group_id=group.group_id))

    groups = list()
    for group in IPF.intent.get_groups():
        groups.append(dict(name=group.name, group_id=group.group_id))

    return groups, intent_groups, intents


def update_and_publish(dict_of_frames, hyper, tdsx):
    pantab.frames_to_hyper(dict_of_frames, hyper)
    swap_hyper(hyper, tdsx)
    os.remove(hyper)
    publish_to_server(tdsx)


def process_event(event: Event):
    if event.type != 'snapshot' or event.action != 'discover' or \
            event.status != 'completed' or 'cron' not in event.requester:
        return  # Only process scheduled discovery snapshots.
    IPF.update()

    # This will set IPF.snapshot_id = '$last' during running webhook tests, or it will fail.
    snapshot_id = event.snapshot.snapshot_id if not event.test else '$last'
    IPF.snapshot_id = snapshot_id
    groups, intent_groups, intents = intent_tables(snapshot_id)

    dict_of_frames = {
        TableName("ipfabric", "devices"): json_normalize(IPF.inventory.devices.all()),
        TableName("ipfabric", "pn"): json_normalize(IPF.inventory.pn.all()),
        TableName("ipfabric", "interfaces"): json_normalize(IPF.inventory.interfaces.all()),
        TableName("ipfabric", "eol"): json_normalize(IPF.fetch_all('tables/reports/eof/detail')),
    }
    update_and_publish(dict_of_frames, DEVICES_FILE, DEVICES_TDSX)

    dict_of_frames = {
        TableName("ipfabric", "groups"): json_normalize(groups),
        TableName("ipfabric", "intent_groups"): json_normalize(intent_groups),
        TableName("ipfabric", "intents"): json_normalize(intents),
    }
    pantab.frames_to_hyper(dict_of_frames, INTENT_FILE)
    update_and_publish(dict_of_frames, INTENT_FILE, INTENT_TDSX)

    os.remove(TABLEAU_LOG)
