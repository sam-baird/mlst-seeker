"""Entrypoint for program."""
import copy
import pandas as pd

from google.cloud.exceptions import NotFound

from . import cache
from . import cli
from . import datasets
from . import mlst
from . import preview

pd.options.display.max_colwidth = 500

def main():
    options = cli.parse_args()
    report = datasets.Report(options.organism)
    metadata = report.get_metadata_dicts()
    metadata_df = pd.DataFrame(metadata, dtype="string")
    filtered_report = copy.deepcopy(report)
    if options.collect_start or options.collect_end:
        if options.collect_start and not options.collect_start.isnumeric():
            raise ValueError("Invalid start year")
        if options.collect_end and not options.collect_end.isnumeric():
            raise ValueError("Invalid end year")
        start = int(options.collect_start) if options.collect_start else None
        end = int(options.collect_end) if options.collect_end else None
        filtered_report = report.filter_by_year(start, end)
    if options.location:
        filtered_report = filtered_report.filter_by_location(options.location)
    if options.command == "preview":
        counts_json = preview.create_counts_json(report, filtered_report)
        print(counts_json)
    cached_df = None
    try:
        cached_df = cache.get_table(options.scheme)
    except NotFound:
        print(f"{options.scheme} cache does not exist")
    if options.command == "cache":
        cache.update(cached_df, metadata_df, options.scheme)
    else:
        accessions = [r["accession"] for r in filtered_report][:5]
        datasets.get_genomes(accessions)
        mlst_df = mlst.perform_mlst(options.scheme)
        if options.command == "fetch":
            mlst_df = mlst.filter_mlst(mlst_df, options.type)
        final_df = mlst.merge_with_metadata(mlst_df, metadata_df)
        print(final_df.to_string())
        print(final_df.dtypes)



if __name__ == "__main__":
    main()
