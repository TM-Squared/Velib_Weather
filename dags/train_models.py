import sys
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
from jobs.transform.ml_availability_bikes import availability_bikes

default_args = {
    'owner': 'manoel',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'train_model',
    default_args=default_args,
    schedule_interval='0 12 * * *', # à 12h
    catchup=False
)

start = EmptyOperator(
    task_id='start',
    dag=dag
)

train_task = PythonOperator(
    task_id='train_bike_availability_model',
    python_callable=availability_bikes,
    dag=dag
)

end = EmptyOperator(
    task_id='end',
    dag=dag
)

start >> train_task >> end