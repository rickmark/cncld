import pandas as pd

from airflow import Asset, DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor
from airflow.sdk.definitions.param import ParamsDict, Param
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.sdk import task, get_current_context, AssetAlias
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.sdk.definitions.param import ParamsDict
from pyathena.filesystem.s3_object import S3Object

@task()
def read_index(file_name):
    """
    Task to read index data from source.
    """
    hook = S3Hook(aws_conn_id='local_bucket')

    s3_object: S3Object = hook.get_key(key=file_name, bucket_name='wikipedia')

    index = s3_object['Body'].read().decode('utf-8')
    lines = [row for row in [line.split(':', maxsplit=3) for line in index.readlines()] if len(row) == 3]

    context = get_current_context()
    df = pd.DataFrame(lines, columns=['stream_offset', 'page_id', 'title'])
    context.xcom_push(key='index_df', value=df)

@task(outlets=[
    AssetAlias('wikipedia.multistream_index')
])
def write_index():
    context = get_current_context()
    df = context.xcom_pull(task_ids='read_index', key='index_df')

    sqlite_insert_task = MySqlHook(
        mysql_conn_id="local_wikipedia",  # Reference the connection ID created in the UI
        schema="wikipedia",
        table="multistream_index"
    )

    df.to_sql('multistream_index', con=sqlite_insert_task.get_conn(), if_exists='replace', index=False)

with DAG(dag_id='index_pipeline',
    default_args={
    'owner': 'rickmark'
    },
    description='Index pipeline for Wikipedia data',
    params=ParamsDict({
        'file_name': 'enwiki-20251220-pages-articles-multistream-index.txt'
    }),
    tags={'trino', 'wikipedia'}) as dag:

    read_index_task = read_index(file_name="{{ params['file_name'] }}")

    write_index_task = write_index()

    read_index_task >> write_index_task
