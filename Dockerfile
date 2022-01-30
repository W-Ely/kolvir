# Python 3.10 has dependency install issues
FROM python:3.9-slim as base
LABEL "service"="kolvir"

WORKDIR /app
ENV \
  DEBIAN_FRONTEND=noninteractive \
  PYTHONIOENCODING=utf-8 \
  PYTHONPATH=$PYTHONPATH:/app \
  TZ=UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone

RUN pip install --upgrade pip setuptools pipenv

# --------------

FROM kolvir:base as python-node
LABEL "service"="kolvir"

RUN apt-get update && apt-get install -y curl build-essential

ENV \
  NODE_VERSION=16.13.2 \
  NVM_VERSION=0.39.1

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh | bash
ENV \
  NVM_DIR=/root/.nvm \
  PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"

# --------------

FROM kolvir:python-node as local
LABEL "service"="kolvir"

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN apt-get install -y unzip
RUN unzip awscliv2.zip
RUN ./aws/install

COPY package* ./
RUN npm ci

COPY Pipfile* ./
RUN pipenv install --system --deploy --dev --ignore-pipfile --keep-outdated

# --------------

FROM kolvir:base as api
LABEL "service"="kolvir"

COPY Pipfile* ./
RUN pipenv install --system --deploy
COPY ./kolvir ./kolvir

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

# --------------

FROM kolvir:base as circle
LABEL "service"="kolvir"

COPY Pipfile* ./
RUN pipenv install --system --deploy --dev --ignore-pipfile --keep-outdated
COPY . .
