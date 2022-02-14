# IP Fabric Webhook Integration for Microsoft Teams and/or Slack

This will send an alert to MS Teams or Slack when certain Snapshot or Intent Rules are process in IP Fabric.

## Setup

### <a id="python-setup"></a> Python Setup
```shell
python3 -m pip install -U pip poetry
poetry install -E notify
```
One time suggested config changes before installing:
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
  - Recommended for only Snapshot events.

### Environment Setup

- Rename `sample.env` to `.env`
- Edit `.env` with your IPF variables
    - Set `IPF_VERIFY` to False if your IP Fabric SSL cert is not trusted
    - `IPF_SECRET` is found in the webhook settings page
    - `IPF_URL` must be in the following format without any trailing information. For example: `https://demo3.ipfabric.io/`
    - `IPF_TOKEN` is an API token created in Settings > API Token
        - If you want to translate User ID to Username token must have User Management Scope
    - `IPF_TEST` will not send test alerts to the channel when set to `False`
    - `IPF_ALERTS` will turn on/off which events to respond to:
      - Default IP Fabric alerts can be found in [ipf_alerts.json](ipf_alerts.json) and then minified into `IPF_ALERTS`
      - Edit [ipf_alerts.json](ipf_alerts.json) to your desired settings
      - `python -c "import json, sys;json.dump(json.load(sys.stdin), sys.stdout)"  < ipf_alerts.json`
      - Copy/paste output in `IPF_ALERTS`
    - Notification Channels (Can send to both locations if both variables are set)
      - `TEAMS_URL` is found when adding an "Incoming Webhook" on a Teams Channel
      - `SLACK_URL` is found when adding an "Incoming Webhook" on a Slack Channel

## Running

### Python

```shell
poetry run api
```

### Docker

```shell
docker-compose up
```

## Examples
### Slack
![slack.png](slack.png)
### Temas
![teams.png](teams.png)