import glob
import os
import logging
from pathlib import Path

from airflow import Asset
from airflow.sdk import task
from airflow.models import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator

default_args = {
    'owner': 'rickmark',
}

with DAG(
    dag_id="local_upload_pipeline",
    schedule="@daily",
    default_args=default_args,
) as dag:
    @task.branch(task_id="check_s3_file")
    def check_s3_file(dest_key, task_key):
        hook = S3Hook(aws_conn_id='local_storage')
        if hook.check_for_key(dest_key, bucket_name='wikipedia'):
            return task_key
        return None

    for file in glob.glob(os.path.expanduser("~/Downloads/wikipedia/*")):
        path_obj = Path(file)
        if path_obj.parent.name == "pageviews":
            continue

        base = os.path.basename(file)

        parts = base.split("-")
        if len(parts) < 3:
            continue

        parts.pop(1)

        non_prefix = '-'.join(parts)

        upload_operator = LocalFilesystemToS3Operator(
            task_id=f'upload_{non_prefix}_to_s3',
            filename=file, # Full path to the file on the Airflow worker
            dest_key=non_prefix, # The key (path/name) in S3
            dest_bucket='wikipedia',
            #outlets=[Asset(f"s3://wikipedia/{non_prefix}")],
            aws_conn_id='local_storage', # Refers to the connection ID created earlier
            replace=True, # Overwrite if the key already exists
        )

    for file in glob.glob(os.path.expanduser("~/Downloads/wikipedia/pageview/*")):
        base = os.path.basename(file)
        split_url = f"s3://wikipedia/pageviews/{base}"
        logging.info(f"Uploading PageViews: {split_url}")
        dest_key = f'pageviews/{base}'
        task_key = base.replace('-', '_')
        task_id = f'upload_pageview_{task_key}_to_s3'


        check_operator = check_s3_file.override(task_id=f"check_s3_file_{task_key}")(dest_key, task_id)
        upload_operator = LocalFilesystemToS3Operator(
            task_id=task_id,
            filename=file, # Full path to the file on the Airflow worker
            dest_key=dest_key, # The key (path/name) in S3
            dest_bucket='wikipedia',
            #outlets=[Asset(split_url)],
            aws_conn_id='local_storage', # Refers to the connection ID created earlier
            replace=False, # Overwrite if the key already exists
        )
        check_operator >> upload_operator

if __name__ == "__main__":
    dag.test()