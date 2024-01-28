"""Entrypoint for program."""
from . import cli
from . import datasets
from . import filters
from . import preview


def main():
    options = cli.parse_args()
    reports = datasets.get_taxon_reports(options.organism)
    filtered_reports = []
    if options.collect_start or options.collect_end:
        start = options.collect_start
        end = options.collect_end
        filtered_reports = filters.filter_reports_by_date(reports, start, end)
    if options.location:
        location = options.location
        filtered_reports = filters.filter_reports_by_location(filtered_reports,
                                                              location)
    if options.cmd == "preview":
        counts_json = preview.create_counts_json(reports, filtered_reports)
        print(counts_json)
        print("Running preview")
    else:
        accessions = [r["accession"] for r in reports]
        datasets.get_genomes(accessions)

if __name__ == "__main__":
    main()
