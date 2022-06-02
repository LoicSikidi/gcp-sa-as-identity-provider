FROM python:3.10-slim

RUN groupadd --gid 1000 pypy \
  && useradd --uid 1000 --gid pypy --shell /bin/bash --create-home pypy

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app/

ENV PYTHONPATH /code/app

ENV GRPC_DNS_RESOLVER native

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "0", "--no-server-header"]

USER pypy
