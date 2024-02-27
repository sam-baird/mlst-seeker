import dotenv
import os
import pandas as pd
import subprocess

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from . import datasets
from . import mlst

BATCH = 25  # number of samples to cache at a time

def update(cached_df: pd.DataFrame, metadata_df: pd.DataFrame, scheme) -> None:
    accessions = []
    if cached_df is None:
        create_table(scheme)
        accessions = metadata_df["accession"].to_list()
    else:
        uncached_df = metadata_df[~(metadata_df["biosample"].isin(cached_df["biosample"]))]
        accessions = uncached_df["accession"].to_list()
    batches = map(lambda i: accessions[i:i + BATCH], range(0, len(accessions), BATCH))
    create_table(scheme)
    num_caching = 0
    for batch in batches:
        num_caching += BATCH
        print(f"Caching {num_caching}/{len(accessions)}...")
        datasets.get_genomes(batch)
        mlst_df = mlst.perform_mlst(scheme)
        merged_df = mlst.merge_with_metadata(mlst_df, metadata_df)
        insert_rows(merged_df)

def create_table(scheme: str) -> None:
    client = bigquery.Client()
    table_id = get_table_id(scheme)
    try:
        client.get_table(table_id)
        print(f"{table_id} already exists")
        return
    except NotFound:
        pass
    schemes = subprocess.run("mlst --longlist", capture_output=True, text=True, shell=True).stdout
    for line in schemes.splitlines():
        if line.startswith(scheme):
            genes = line.split("\t")[1:]
            break
    print(genes)
    gene_cols = [bigquery.SchemaField(g, "STRING") for g in genes]
    schema = [
        bigquery.SchemaField("accession", "STRING"),
        bigquery.SchemaField("biosample", "STRING"),
        bigquery.SchemaField("source_database", "STRING"),
        bigquery.SchemaField("location", "STRING"),
        bigquery.SchemaField("collection_date", "STRING"),
        bigquery.SchemaField("scheme", "STRING"),
        bigquery.SchemaField("sequence_type", "STRING"),
        *gene_cols,
        bigquery.SchemaField("last_updated", "TIMESTAMP",
                             default_value_expression="CURRENT_TIMESTAMP"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)
    print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

def insert_rows(df: pd.DataFrame) -> None:
    client = bigquery.Client()
    scheme = df["scheme"].iloc[0]
    table_id = get_table_id(scheme)
    job = client.load_table_from_dataframe(df, table_id)
    job.result()

def get_table(scheme: str) -> pd.DataFrame:
    table_id = get_table_id(scheme)
    client = bigquery.Client()
    query = "SELECT * FROM {}".format(table_id)
    df = client.query(query).to_dataframe()
    return df

def get_table_id(scheme: str) -> str:
    dotenv.load_dotenv()
    project = os.getenv("GCP_PROJECT")
    table_id = f"{project}.mlst_seeker.{scheme}"
    return table_id

if __name__ == "__main__":
    create_table("mabscessus")
