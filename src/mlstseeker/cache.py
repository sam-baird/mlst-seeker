import dotenv
import logging
import os
import pandas as pd
import subprocess

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from . import datasets
from . import mlst

BATCH = 25  # number of samples to cache at a time
DATASET = "mlst_seeker"


def add_to_cache(cached_df: pd.DataFrame, metadata_df: pd.DataFrame, scheme: str) -> None:
    """Add new records to BigQuery for the given MLST scheme. Peform MLST
    for samples in `metadata_df` that are not already in `cached_df`,
    and add them to the BigQuery table.
    """
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
        logging.info("Caching %s/%s...", num_caching, len(accessions))
        datasets.get_genomes(batch)
        mlst_df = mlst.perform_mlst(scheme)
        merged_df = mlst.merge_with_metadata(mlst_df, metadata_df)
        insert_rows(merged_df)


def create_table(scheme: str) -> None:
    """Create a new BigQuery table for the given MLST scheme."""
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
        bigquery.SchemaField("organism", "STRING"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)
    print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))


def add_column_all_tables(column_name: str, dtype: str) -> None:
    """Add a column to all BigQuery tables with the given data type."""
    client = bigquery.Client()
    table_ids = get_all_table_ids()
    for table_id in table_ids:
        table = client.get_table(table_id)
        schema = table.schema
        schema.append(bigquery.SchemaField(column_name, dtype.upper()))
        table.schema = schema
        client.update_table(table, ["schema"])


def update_table(scheme: str, new_data: pd.DataFrame) -> None:
    """Update table corresponding to the given MLST scheme with values in
    DataFrame. Uses accession as the index.
    """
    client = bigquery.Client()
    df = get_table(scheme).set_index(["accession"])
    print(df.dtypes)
    print(new_data.dtypes)
    df.update(new_data.set_index("accession"))
    table_id = get_table_id(scheme)
    # overwrite existing table with updated table
    config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df, table_id, job_config=config)


def get_all_table_ids() -> list:
    """Get all BigQuery table IDs."""
    client = bigquery.Client()
    dataset_id = f"{os.getenv('GCP_PROJECT')}.{DATASET}"
    tables = client.list_tables(dataset_id)
    return [f"{t.project}.{t.dataset_id}.{t.table_id}" for t in tables]


def insert_rows(df: pd.DataFrame) -> None:
    """Insert rows in `df` to the corresponding BigQuery table."""
    client = bigquery.Client()
    scheme = df["scheme"].iloc[0]
    table_id = get_table_id(scheme)
    job = client.load_table_from_dataframe(df, table_id)
    job.result()


def get_table(scheme: str) -> pd.DataFrame:
    """Return DataFrame of BigQuery table for the given MLST scheme."""
    logging.info("Downloading cached MLST results...")
    table_id = get_table_id(scheme)
    client = bigquery.Client()
    query = "SELECT * FROM {}".format(table_id)
    df = client.query(query).to_dataframe().astype("string")
    logging.info("Downloaded %s cached MLST results", df.shape[0])
    return df


def get_table_id(scheme: str) -> str:
    """Return the BigQuery table ID for the given MLST scheme."""
    table_id = f"{os.getenv('GCP_PROJECT')}.{DATASET}.{scheme}"
    return table_id


def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """Return rows with the given location in `df`."""
    filtered = df[df["location"].notna()]
    filtered = filtered[filtered["location"].str.startswith(location)]
    return filtered


def filter_by_year(df: pd.DataFrame, start: int | None, end: int | None) -> pd.DataFrame:
    """Return rows in between `start` and `end` years (inclusive) in `df`."""
    filtered = df.copy()
    filtered["year"] = pd.to_datetime(df["collection_date"], errors="coerce").dt.year
    filtered = filtered[filtered["year"].notna()]
    filtered = filtered[filtered["year"] >= start | filtered["year"] <= end]
    filtered.drop(columns="year")
    return filtered


def filter_by_sequence_type(df: pd.DataFrame, sequence_type: str) -> pd.DataFrame:
    """Return rows with the given `sequence_type` in `df`."""
    return df[df["sequence_type"] == sequence_type]


if __name__ == "__main__":
    dotenv.load_dotenv()
    print(add_column_all_tables("organism", "STRING"))
