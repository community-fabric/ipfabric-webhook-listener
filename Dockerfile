# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN useradd -ms /bin/bash ipf

WORKDIR /opt/ipf
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN python3 -m pip install pip \
    && pip3 install poetry \
    && poetry config experimental.new-installer false && poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY ipf_webhook_listener ipf_webhook_listener
COPY ipf_webhook_listener/images images
RUN chown -R ipf .
RUN poetry install --no-dev -E tableau

USER ipf

EXPOSE 8000
CMD ["python3", "-m" , "uvicorn", "ipf_webhook_listener.api:app", "--host", "0.0.0.0", "--port", "8000"]
