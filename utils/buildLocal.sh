docker build -t art-airflow-local docker/
docker tag art-airflow-local localhost:5000/art-airflow-local
docker push localhost:5000/art-airflow-local:latest

helm uninstall airflow-eks
helm install airflow-eks helm/airflow-eks
