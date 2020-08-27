
### Running Locally

1. Update `utils/build.sh` with `ECR_BASE_URL` with any name
2. Run `docker-compose up`

---

### Running on AWS

1. Create EKS Cluster without Fargate Profile

```shell
# AWS_PROFILE=<PROFILE_NAME> eksctl create cluster --name <CLUSTER_NAME> --version 1.17
AWS_PROFILE=airflow_eks eksctl create cluster --name art-eks --version 1.17
```

2. Switch your kubectl to use newly created EKS Cluster
   
```shell
# Update KubeConfig
# aws eks --region <REGION> update-kubeconfig --name <EKS CLUSTER NAME> --profile <AWS_PROFILE>
aws eks --region us-east-2 update-kubeconfig --name art-eks --profile airflow_eks

# Set Context to New EKS Cluster
# kubectl config set-context <EKS CLUSTER ARN>
kubectl config set-context arn:aws:eks:us-east-2:020886952569:cluster/art-eks
```

3. Create Fargate Profile and Namespace

```shell
# eksctl create fargateprofile --cluster <CLUSTER_NAME> --name <FARGATE_PROFILE_NAME> --namespace <NAMESPACE> --labels key=value
eksctl create fargateprofile --cluster art-eks --name airflow_dag --namespace fargate

# Create Kubernetes Namespace
kubectl create namespace 
```

4. Create ECR for Docker Images

```shell
# aws ecr create-repository --repository-name <repo-name>
aws ecr create-repository --repository-name art-airflow
```

Copy the repositoryURL

5. Update `utils/build.sh` with `ECR_BASE_URL` and run script
```
./utils/build.sh
```

6. Update Helm Chart values under `helm/airflow-eks/values.yaml`  and Install Airflow via Helm
```
helm install airflow-eks helm/airflow-eks
```

7. Verify Pods are running and airflow service is up

```
kubectl get pods --all-namespaces
```


---

## Cleanup

```shell

# Uninstall Airflow
helm uninstall airflow-eks

# Delete EKS Cluster
eksctl delete cluster -n art-eks -r us-east-2

# Delete ECR Repository
aws ecr delete-repository --repository-name art-airflow --force
```
