from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG('kubernetes_fargate_sample', default_args=default_args, schedule_interval=timedelta(minutes=10))


start = DummyOperator(task_id='run_this_first', dag=dag)

fargate_task = KubernetesPodOperator(namespace='fargate',
                          image="python:3.6",
                          cmds=["python","-c"],
                          arguments=["print('hello fargate')"],
                          labels={"foo": "bar"},
                          name="fargate-task",
                          startup_timeout_seconds=600,
                          task_id="fargate-task",
                          in_cluster=True,
                          get_logs=True,
                          dag=dag
                          )

eks_task = KubernetesPodOperator(namespace='default',
                          image="python:3.6",
                          cmds=["python","-c"],
                          arguments=["print('hello eks')"],
                          labels={"foo": "bar"},
                          name="eks-task",
                          task_id="eks-task",
                          in_cluster=True,
                          get_logs=True,
                          dag=dag
                          )

fargate_task.set_upstream(start)
eks_task.set_upstream(start)