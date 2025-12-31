import pandas as pd
import bz2
import re

from airflow import Asset
from airflow.models import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

import logging

from airflow.sdk import task

logging.basicConfig(level=logging.INFO)

PAGEVIEWS_FILE = re.compile(r"pageviews/pageviews-(\d+)-user.bz2")



with DAG(
    dag_id="pageview_pipeline",
    description="Upload pageview data to S3",
    schedule="@daily") as dag:



    @task
    def process_pageviews_file(filename):
        logging.info(f"Parsing {filename}")
        date_stamp = PAGEVIEWS_FILE.match(filename)[1]

        s3_bucket = S3Hook(aws_conn_id='local_storage')

        input_data = s3_bucket.get_key(filename, bucket_name='wikipedia').get()['Body']

        with  bz2.BZ2File(input_data, 'r') as stream:
            pageviews_raw: pd.DataFrame = pd.read_csv(stream, sep=' ', names=['project', 'page_title', 'page_id', 'access_method', 'view_count', 'view_sequence'])

        df = pageviews_raw.drop(['project', 'access_method', 'view_sequence', 'page_title'], axis=1)

        df = df[df['page_id'].notnull()]

        df = df.groupby('page_id').agg({'view_count': 'sum'}).reset_index()
        df['ds'] = f"{date_stamp[0:4]}-{date_stamp[4:6]}-01"
        df['page_id'] = df['page_id'].astype(int)

        insert_hook = MySqlHook(
            mysql_conn_id="mysql_wikipedia",
            schema="wikipedia"
        )
        df.to_sql('pageviews_raw', con=insert_hook.get_sqlalchemy_engine(), if_exists='replace', chunksize=1000, index=False)


    create_pageviews_table = SQLExecuteQueryOperator(
        task_id="create_pageviews_table_task",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="""
            CREATE TABLE IF NOT EXISTS mysql.wikipedia.pageviews_raw (
                ds VARCHAR NOT NULL,
                page_id INT NOT NULL,
                view_count INT NOT NULL
            )"""
    )

    drop_target_table = SQLExecuteQueryOperator(
        task_id="drop_target_table_task",
        conn_id="mysql_wikipedia",
        do_xcom_push=True,
        sql="""DROP TABLE IF EXISTS mysql.wikipedia.target_entities"""
    )

    create_target_entities = SQLExecuteQueryOperator(
        task_id='create_target_entities_task',
        conn_id="trino_default",
        do_xcom_push=True,
        sql="""
            CREATE TABLE IF NOT EXISTS mysql.wikipedia.target_entities
            SELECT p.page_id, pr.view_count, 1 AS entity_type
            FROM mysql.wikipedia.categorylinks AS cl
                     INNER JOIN mysql.wikipedia.linktarget AS lt
                                ON lt.lt_id = cl.cl_target_id
                                    AND cl_type = 'page'
                     INNER JOIN mysql.wikipedia.page AS p
                                ON p.page_id = cl.cl_from
                                    AND p.page_namespace = 0
                     INNER JOIN mysql.wikipedia.pageview_rollup AS pr
                                ON pr.page_id = p.page_id
            WHERE from_utf8(lt_title) = 'Living_people'
            ORDER BY pr.view_count DESC
            LIMIT 10000
                """
    )

    drop_pageview_rollup = SQLExecuteQueryOperator(
        task_id="drop_pageview_rollup_task",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DROP TABLE IF EXISTS mysql.wikipedia.pageview_rollup",
    )

    pageview_rollup = SQLExecuteQueryOperator(
        task_id="pageview_rollup",
        conn_id="trino_default",
        do_xcom_push=True,
        outlets=[Asset("trino://localhost:8300/mysql/wikipedia/pageview_rollup")],
        sql="""
            CREATE TABLE mysql.wikipedia.pageview_rollup AS (
                SELECT page_id, SUM(view_count) AS view_count
                FROM mysql.wikipedia.pageviews_raw AS pr
                GROUP BY page_id
            )
            """,
    )

    pageviews_files = S3ListOperator(task_id="pageviews_files", bucket="wikipedia", aws_conn_id="default_storage", prefix="pageviews")

    process_pageviews_file.partial().expand(filename=pageviews_files.outlets) >> drop_pageview_rollup >> pageview_rollup >> create_target_entities

    create_pageviews_table >> pageviews_files
    drop_target_table >> create_target_entities

if __name__ == "__main__":
    dag.test()