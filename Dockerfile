ARG PYTHON_VERSION="3.8-slim-buster"
ARG PYTHON_IMAGE_ORIGIN="python"
ARG PYTHON_IMAGE=$PYTHON_IMAGE_ORIGIN:$PYTHON_VERSION

FROM $PYTHON_IMAGE AS BuildStage

LABEL MAINTAINER="George Babarus <george.babarus@gmail.com>"
ENV PS1="\[\e[0;33m\]|> lcli <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "
ENV PATH="/app/venv/bin:${PATH}"

RUN apt-get update \
     && apt-get install -y make \
     && rm -rf /var/lib/apt/lists/*

RUN pip3 install pipenv poetry

COPY ./poetry.config.toml ~/.config/pypoetry/config.toml
WORKDIR /app

RUN useradd -m lcli \
    && chown -R lcli:lcli /app

COPY --chown=lcli . .

USER lcli

RUN poetry env use python \
      && poetry install \
      && ln -s  $(poetry env info --path) venv

FROM BuildStage as TestStage

RUN pytest --cov=src/lcli

FROM $PYTHON_IMAGE AS BinaryStage
LABEL MAINTAINER="George Babarus <george.babarus@gmail.com>"

ENV PS1="\[\e[0;33m\]|> lcli <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "
ENV PATH="/app/venv/bin:${PATH}"

WORKDIR /app

RUN useradd -m lcli \
    && chown -R lcli:lcli /app

COPY --chown=lcli . .

RUN pip install -U .

USER lcli
