"""
The datasets feature is pre-built into the Astro Python SDK.
Datasets will be registered from any output tables, and the user
does not need to define any `outlets` explicitly. 

This DAG will create three datasets, one for the output of each task.
"""

import os
from datetime import datetime

import pandas as pd
from airflow.decorators import dag

from astro.files import File
from astro.sql import (
    load_file,
    transform,
)
from astro.sql.table import Table



SNOWFLAKE_CONN_ID = "snowflake_conn"
AWS_CONN_ID = "aws_conn"

# The first transformation combines data from the two source tables
@transform
def extract_data(homes1: Table, homes2: Table):
    return """
    SELECT *
    FROM {{homes1}}
    UNION
    SELECT *
    FROM {{homes2}}
    """

@dag(start_date=datetime(2021, 12, 1), schedule_interval="@daily", catchup=False, doc_md=__doc__)
def example_sdk_datasets():

    # Initial load of homes data csv's from S3 into Snowflake
    homes_data1 = load_file(
        task_id="load_homes1",
        input_file=File(path="s3://airflow-kenten/homes1.csv", conn_id=AWS_CONN_ID),
        output_table=Table(name="HOMES1", conn_id=SNOWFLAKE_CONN_ID),
        if_exists='replace'
    )

    homes_data2 = load_file(
        task_id="load_homes2",
        input_file=File(path="s3://airflow-kenten/homes2.csv", conn_id=AWS_CONN_ID),
        output_table=Table(name="HOMES2", conn_id=SNOWFLAKE_CONN_ID),
        if_exists='replace'
    )

    # Define task dependencies
    extracted_data = extract_data(
        homes1=homes_data1,
        homes2=homes_data2,
        output_table=Table(name="combined_homes_data"),
    )

example_sdk_datasets = example_sdk_datasets()