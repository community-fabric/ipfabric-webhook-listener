# IP Fabric Webhook Integration for Emailing a PDF Report

This creates a summary PDF report of a snapshot.  It requires both Snapshot and Intent webhooks.
Once a Scheduled snapshot is completed, this will create and email the report.
An example report is located at [IPFabric.pdf](IPFabric.pdf)

## Setup

### <a id="python-setup"></a> Python Setup
```shell
python3 -m pip install -U pip poetry
poetry install -E pdf
```
One time suggested config changes:
```shell
poetry config experimental.new-installer false
poetry config virtualenvs.in-project true
```

If you have any poetry install issues go to `AppData\Local\pypoetry` and delete the `Cache` directory and try again.

### IP Fabric Setup

- Go to Settings > Webhooks > Add webhook
- Provide a name
- URL will be: `http(s)://<YOUR IP/DNS>:8000/ipfabric`
- Copy secret
- Select if you want both Snapshot and Intent Events

### Environment Setup

- Rename `sample.env` to `.env`
- Edit `.env` with your IPF variables
    - Set `IPF_VERIFY` to False if your IP Fabric SSL cert is not trusted
    - `IPF_SECRET` is found in the webhook settings page
    - `IPF_URL` must be in the following format without any trailing information. For example: `https://demo3.ipfabric.io/`
    - `IPF_TOKEN` is an API token created in Settings > API Token
        - If you want to translate User ID to Username token must have User Management Scope
    - `IPF_TEST` will not send test alerts to the channel when set to `False`
    - `EMAIL_USER` User to sign into SMTP server
    - `EMAIL_PASS` Password for SMTP server auth
    - `MAIL_TO` Email address to mail to
    - `MAIL_FROM` Email to mail from
    - `SMTP_SERVER` SMTP server host
    - `SMTP_PORT` SMTP port

## Running

### Python

```shell
poetry run api
```

### Docker

```shell
docker-compose up
```
