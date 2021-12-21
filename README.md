# IP Fabric Webhook Integration for X

Integrations will be developed under different branches based on the main branch. 
This will allow for easier development and not require installing all packages for integrations 
you do not plan to use.  We will develop an integration video on how to merge different branches into 
a usable product per your environment.

## Development
This project will use Python Poetry exclusively so package handling is easily managed and
dependencies across branches do not conflict.  See [Python Setup](#python-setup)

- Fork this repository to your workspace and create a new branch for your integration.
- To add new packages for your integration run:
  - `poetry add package-name --optional`
  - In `pyproject.toml` look for `[tool.poetry.extras]`
  - Add a new line with your integration and the required packages, for instance:
    - `tableau = ["tableauhyperapi", "pandas", "pantab"]`
    - If your package is specified in another extra it is acceptable to include it in yours without adding it.
  - To install and use the packages:
    - `poetry install -E tableau`
- Copy README.md to README-integration-name.md and edit with appropriate documentation for your branch.
- Once your integration is working commit the branch to your github repository
- Switch to the main branch and add your `pyproject.toml` changes and commit them
- Open a PR to the community-fabric main branch and specify your integration and branch name.
- Once approved and merged we will create a new branch for you.
- Once the new branch is created open a new PR for your new integration into our branch.

## Setup

### <a id="python-setup"></a> Python Setup
```shell
python3 -m pip install -U pip poetry
poetry install
```
One time suggested config changes:
```shell
poetry config experimental.new-installer false
poetry config virtualenvs.in-project true
```

To install optional requirements use the -E option:
```shell
poetry install -E tableau
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

## Running

### Python

```shell
poetry run api
```

### Docker

```shell
docker-compose up
```
