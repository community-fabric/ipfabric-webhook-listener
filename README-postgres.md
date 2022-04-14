# IP Fabric Webhook Integration for Postgres
This will listen to webhook events and extract a subset of IP Fabric data like Inventory Tables and
Intent check summary to insert into a Postgres Database.  This is useful for trending data over time.
Since only 5 snapshots are allowed to be loaded at one time this can help expand data to weeks or months
for trending in Grafana, Tableau, or other visualization tools.


## Setup

### <a id="python-setup"></a> Python Setup
```shell
python3 -m pip install -U pip poetry
poetry install -E postgres
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
    - `IPF_TEST` will not process a webhook when using the test function `False`
      - Test webhook requests will fail because it uses a random snapshot ID so automation will fail.
      - If test is set to true, automation will use $last snapshot ID.
    - Postgres Information
      - `POSTGRES_USER` Postgres User
      - `POSTGRES_PASS` Postgres Password
      - `POSTGRES_HOST` Posgtres host (defaults to localhost)
      - `POSTGRES_PORT` Postgres Port (defaults to 5432)
      - `POSTGRES_DB` Postgres Database to insert data (defaults to ipfabric)

## Running

### Python

```shell
poetry run api
```

### Docker

```shell
docker-compose up
```

## Grafana
Please see the JSON models located in [Grafana](Grafana) for examples on creating a dashboard.
You will need to connect Grafana to your PostgreSQL DB and find the `UID` of it.
After you have that identifier replace all instances of `<REPLACE WITH UID OF YOUR CONNECTED POSTGRES DB>` in the JSON files and import it.