from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator


# Default arguments that are going to be passed to all the tasks
# They can be overwritten inside each task
default_args = {'retries': 5,  # Number of retries before marking as failed
                'retry_delay': timedelta(seconds=30)  # Time between retries
                }


# Function to be called in a task
def _downloading_data(ti):
    with open('/tmp/my_file.txt', 'w') as f:
        f.write("my_data")

    ti.xcom_push(key='my_key', value=42)


def _get_metadata(**kwargs):
    # By using kwargs, we get airflow context information
    print(kwargs)


def _check_data(ti):
    my_xcom = ti.xcom_pull(key='my_key', task_ids=['downloading_data'])
    print("XCOM", my_xcom)


def _get_named_metadata(ds):
    # Can get a parameter from previous function by its name
    print(ds)


# Passing parameters from functions
def my_param_func(my_param, ds):
    print(my_param)
    print(ds)


with DAG(dag_id="simple_dag",
         start_date=datetime(2021, 6, 1),
         schedule_interval=timedelta(minutes=10),
         catchup=False,
         default_args=default_args) as dag:
    task_1 = DummyOperator(task_id="task_1")
    task_2 = DummyOperator(task_id="task_2")
    task_3 = PythonOperator(task_id="downloading_data",
                            python_callable=_downloading_data)

    task_4 = PythonOperator(task_id="metadata",
                            python_callable=_get_metadata)

    task_5 = PythonOperator(task_id="named_metadata",
                            python_callable=_get_named_metadata)

    task_6 = PythonOperator(task_id="my_param_func",
                            python_callable=my_param_func,
                            op_kwargs={'my_param': 'Rodrigo'})

    task_7 = PythonOperator(task_id="xcoms_data",
                            python_callable=_check_data)


task_1 >> task_2 >> [task_3, task_4]
task_4 >> [task_5, task_6] >> task_7

