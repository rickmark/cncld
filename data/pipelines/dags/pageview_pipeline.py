from airflow.models import DAG

with DAG(
    dag_id="pageview_pipeline",
    description="Upload pageview data to S3",
    schedule="@daily",
) as dag:
    pass
