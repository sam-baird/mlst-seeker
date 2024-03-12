import pandas as pd

def apply(df: pd.DataFrame, options):
    if ((hasattr(options, "collect_start") and options.collect_start)
        or (hasattr(options, "collect_end") and options.collect_end)
    ):
        df = filter_by_year(df, start=int(options.collect_start))
    if hasattr(options, "location") and options.location:
        df = filter_by_location(df, options.location)
    return df


def filter_by_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """Return rows with the given location in `df`."""
    filtered = df[df["location"].notna()]
    filtered = filtered[filtered["location"].str.startswith(location)]
    return filtered


def filter_by_year(
        df: pd.DataFrame,
        start: int | None = None,
        end: int | None = None
    ) -> pd.DataFrame:
    """Return rows in between `start` and `end` years (inclusive) in `df`."""
    filtered = df.copy()
    filtered["year"] = pd.to_datetime(
        df["collection_date"],
        errors="coerce",
        format="ISO8601",
        utc=True,
    ).dt.year
    filtered = filtered[filtered["year"].notna()]
    filtered = filtered[(filtered["year"] >= start) | (filtered["year"] <= end)]
    filtered = filtered.drop(columns=["year"])
    return filtered


def filter_by_sequence_type(df: pd.DataFrame, sequence_type: str) -> pd.DataFrame:
    """Return rows with the given `sequence_type` in `df`."""
    return df[df["sequence_type"] == sequence_type]
