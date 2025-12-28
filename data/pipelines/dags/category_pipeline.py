from datetime import datetime
from airflow import Asset
from airflow.sdk import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk.definitions.param import ParamsDict, Param

default_args = {"owner": "rickmark"}

with DAG(
    dag_id="category_pipeline",
    default_args=default_args,
    description="Extract target entities from categories",
    schedule="@daily",
    catchup=False,
    tags={"trino", "wikipedia"},
    params=ParamsDict({
            "person_category": Param(
        236283,
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
            CREATE TABLE mysql.wikipedia.target_entities AS
            WITH cat_list AS (
                WITH RECURSIVE category_tree (cl_from, cl_target_id) AS (
                    SELECT c.cl_from, c.cl_target_id
                    FROM mysql.wikipedia.categorylinks AS c
                    WHERE cl_from = {{params['person_category']}} -- Category "People"
            
                    UNION ALL
                    SELECT c.cl_from, c.cl_target_id
                    FROM mysql.wikipedia.categorylinks AS c
                    INNER JOIN category_tree AS t
                        ON t.cl_target_id = c.cl_from
                        AND c.cl_type = 'subcat'
                )
                SELECT {{params['person_category']}} AS cat_id
                UNION ALL
                SELECT ct.cl_target_id AS cat_id
                FROM category_tree AS ct
            )
            SELECT DISTINCT cl_from AS page_id, 1 AS entity_type
            FROM mysql.wikipedia.categorylinks AS c
            WHERE cl_target_id IN (SELECT cat_id FROM cat_list)
                AND cl_type = 'page'
                AND cl_from IN (SELECT page_id FROM mysql.wikipedia.page)
        """,
    )

    drop_target_entities >> person_categories

if __name__ == "__main__":
    dag.test()