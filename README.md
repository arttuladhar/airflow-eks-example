
### Running Locally

1. Update `utils/build.sh` with `ECR_BASE_URL` with any name
2. Run `docker-compose up`

---

### Running on AWS

1. Create EKS Cluster with Fargate

```shell
# AWS_PROFILE=<PROFILE_NAME> eksctl create cluster --name <CLUSTER_NAME> --version 1.17 --fargate
AWS_PROFILE=airflow_eks eksctl create cluster --name art-eks-fargate --version 1.17 --fargate
```

2. Switch your KubeCtl to newly created EKS Cluster
```shell

# Update KubeConfig
# aws eks --region <REGION> update-kubeconfig --name <EKS CLUSTER NAME> --profile <AWS_PROFILE>
aws eks --region <REGION> update-kubeconfig --name art-eks-fargate --profile airflow_eks

# Set Context to New EKS Cluster
# kubectl config set-context <EKS CLUSTER ARN>
kubectl config set-context <EKS CLUSTER ARN>
```

3. Create ECR

```shell
# aws ecr create-repository --repository-name <repo-name>
aws ecr create-repository --repository-name art-airflow
```

4. Update `utils/build.sh` with `ECR_BASE_URL`
5. Update Helm Chart values under `helm/airflow-eks/values.yaml` 
6. Install Airflow via Helm

```
helm install airflow-eks helm/airflow-eks
helm uninstall airflow-eks
```