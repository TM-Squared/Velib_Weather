FROM apache/airflow:2.10.5-python3.10
LABEL authors="manoel"
USER root
RUN apt-get update \
  && apt-get install -y openjdk-17-jdk \
  && apt-get install -y wget \
  && apt-get install -y --no-install-recommends   \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow
RUN pip install --upgrade pip  \
    && pip install poetry==2.1.1
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

