# IP Fabric Webhook Integration for X

## Setup

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

## Running

### Python

```shell
python3 -m venv venv && source venv/bin/activate
pip3 install -r requirements.txt
python3 api.py
```

If Using poetry
```shell
python3 -m pip install -U pip poetry
poetry install
poetry run python api.py
```

### Docker

```shell
docker-compose up
```
