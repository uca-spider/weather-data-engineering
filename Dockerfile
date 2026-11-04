FROM apache/airflow:2.8.1-python3.11

COPY --chown=airflow:root requirements.txt /requirements.txt

USER airflow

RUN pip install --no-cache-dir --user \
    --upgrade-strategy only-if-needed \
    -r /requirements.txt
