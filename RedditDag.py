from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
from Reddit_etl import reddit_Extraction

default_args = {
    'owner': 'Chinmayi',
    'depends_on_past': False,
    'start_date': datetime(2020, 11, 8),
    'email': ['chinmayiprakashmurthy@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'Reddit_dag',
    default_args=default_args,
    description='US Elections emotions dag',
    schedule_interval=timedelta(days=1),
)

run_etl = PythonOperator(
    task_id='Reddit_ETL',
    python_callable=reddit_Extraction,
    dag=dag, 
)

run_etl