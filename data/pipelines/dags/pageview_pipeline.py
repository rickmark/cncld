import glob
import os

from airflow import Asset
from airflow.models import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

with DAG(
    dag_id="pageview_pipeline",
    description="Upload pageview data to S3",
    schedule="@daily",
) as dag:
    pass
