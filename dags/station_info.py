import sys
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
from jobs.extract.fetch_station_info import fetch_station_info

default_args = {
    'owner': 'manoel',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'fetch_station_info',
    default_args=default_args,
    schedule_interval='@yearly', 
    catchup=False
)

start = EmptyOperator(
    task_id='start',
    dag=dag
)

update_station_info_task = PythonOperator(
    task_id='update_station_info',
    python_callable=fetch_station_info,
    dag=dag
)

end = EmptyOperator(
    task_id='end', 
    dag=dag
)

start >> update_station_info_task >> end