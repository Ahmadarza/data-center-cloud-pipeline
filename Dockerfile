FROM apache/airflow:2.5.1

USER airflow

RUN pip install --no-cache-dir selenium==4.10.0