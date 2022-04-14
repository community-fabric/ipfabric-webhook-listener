import logging
import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .pdfmaker import GeneratePDF
from .snapminer import MineSnapshot
from ..config import settings
from ..models import Event

logger = logging.getLogger()


def send_email(subject, pdf_data, file_name):
    mimemsg = MIMEMultipart()
    mimemsg['From'] = settings.mail_from
    mimemsg['To'] = settings.mail_to
    mimemsg['Subject'] = subject
    mimemsg.attach(MIMEText("Please see attached IP Fabric PDF Report.", 'plain'))

    mimefile = MIMEBase('application', 'octet-stream')
    mimefile.set_payload(pdf_data)
    encoders.encode_base64(mimefile)
    mimefile.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
    mimemsg.attach(mimefile)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port, context=context) as server:
        server.login(settings.email_user, settings.email_pass)
        server.sendmail(settings.mail_from, settings.mail_to, mimemsg.as_string())


def process_intent(timestamp):
    snapshot_id = os.getenv('CRON_SNAPSHOT_ID')
    logger.info("Getting IP Fabric Data")
    base_dataset = MineSnapshot(base_url=settings.ipf_url, token=settings.ipf_token, verify=settings.ipf_verify,
                                snapshot_id=snapshot_id)
    logger.info("Generating IP Fabric PDF Report")
    pdf_object = GeneratePDF()
    pdf_data = pdf_object.analysis_report(base_dataset)
    logger.info("Emailing IP Fabric PDF Report")
    send_email(f"IP Fabric Report - {timestamp.ctime()}", pdf_data, f"IPFabric-{timestamp.strftime('%m%d%Y-%H%M')}.pdf")


def process_event(event: Event):
    snapshot_id = event.snapshot.snapshot_id if not event.test else '$last'
    if event.type == 'snapshot' and event.action == 'discover' and \
            event.status == 'completed' and event.requester == 'cron':
        os.environ['CRON_SNAPSHOT_ID'] = snapshot_id
    elif event.type == 'intent-verification' and event.status == 'completed' \
            and ((event.requester == 'snapshot:discover' and event.snapshot_id == os.getenv('CRON_SNAPSHOT_ID')) or
                 event.test):
        process_intent(event.timestamp)
        os.unsetenv('CRON_SNAPSHOT_ID')
