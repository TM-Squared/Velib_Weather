import sys
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
from jobs.transform.ml_predict_bike_availability import predict_bike_availability

default_args = {
    'owner': 'manoel',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'predict_bike_availability',
    default_args=default_args,
    schedule_interval='0 * * * *', 
    catchup=False
)

start = EmptyOperator(task_id='start', dag=dag)

predict_task = PythonOperator(
    task_id='predict_bike_availability',
    python_callable=predict_bike_availability,
    dag=dag
)

end = EmptyOperator(task_id='end', dag=dag)

start >> predict_task >> end
