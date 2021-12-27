# IP Fabric Webhook Integration for Tableau
This will create a hyper file which can be published to Tableau.  It does not publish and will need
further development with a working Tableau server.

This currently only saves device inventory table into hyper file after a discovery completed
webhook is received.  You can extend this to other tables as you wish.

Make sure to schedule a cleanup to remove old files.

## Tableau Information
- [Python Hyper API Example](https://help.tableau.com/current/api/hyper_api/en-us/docs/hyper_api_create_update.html)
- [Pantab Documentation](https://pantab.readthedocs.io/en/latest/examples.html)
- [Publish Hyper Files](https://help.tableau.com/current/api/hyper_api/en-us/docs/hyper_api_publish.html)
- [Single table publisher example](https://github.com/tableau/hyper-api-samples/tree/main/Community-Supported/publish-hyper)
- [Multi-Table publisher example](https://github.com/tableau/hyper-api-samples/tree/main/Community-Supported/publish-multi-table-hyper)

## Notes
### Working with Epoch Timestamps
To convert epoch timestamp (i.e. End of Life dates or other data):
- Right click the field name > Create > Calculated Field
- Example Calculation: `DATEADD('second', INT([End Support]/1000), #1970-01-01#)`

For times like Uptime, these can be converted to dd:hh:mm:ss
- https://kb.tableau.com/articles/howto/converting-seconds-to-hh-mm-ss-or-dd-hh-mm-ss


## Setup

### <a id="python-setup"></a> Python Setup
```shell
python3 -m pip install -U pip poetry
poetry install -E tableau
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
      - Test webhook requests will fail because it uses a random snapshot ID so automation will fail.
      - In automation.py you can set `IPF.snapshot_id = '$last'` while running tests.

## Running

### Python

```shell
poetry run api
```

### Docker
Docker may not work as this requires writing a file to storage.

```shell
docker-compose up
```
