import json
import pandas as pd

from . import cache

def create_counts_json(
        metadata_df: pd.DataFrame,
        filtered_metadata_df: pd.DataFrame,
        cached_df: pd.DataFrame,
        filtered_cached_df: pd.DataFrame,
        sequence_type: str) -> str:

    if sequence_type is not None:
        cached_filtered_matches = cache.filter_by_sequence_type(
            filtered_cached_df,
            sequence_type
        ).shape[0]
        cached_unfiltered_matches = cache.filter_by_sequence_type(
            cached_df,
            sequence_type
        ).shape[0]
    else:
        cached_filtered_matches = cached_df.shape[0]
        cached_unfiltered_matches = filtered_cached_df.shape[0]
    print(metadata_df.shape[0])
    mask = ~(metadata_df["biosample"].isin(cached_df["biosample"]))
    uncached_df = metadata_df.loc[mask]
    mask = ~(filtered_metadata_df["biosample"].isin(filtered_cached_df["biosample"]))
    uncached_filtered_df = filtered_metadata_df.loc[mask]

    counts = {}
    counts["typed"] = {}
    counts["typed"]["filtered_matches"] = cached_filtered_matches
    counts["typed"]["unfiltered_matches"] = cached_unfiltered_matches
    counts["typed"]["filtered_overall"] = filtered_cached_df.shape[0]
    counts["typed"]["unfiltered_overall"] = cached_df.shape[0]
    counts["untyped"] = {}
    counts["untyped"]["filtered_overall"] = uncached_filtered_df.shape[0]
    counts["untyped"]["unfiltered_overall"] = uncached_df.shape[0]
    return json.dumps(counts, indent=2)
