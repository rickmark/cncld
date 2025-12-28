import pandas as pd
from airflow import DAG
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.sdk import task, AssetAlias
from airflow.sdk.definitions.param import ParamsDict

import logging

logger = logging.getLogger(__name__)

with DAG('multistream_index_pipeline',
         params=ParamsDict({
             'file_name': 'enwiki-pages-articles-multistream-index.txt'
         }),
         schedule="@daily") as dag:


    @task(do_xcom_push=True)
    def read_index(file_name):
        """
        Task to read index data from source.
        """
        hook = S3Hook(aws_conn_id='local_storage')

        s3_object = hook.get_key(key=file_name, bucket_name='wikipedia')

        lines = [row for row in [
            line.decode('utf8').split(':', maxsplit=3)
            for line
            in s3_object.get()['Body'].iter_lines()
        ] if len(row) == 3]

        result_df = pd.DataFrame(lines, columns=['stream_offset', 'page_id', 'title'])
        return result_df

    @task(outlets=[
              AssetAlias('trino://localhost/mysql/wikipedia/multistream_index')
          ])
    def write_index(ti):
        multistream_index_hook = MySqlHook(
            mysql_conn_id="mysql_wikipedia",  # Reference the connection ID created in the UI
            schema="wikipedia",
            table="multistream_index"
        )

        result_df = ti.xcom_pull(task_ids='read_index')

        result_df.to_sql('multistream_index',
                         con=multistream_index_hook.get_sqlalchemy_engine(),
                         if_exists='replace',
                         index=False)

        return result_df

    drop_multistream_index = SQLExecuteQueryOperator(
        task_id="drop_multistream_index",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DROP TABLE IF EXISTS mysql.wikipedia.multistream_index"
    )

    create_multistream_index = SQLExecuteQueryOperator(
        task_id="create_multistream_index",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="""CREATE TABLE IF NOT EXISTS mysql.wikipedia.multistream_index (
                    stream_offset INT NOT NULL,
                    page_id INT NOT NULL,
                    title VARCHAR NOT NULL
                )"""
    )


    read_index_task = read_index(file_name="{{ params['file_name'] }}")

    write_task = write_index()

    drop_multistream_index >> create_multistream_index >> read_index_task >> write_task

if __name__ == "__main__":
    dag.test()