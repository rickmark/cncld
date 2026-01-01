from datetime import timedelta

from airflow.sdk import task, DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

default_args = {
    'owner': 'rickmark',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

import ollama
import pydantic
import math
import dataclasses
import uuid
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import String, Float, Boolean, UUID



@dataclasses.dataclass
class InferenceContext:
    page_id: int
    page_title: str
    page_type: str
    recent_news: list[str]
    wikipedia_body: str

    def __str__(self):
        return f"{self.page_title}\n\n{self.wikipedia_body}\n\n# Recent News:\n{'\n'.join(self.recent_news)}"

class CancelInferenceResult(pydantic.BaseModel):
    is_toxic: bool
    revocable: bool
    rationale: str
    penance: str | None

@dataclasses.dataclass()
class CancelResult:
    context: InferenceContext
    result: CancelInferenceResult
    confidence: float

Base = declarative_base()
@dataclasses.dataclass()
class Result(Base):
    __tablename__ = 'the_list'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    title: Mapped[str] = mapped_column(String)
    canceled: Mapped[bool] = mapped_column(Boolean)
    revocable: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(String)
    penance: Mapped[str | None] = mapped_column(String, nullable=True)
    dimension: Mapped[str] = mapped_column(String)


    def __str__(self):
        return f"{self.title}: {'Canceled' if self.canceled else 'Not Canceled'} (confidence: {self.confidence:.2f})\nRationale: {self.rationale}{"\nPenance: " + self.penance if self.canceled else ""}\n\n"

SYSTEM_PROMPT = """
You are a competent, reasonable, investigative journalist.  You are a supporter of LGBT rights and evaluate the subjects of your investigation for their toxicity to the LGBT community.  You do not exclude trans individuals from this definition.  You are fair and understand that people can change over time.  You provide thoughtful rationale to your opinions and also provide an explanation of what if anything the subject of the investigation could do to no longer be considered toxic to the LGBT community.
"""

TASK_PROMPT = """
# Task

Given the following context, determine whether the subject of the investigation is toxic to the LGBT community.  Explain why you made this decision.  Determine whether the subject of the investigation can have this decision revoked.  Explain what steps would need to be taken to revoke this decision.

# Context

"""


with DAG(
    dag_id='infer_judgement',
    schedule='@daily',
    default_args=default_args,
) as dag:
    @task
    def get_inference_targets():
        return []

    @task
    def upload_result(inference_result: Result):
        conn = MySqlHook(conn_id='mysql_default')
        data = {k: v for k, v in inference_result.__dict__.items() if not k.startswith('_')}

        stmt = insert(inference_result.__table__).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[inference_result.__table__.c.title],
            set_= dict(
                canceled=stmt.excluded.canceled,
                revocable=stmt.excluded.canceled,
                rationale=stmt.excluded.canceled,
                penance=stmt.excluded.canceled,
                confidence=stmt.excluded.confidence,
                dimension=stmt.excluded.dimension
            )
        )
        conn.execute(stmt)

    @task
    def process_input(single_input: InferenceContext) -> CancelResult:
        client = ollama.Client(timeout=600.0)
        response = client.chat(
            model="llama4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": TASK_PROMPT + str(single_input)}
            ],
            logprobs=True,
            options={
                'num_predict': 2048
            },
            format=CancelInferenceResult.model_json_schema()
        )

        parsed_response = CancelInferenceResult.model_validate_json(response.message.content)

        return CancelResult(
            context=single_input,
            result=parsed_response,
            confidence=math.exp(response.logprobs[6].logprob)
        )

    @task
    def process_result(result_input_context: InferenceContext) -> Result:
        inference_result_context = process_input(result_input_context)
        return Result(
            title=inference_result_context.context.page_title.replace('_', ' '),
            canceled=inference_result_context.result.is_toxic,
            revocable=inference_result_context.result.revocable,
            rationale=inference_result_context.result.rationale,
            penance=inference_result_context.result.penance if inference_result_context.result.revocable else None,
            confidence=inference_result_context.confidence,
            dimension='lgbt'
        )

    @task
    def infer_judgement(llm_context):
        result = process_result(llm_context)
        upload_result(result)
        return result

    sql_task = SQLExecuteQueryOperator(
        task_id='query_targets',
        # Reference the connection ID created in the Airflow UI
        conn_id='mysql_airflow_conn',
        # The SQL query to execute
        sql=r"""
            SELECT
                col1,
                col2
            FROM
                table_name
            WHERE
                col1 = 'some_value';
            """,
        # Optional: set autocommit to True if needed
        autocommit=True
    )

    infer_judgement.partial().expand(llm_context=get_inference_targets())


if __name__ == "__main__":
    dag.test()