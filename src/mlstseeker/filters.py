"""Filter taxon reports from the NCBI datasets API."""

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


def filter_reports_by_date(reports: list[dict],
                           start: str | None,
                           end: str | None) -> list[dict]:
    """Filter taxon reports from the NCBI datasets API based on the
    collection_date BioSample attribute.

    Args:
        reports (list[dict]): taxon reports (from datasets.get_taxon_reports())
        start (str | None): earliest collection date YYYY<-MM-DD>
        end (str | None): latest collection date YYYY<-MM-DD>

    Returns:
        list[dict]: new reports list after filtering
    """
    filtered = []
    for report in reports:
        date = get_attribute(report, "collection_date")
        if date and ((start is None or date >= start)
                     and (end is None or date <= end)):
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
