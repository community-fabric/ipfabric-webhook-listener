# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN useradd -ms /bin/bash ipf
USER ipf

WORKDIR /opt/ipf

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/. .

EXPOSE 8000
CMD [ "python3", "-m" , "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
