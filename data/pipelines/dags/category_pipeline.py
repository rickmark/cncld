from datetime import datetime
from airflow import Asset
from airflow.sdk import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.definitions.param import ParamsDict, Param

default_args = {
    'owner': 'rickmark',
}


with DAG(
    dag_id="category_pipeline",
    default_args=default_args,
    description="Extract target entities from categories",
    schedule="@daily",
    tags={"trino", "wikipedia"},
    params=ParamsDict({
            "person_category": Param(
        173,
                type="integer",
            ),
            "top_n": Param(
                1000,
                type="integer",
            ),
            "entity_type": Param(
                1,
                type="integer",
            )
        })
) as dag:


    drop_target_entities = SQLExecuteQueryOperator(
        task_id="delete_people",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DROP TABLE IF EXISTS mysql.wikipedia.target_entities",
    )

    person_categories = SQLExecuteQueryOperator(
        task_id="target_entities",
        conn_id="trino_default",
        do_xcom_push=True,
        outlets=[Asset("trino://localhost:8300/mysql/wikipedia/target_entities")],
        sql="""
            CREATE TABLE IF NOT EXISTS mysql.wikipedia.target_entities AS
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
        """,
    )

    drop_target_entities >> person_categories

if __name__ == "__main__":
    dag.test()