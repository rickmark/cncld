from __future__ import annotations

import datetime
import os
import textwrap

import pendulum

from airflow.sdk import DAG, task

LATESET_WIKI_DUMPS_PATH = "https://dumps.wikimedia.org/enwiki/latest/"

with DAG(
    "ingest_latest_wikipedia_dump",
    description="Ingest the latest Wikipedia dump into the database.",
    schedule="*/1 * * * *",
    catchup=False,
    tags=["wikipedia"],
) as dag:
    pass