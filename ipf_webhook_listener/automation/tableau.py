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
TDSX_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'IPFabric-Extract.tdsx')
HYPER_NAME = 'IPFabric.hyper'
TABLEAU_LOG = 'hyperd.log'


def swap_hyper(hyper_name):
    """Uses tableau_tools to open a local .tdsx file and replace the hyperfile."""
    # Uses tableau_tools to replace the hyper file in the TDSX.
    local_tds = TableauFileManager.open(filename=TDSX_NAME, logger_obj=Logger(TABLEAU_LOG))
    filenames = local_tds.get_filenames_in_package()
    for filename in filenames:
        if filename.find('.hyper') != -1:
            logger.info("Overwritting Hyper in original TDSX.")
            local_tds.set_file_for_replacement(filename_in_package=filename, replacement_filname_on_disk=hyper_name)
            break

    tdsx_name_before_extension, tdsx_name_extension = os.path.splitext(TDSX_NAME)
    tdsx_updated_name = tdsx_name_before_extension + '_updated' + tdsx_name_extension
    local_tds.save_new_file(new_filename_no_extension=tdsx_updated_name)
    os.remove(TDSX_NAME)
    os.rename(tdsx_updated_name, TDSX_NAME)


def publish_to_server():
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
        datasource = server.datasources.publish(datasource, TDSX_NAME, overwrite_true)
        logger.info(f"Publishing of datasource complete.")


def process_event(event: Event):
    if event.type != 'snapshot' or event.action != 'discover' or \
            event.status != 'completed' or 'cron' not in event.requester:
        return  # Only process scheduled discovery snapshots.
    IPF.update()

    # This will set IPF.snapshot_id = '$last' during running webhook tests, or it will fail.
    IPF.snapshot_id = event.snapshot.snapshot_id if not event.test else '$last'

    dict_of_frames = {
        TableName("ipfabric", "devices"): json_normalize(IPF.inventory.devices.all()),
        TableName("ipfabric", "pn"): json_normalize(IPF.inventory.pn.all()),
        TableName("ipfabric", "interfaces"): json_normalize(IPF.inventory.interfaces.all()),
        TableName("ipfabric", "eol"): json_normalize(IPF.fetch_all('tables/reports/eof/detail')),
    }
    pantab.frames_to_hyper(dict_of_frames, HYPER_NAME)
    swap_hyper(HYPER_NAME)
    os.remove(HYPER_NAME)
    publish_to_server()
    os.remove(TABLEAU_LOG)
