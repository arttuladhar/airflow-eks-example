from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.secret import Secret

args = {
    'owner': 'Airflow',
    'start_date': days_ago(2)
}

dag = DAG(
    'citi-bike-kubernetes-operator-pipeline',
    default_args=args,
    description='Spark Submit job to EMR',
    schedule_interval=None,
)

env_var_secret1 = Secret('env', 'AWS_ACCESS_KEY_ID', 'citi-bike-secrets', 'aws_access_key_id')
env_var_secret2 = Secret('env', 'AWS_SECRET_ACCESS_KEY', 'citi-bike-secrets', 'aws_secret_access_key')

create_cluster_task = KubernetesPodOperator(namespace='default',
    task_id="create_cluster",
    name="create_cluster_task",
    image="020886952569.dkr.ecr.us-east-2.amazonaws.com/python-aws:latest",
    arguments=["create_cluster"],
    in_cluster=True,
    get_logs=True,
    do_xcom_push=True,
    secrets=[env_var_secret1, env_var_secret2],
    image_pull_policy='Always',
    env_vars={'DATA_PRODUCT':'citi_bike'},
    resources = {'request_cpu': '0.50', 'request_memory': '0.7Gi'},
    node_selectors={'app':'citi_bike'}
    dag=dag
)

configure_job = KubernetesPodOperator(namespace='default',
    name="configure_job",
    task_id="configure_job",
    image="020886952569.dkr.ecr.us-east-2.amazonaws.com/python-aws:latest",
    arguments=["configure_job",
    "{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value')['clusterId'] }}"],
    in_cluster=True,
    get_logs=True,
    do_xcom_push=False,
    image_pull_policy='Always',
    secrets=[env_var_secret1, env_var_secret2],
    env_vars={'DATA_PRODUCT':'citi_bike'},
    resources = {'request_cpu': '0.50', 'request_memory': '0.7Gi'},
    node_selectors={'app':'citi_bike'}
    dag=dag
)

spark_submit_task = KubernetesPodOperator(namespace='default',
    name="submit_job",
    task_id="submit_job",
    image="020886952569.dkr.ecr.us-east-2.amazonaws.com/python-aws:latest",
    secrets=[env_var_secret1, env_var_secret2],
    arguments=["submit_job", "{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value')['clusterId'] }}"],
    in_cluster=True,
    do_xcom_push=False,
    image_pull_policy='Always',
    env_vars={'DATA_PRODUCT':'citi_bike'},
    resources = {'request_cpu': '0.50', 'request_memory': '0.7Gi'},
    node_selectors={'app':'citi_bike'},
    get_logs=True,
    dag=dag
)

terminate_cluster_task = KubernetesPodOperator(namespace='default',
    name="terminate_job",
    task_id="terminate_job",
    image="020886952569.dkr.ecr.us-east-2.amazonaws.com/python-aws:latest",
    secrets=[env_var_secret1, env_var_secret2],
    arguments=["terminate_cluster", "{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value')['clusterId'] }}"],
    in_cluster=True,
    do_xcom_push=False,
    env_vars={'DATA_PRODUCT':'citi_bike'},
    image_pull_policy='Always',
    resources = {'request_cpu': '0.50', 'request_memory': '0.7Gi'},
    node_selectors={'app':'citi_bike'}
    get_logs=True,
    dag=dag
)

create_cluster_task >> configure_job  >> spark_submit_task >> terminate_cluster_task