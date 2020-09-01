import sys, json, os
from controllers.EmrClusterController import EmrClusterController

def create_EMR_cluster(cluster_name, emr_version):
    cluster_id = EmrClusterController.create_cluster_job_execution(cluster_name, emr_version)
    print("Waiting for Cluster: ", cluster_id)
    xcom_return = {"clusterId": cluster_id}
    
    with open ("/airflow/xcom/return.json", "w") as file:
        json.dump(xcom_return, file)
    
    return EmrClusterController.wait_for_cluster_creation(cluster_id)

def configure_job(cluster_id):
    step_get_credentials = EmrClusterController.add_job_step(cluster_id, "Get-Credentials", "command-runner.jar",
                                                ["aws", "s3", "cp", "s3://art-emr-configuration-scripts/credentials",
                                                 "/home/hadoop/.aws/"])
    EmrClusterController.wait_for_step_completion(cluster_id, step_get_credentials)
    status = EmrClusterController.get_step_status(cluster_id, step_get_credentials)
    if status == "FAILED":
        print("GET CREDENTIALS FROM S3 FAILED")
        raise RuntimeError("Get Credentials Failed During Execution: Reason documented in logs probably...?")
    elif status == "COMPLETED":
        print("GET CREDENTIALS FROM S3 COMPLETED SUCCESSFULLY")

    step_get_jars = EmrClusterController.add_job_step(cluster_id, "Get-Jars", "command-runner.jar",
                                                ['aws', 's3', 'cp', 's3://art-emr-configuration-scripts/CitiBikeDataProduct-assembly-0.1.jar',
                                                 "/home/hadoop/"])
    EmrClusterController.wait_for_step_completion(cluster_id, step_get_jars)
    status = EmrClusterController.get_step_status(cluster_id, step_get_jars)
    if status == "FAILED":
        print("GET JAR FROM S3 FAILED")
        raise RuntimeError("Get Jar Failed During Execution: Reason documented in logs probably...?")
    elif status == "COMPLETED":
        print("GET JAR FROM S3 COMPLETED SUCCESSFULLY")    

def spark_submit(cluster_id):
    step_spark_submit = EmrClusterController.add_job_step(cluster_id, "Spark-Submit", "command-runner.jar",
                                                ['spark-submit', '--class', 'com.ricardo.farias.App',
                                                 "/home/hadoop/CitiBikeDataProduct-assembly-0.1.jar"])
    EmrClusterController.wait_for_step_completion(cluster_id, step_spark_submit)
    status = EmrClusterController.get_step_status(cluster_id, step_spark_submit)
    if status == "FAILED":
        print("SPARK SUBMIT JOB FAILED")
        raise RuntimeError("Spark Job Failed During Execution: Reason documented in logs probably...?")
    elif status == "COMPLETED":
        print("SPARK SUBMIT JOB COMPLETED SUCCESSFULLY")

def terminate_cluster(cluster_id):
    cluster_id = ti.xcom_pull(task_ids='create_cluster')
    EmrClusterController.terminate_cluster(cluster_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SyntaxError("Insufficient arguments.")

    option = sys.argv[1]

    if option == "create_cluster":
        print ("Create EMR Cluster")
        cluster_id = create_EMR_cluster("Citi Bike Cluster", "emr-5.30.0")
    
    elif option == "configure_job":
        print ("Configuring Job")
        configure_job(sys.argv[2])
    
    elif option == "submit_job":
        print("Submitting Spark Job")
        spark_submit(sys.argv[2])

    elif option == "delete_cluster":
        print("Deleting EMR Cluster")
        terminate_cluster(sys.argv[2])
    else:
        print ("Invalid Options")
        exit(-1)
