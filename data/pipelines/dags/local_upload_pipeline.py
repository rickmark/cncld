import glob
import os
from pathlib import Path

from airflow import Asset
from airflow.models import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator


with DAG(
    dag_id="pageview_pipeline",
    schedule="@daily",
) as dag:
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
            outlets=[Asset(f"s3://wikipedia/{non_prefix}")],
            aws_conn_id='local_storage', # Refers to the connection ID created earlier
            replace=True, # Overwrite if the key already exists
        )

    for file in glob.glob(os.path.expanduser("~/Downloads/wikipedia/pageviews/*")):
        split_url = f"s3://wikipedia/pageviews/{file}"

        upload_operator = LocalFilesystemToS3Operator(
            task_id=f'upload_pageview_{file}_to_s3',
            filename=file, # Full path to the file on the Airflow worker
            dest_key=f'pageviews/{file}', # The key (path/name) in S3
            dest_bucket='wikipedia',
            outlets=[Asset(split_url)],
            aws_conn_id='local_storage', # Refers to the connection ID created earlier
            replace=False, # Overwrite if the key already exists
        )
