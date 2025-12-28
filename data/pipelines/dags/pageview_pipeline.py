import pandas as pd
import bz2
import re

from airflow.models import DAG
from airflow.sdk import task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

import logging
logging.basicConfig(level=logging.INFO)

PAGEVIEWS_FILE = re.compile(r"pageviews/pageviews-(\d+)-user.bz2")

with DAG(
    dag_id="pageview_pipeline",
    description="Upload pageview data to S3",
    schedule="@daily") as dag:

    @task(task_id='parse_s3_csv')
    def parse_s3_csv(item):
        logging.info(f"Parsing {item}")
        date_stamp = PAGEVIEWS_FILE.match(item)[1]

        s3_bucket = S3Hook(aws_conn_id='local_storage')

        input_data = s3_bucket.get_key(item, bucket_name='wikipedia').get()['Body']

        insert_hook = MySqlHook(
            mysql_conn_id="mysql_wikipedia",
            schema="wikipedia"
        )
        with  bz2.BZ2File(input_data, 'r') as stream:
            pageviews_raw: pd.DataFrame = pd.read_csv(stream, sep=' ', names=['project', 'page_title', 'page_id', 'access_method', 'view_count', 'view_sequence'])

        df = pageviews_raw.drop(['project', 'access_method', 'view_sequence', 'page_title'], axis=1)

        df = df[df['page_id'].notnull()]

        df = df.groupby('page_id').agg({'view_count': 'sum'}).reset_index()
        df['ds'] = f"{date_stamp[0:4]}-{date_stamp[4:6]}-01"
        df['page_id'] = df['page_id'].astype(int)

        df.to_sql('pageviews_raw', con=insert_hook.get_sqlalchemy_engine(), if_exists='replace', chunksize=1000, index=False)


    @task(task_id='create_pageviews_table_task')
    def for_each_pageview() -> list[str]:
        results: list = S3Hook(aws_conn_id='local_storage').list_keys(bucket_name='wikipedia', prefix='pageviews')
        for result in results:
            logging.info(f"Processing {result}")
        results = [ result for result in results if PAGEVIEWS_FILE.match(result) ]
        logging.info(f"Found {len(results)} pageviews")
        return results



    create_pageviews_table_task = SQLExecuteQueryOperator(
        task_id="drop_person_candidates",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="""
            CREATE TABLE IF NOT EXISTS mysql.wikipedia.pageviews_raw (
                ds VARCHAR NOT NULL,
                page_id INT NOT NULL,
                view_count INT NOT NULL
            )"""
    )

    create_pageviews_table_task >> parse_s3_csv.expand(item=for_each_pageview())

if __name__ == "__main__":
    dag.test()