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
    schedule="@daily",  # Override to match your needs
    start_date=datetime(2022, 1, 1),
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


    delete_people = SQLExecuteQueryOperator(
        task_id="delete_people",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DELETE FROM mysql.wikipedia.target_entities WHERE entity_type = {{params['entity_type']}}",
    )

    drop_person_candidates = SQLExecuteQueryOperator(
        task_id="drop_person_candidates",
        conn_id="trino_default",
        do_xcom_push=True,
        sql="DROP TABLE IF EXISTS mysql.wikipedia.person_candidates"
    )

    person_categories = SQLExecuteQueryOperator(
        task_id="person_categories",
        conn_id="trino_default",
        do_xcom_push=True,
        outlets=[Asset("trino://localhost:8300/mysql/wikipedia/person_candidates")],
        sql="""
            CREATE TABLE mysql.wikipedia.person_candidates AS
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

    top_n_people = SQLExecuteQueryOperator(
        task_id="top_n_people",
        conn_id="trino_default",
        outlets=[Asset("trino://localhost:8300/mysql/wikipedia/target_entities")],
        do_xcom_push=True,
        sql=f"""
            INSERT INTO mysql.wikipedia.target_entities (page_id, entity_type)
            SELECT page_id, {{params['entity_type']}} 
            FROM mysql.wikipedia.person_candidates 
            INNER JOIN mysql.wikipedia.page USING (page_id)
            ORDER BY page_id 
            LIMIT {{params['top_n']}}
        """,
    )

    [drop_person_candidates, delete_people] >> person_categories >> top_n_people
