import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))

from jobs.extract.ingest_api_data import fetch_bike_data, fetch_weather_data
from jobs.transform.transform_raw_to_fmt import transform_raw_to_fmt
from jobs.transform.ml_availability_bikes import availability_bikes
from jobs.transform.aggregate_fmt_to_agg import aggregate_fmt_to_agg
from jobs.load.index_agg_to_elasticsearch import index_agg_to_elasticsearch

default_args = {
    'owner': 'manoel',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    schedule_interval='*/10 * * * *',
    catchup=False
)

start = EmptyOperator(
    task_id='start',
    dag=dag
)



ingest_bike_task = PythonOperator(
    task_id='ingest_bike_data',
    python_callable=fetch_bike_data,
    dag=dag
)

ingest_weather_task = PythonOperator(
    task_id='ingest_weather_data',
    python_callable=fetch_weather_data,
    dag=dag
)


raw_to_fmt_task = PythonOperator(
    task_id="transform_raw_to_fmt",
    python_callable=transform_raw_to_fmt,
    dag=dag
)

fmt_to_agg_task = PythonOperator(
    task_id="aggregation_fmt_to_agg",
    python_callable=aggregate_fmt_to_agg,
    dag=dag
)



index_to_elasticsearch_task = PythonOperator(
    task_id="index_to_elasticsearch",
    python_callable=index_agg_to_elasticsearch,
    dag=dag
)

end = EmptyOperator(
    task_id='end',
    dag=dag
)


start >> [ingest_bike_task, ingest_weather_task] >> raw_to_fmt_task >> fmt_to_agg_task
fmt_to_agg_task  >> index_to_elasticsearch_task >> end
