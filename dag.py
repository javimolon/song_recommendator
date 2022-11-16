from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import song_recommendator as sr

with DAG('my_dag', start_date = (2022,11,17),schedule_interval = '(@daily)', catchup = False) as dag:
    extract_task = PythonOperator(task_id = 'extract', python_callable = sr.extract)
    df1, df2 = extract_task.output
    transform_task = PythonOperator(task_id = 'transform', python_callable = sr.transform, args = [df1, df2])
    load_task = PythonOperator(task_id = 'load', python_callable = sr.load, args = [transform_task.output])
    main_task = PythonOperator(task_id = 'main', python_callable = sr.main, args = [transform_task.output])
    

