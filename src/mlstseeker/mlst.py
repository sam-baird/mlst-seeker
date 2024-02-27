import pandas as pd
import subprocess

# mlst program uses column #3 to output sequence type
SEQUENCE_TYPE_COLUMN = 2


def perform_mlst(scheme: str) -> pd.DataFrame:
    mlst_command = f"""
        mlst \
        --scheme {scheme} \
        --legacy \
        --quiet \
        genomes/ncbi_dataset/*/*/* \
        > mlst.tsv
    """
    subprocess.run(mlst_command, check=True, shell=True)
    mlst_df = pd.read_csv("mlst.tsv", sep="\t", dtype="string",
                            on_bad_lines='warn')
    # extract GenBank accession from file path
    mlst_df["accession"] = mlst_df["FILE"].str.extract(r"(\bGCA_\d+\.\d+\b)")
    return mlst_df


def filter_mlst(mlst_df: pd.DataFrame, sequence_type: str) -> pd.DataFrame:
    filtered_mlst = mlst_df[mlst_df.iloc[:, SEQUENCE_TYPE_COLUMN] == sequence_type]
    return filtered_mlst

def merge_with_metadata(mlst_df: pd.DataFrame, metadata_df: pd.DataFrame) -> pd.DataFrame:
    genes = mlst_df.columns.to_list()[3:]
    merged_df = pd.merge(mlst_df, metadata_df, on="accession")
    new_cols = {
        "accession": "accession",
        "biosample": "biosample",
        "source_database": "source_database",
        "location": "location",
        "collection_date": "collection_date",
        "SCHEME": "scheme",
        "ST": "sequence_type",
        **{g: g for g in genes}
    }
    merged_df = merged_df[new_cols.keys()].rename(columns=new_cols)
    return merged_df