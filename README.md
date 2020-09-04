# airflow-eks-demo

## Running Locally

Run `./utils/kind-with-registry.sh` to spin up kubernetes cluster with docker registry. This will create a kubernetes cluster named `kind` with local docker registry running on `localhost:5000`

Build local docker image using

```
docker build -t art-airflow-local docker/
```

Tag Airflow Image and push to localhost registry

```
docker tag art-airflow-local localhost:5000/art-airflow-local
docker push localhost:5000/art-airflow-local:latest
```

Update Helm values with local docker registry
```
  repository: localhost:5000/art-airflow-local
  tag: latest
```

Deploy airflow along with DAGS using helm

```
helm install airflow-eks helm/airflow-eks
```

Port forward Kubernetes Port to localhost

```
kubectl port-forward svc/airflow 8080:80
```

---

## Running on AWS

Update `utils/build.sh` with `ECR_BASE_URL` with any name

Create EKS Cluster

```shell
# eksctl create cluster --name <CLUSTER_NAME> --version 1.17
eksctl create cluster --name art-eks --managed
```

Switch your kubectl to use newly created EKS Cluster
   
```shell
# Update KubeConfig
# aws eks --region <REGION> update-kubeconfig --name <EKS CLUSTER NAME>
aws eks --region us-east-2 update-kubeconfig --name art-eks

# Set Context to New EKS Cluster
# kubectl config set-context <EKS CLUSTER ARN>
kubectl config set-context arn:aws:eks:us-east-2:020886952569:cluster/art-eks
```

Create Fargate Profile and Namespace

```shell
# eksctl create fargateprofile --cluster <CLUSTER_NAME> --name <FARGATE_PROFILE_NAME> --namespace <NAMESPACE> --labels key=value
eksctl create fargateprofile --cluster art-eks --name fargate --namespace fargate

# Create Kubernetes Namespace
kubectl create namespace fargate
```

<!--
Create ECR for Docker Images

```shell
# aws ecr create-repository --repository-name <repo-name>
aws ecr create-repository --repository-name art-airflow
```
 -->

Copy the repositoryURL

Update `utils/buildAndDeploy.sh` with `ECR_BASE_URL` and run script
```
./utils/build.sh
```

Update Helm Chart values under `helm/airflow-eks/values.yaml`  and Install Airflow via Helm

```
helm install airflow-eks helm/airflow-eks
```

Verify Pods are running and airflow service is up

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

---

## Debug

### Port Forward Airflow port
```
kubectl port-forward svc/airflow 8080:80
```


### Delete Old Pods

```
kubectl get pods | grep Completed | awk '{print $1}' | xargs kubectl delete pod
kubectl get pods | grep Error | awk '{print $1}' | xargs kubectl delete pod
kubectl get pods | grep ImagePullBackOff | awk '{print $1}' | xargs kubectl delete pod
```

### SSH to the Container
```
kubectl exec --stdin --tty airflow-6789996f94-f6dqx -c scheduler -- /bin/bash
```

