"""Filter taxon reports from the NCBI datasets API."""
import pandas as pd

# mlst program uses column #3 to output sequence type
SEQUENCE_TYPE_COLUMN = 2

def filter_mlst(mlst: pd.DataFrame, sequence_type: str) -> pd.DataFrame:
    filtered_mlst = mlst[mlst.iloc[:, SEQUENCE_TYPE_COLUMN] == sequence_type]
    return filtered_mlst
