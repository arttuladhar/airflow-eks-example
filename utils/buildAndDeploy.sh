#!/bin/bash

echo "This script assumes that it is ran from the root project directory. Make sure that it is ran from the correct directory."

# AWS Profile and Region
PROFILE=airflow_eks
REGION=us-east-2

# Address of the ECR repository
ECR_BASE_URL=020886952569.dkr.ecr.us-east-2.amazonaws.com/airflow
# ECR_BASE_URL=art-repo

if [ $? -eq 0 ]; then
  ECR_URL=`for i in $(echo $ECR_BASE_URL | tr "/" "\n")
  do
    echo $i
  done | sed -n 1p`
  aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL
fi

# docker builder prune --filter type=exec.cachemount
docker build --no-cache -t art-airflow docker/
docker tag art-airflow:latest $ECR_BASE_URL

if [ $? -eq 0 ]; then
  docker push $ECR_BASE_URL
fi