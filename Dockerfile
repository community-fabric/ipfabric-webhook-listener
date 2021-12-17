# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN useradd -ms /bin/bash ipf
USER ipf

WORKDIR /opt/ipf

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ipf_webhook_listener ipf_webhook_listener

ENV PYTHONPATH /opt/ipf

EXPOSE 8000
CMD ["python3", "-m" , "uvicorn", "ipf_webhook_listener.api:app", "--host", "0.0.0.0", "--port", "8000"]
