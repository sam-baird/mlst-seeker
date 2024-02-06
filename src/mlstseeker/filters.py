"""Filter taxon reports from the NCBI datasets API."""
import dateutil.parser
import pandas as pd

# mlst program uses column #3 to output sequence type
SEQUENCE_TYPE_COLUMN = 2

def filter_reports_by_location(reports: list[dict],
                               location: str) -> list[dict]:
    """Filter taxon reports from the NCBI datasets API based on the
    geo_loc_name BioSample attribute.

    Args:
        reports (list[dict]): taxon reports (from datasets.get_taxon_reports())
        location (str): geo_loc_name following INSDC qualifier formatting

    Returns:
        list[dict]: new reports list after filtering
    """
    filtered = []
    for report in reports:
        geo_loc_name = get_attribute(report, "geo_loc_name")
        if geo_loc_name and geo_loc_name.startswith(location):
            filtered.append(report)
    return filtered


def filter_reports_by_year(reports: list[dict],
                           start: str | None,
                           end: str | None) -> list[dict]:
    """Filter taxon reports from the NCBI datasets API based on the
    collection_date BioSample attribute.

    Args:
        reports (list[dict]): taxon reports (from datasets.get_taxon_reports())
        start (str | None): earliest collection year
        end (str | None): latest collection year

    Returns:
        list[dict]: new reports list after filtering
    """
    filtered = []
    unknown_date_count = 0
    for report in reports:
        date_str = get_attribute(report, "collection_date")
        try:
            year = dateutil.parser.parse(date_str).year
        except (ValueError, TypeError):
            # exclude if an unintelligible date
            unknown_date_count += 1
            continue
        if year and ((start is None or year >= start)
                        and (end is None or year <= end)):
            filtered.append(report)
    return filtered


def get_attribute(report: dict, attribute: str) -> str | None:
    """Return the value of a BioSample attribute from a taxon report.

    Args:
        report (dict): a taxon report 
        attribute (str): the attribute for which to retrieve a value

    Returns:
        str | None: attribute value (if it exists)
    """
    attributes = report["assembly_info"]["biosample"]["attributes"]
    record = next((item for item in attributes
                   if item["name"] == attribute), None)
    return record.get("value") if record else None


def filter_mlst(mlst: pd.DataFrame, sequence_type: str) -> pd.DataFrame:
    filtered_mlst = mlst[mlst.iloc[:, SEQUENCE_TYPE_COLUMN] == sequence_type]
    return filtered_mlst
