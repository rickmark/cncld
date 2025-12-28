from datetime import datetime
from airflow import Asset
from airflow.sdk import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.definitions.param import ParamsDict, Param

default_args = {"owner": "rickmark"}

with DAG(
    dag_id="pageview_composite_pipeline",
    default_args=default_args,
    description="Extract target entities from categories",
    schedule="@daily",
    tags={"trino", "wikipedia"}
) as dag:


    drop_pagview_rollup = SQLExecuteQueryOperator(
        task_id="drop_pagview_rollup",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DROP TABLE IF EXISTS mysql.wikipedia.pagview_rollup",
    )

    pageview_rollup = SQLExecuteQueryOperator(
        task_id="pageview_rollup",
        conn_id="trino_default",
        do_xcom_push=True,
        outlets=[Asset("trino://localhost:8300/mysql/wikipedia/pageview_rollup")],
        sql="""
            CREATE TABLE mysql.wikipedia.pagview_rollup AS
            WITH pageview_rollup AS (SELECT page_id, SUM(view_count) AS view_count
                                     FROM mysql.wikipedia.pageviews_raw AS pr
                                     GROUP BY page_id)
            SELECT p.page_id, pr.view_count
            FROM pageview_rollup AS pr
            INNER JOIN mysql.wikipedia.page AS p
                ON p.page_id = pr.page_id
            INNER JOIN mysql.wikipedia.target_entities AS te
                ON te.page_id = p.page_id
        """,
    )


    drop_pagview_rollup << pageview_rollup

if __name__ == "__main__":
    dag.test()