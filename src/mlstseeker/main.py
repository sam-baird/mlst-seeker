"""Entrypoint for program."""
import copy
import dotenv
import logging
import logging.config
import pandas as pd
import sys

from google.cloud.exceptions import NotFound

from . import cache
from . import cli
from . import datasets
from . import mlst
from . import preview

pd.options.display.max_colwidth = 500


def main():
    logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})
    logging.basicConfig(level=logging.DEBUG)
    options = cli.parse_args()
    report = datasets.Report(options.organism)
    metadata = report.get_metadata_dicts()
    metadata_df = pd.DataFrame(metadata, dtype="string")
    filtered_report = copy.deepcopy(report)
    cached_df = None

    try:
        dotenv.load_dotenv()
        cached_df = cache.get_table(options.scheme)
        filtered_cached_df = cached_df.copy()
    except NotFound:
        print(f"{options.scheme} cache does not exist")

    if options.collect_start or options.collect_end:
        cli.validate_collect_dates(options)
        start = int(options.collect_start) if options.collect_start else None
        end = int(options.collect_end) if options.collect_end else None
        filtered_report = report.filter_by_year(start, end)
        filtered_cached_df = cache.filter_by_year(filtered_cached_df, start, end)
    if options.location:
        filtered_report = filtered_report.filter_by_location(options.location)
        filtered_cached_df = cache.filter_by_location(filtered_cached_df, options.location)

    filtered_metadata_df = pd.DataFrame(filtered_report.get_metadata_dicts(), dtype="string")
    if options.command == "preview":
        counts_json = preview.create_counts_json(
            metadata_df,
            filtered_metadata_df,
            cached_df,
            filtered_cached_df,
            options.type
        )
        print(counts_json)

    elif options.command == "cache":
        cache.add_to_cache(cached_df, metadata_df, options.scheme)
        cache.update_table(options.scheme, metadata_df)
    else:
        matches_df = filtered_cached_df[filtered_cached_df["sequence_type"] == options.type]
        if not options.cached_only:
            uncached_df = metadata_df[~(metadata_df["accession"].isin(cached_df["accession"]))]
            accessions = uncached_df["accession"].to_list()
            if accessions:
                logging.info("Found %s genomes on NCBI that have not been typed (use --cached-only to skip)", len(accessions))
                datasets.get_genomes(accessions)
                mlst_df = mlst.perform_mlst(options.scheme)
                mlst_df = mlst.filter_mlst(mlst_df, options.type)
                mlst_df = mlst.merge_with_metadata(mlst_df, metadata_df)
                mlst_df = mlst_df[mlst_df["sequence_type"] == options.type]
                matches_df = pd.concat([matches_df, mlst_df])
        logging.info("Found %s ST%s genomes", matches_df.shape[0], options.type)
        datasets.get_genomes(matches_df['accession'].to_list())
        matches_df.to_csv(sys.stdout, sep='\t')


if __name__ == "__main__":
    main()
