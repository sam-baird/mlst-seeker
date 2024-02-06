"""Entrypoint for program."""
from . import cli
from . import datasets
from . import filters
from . import preview


def main():
    options = cli.parse_args()
    reports = datasets.get_taxon_reports(options.organism)
    filtered_reports = reports
    if options.collect_start or options.collect_end:
        if options.collect_start and not options.collect_start.isnumeric():
            raise ValueError("Invalid start year")
        if options.collect_end and not options.collect_end.isnumeric():
            raise ValueError("Invalid end year")
        start = int(options.collect_start) if options.collect_start else None
        end = int(options.collect_end) if options.collect_end else None
        filtered_reports = filters.filter_reports_by_year(reports, start, end)
    if options.location:
        location = options.location
        filtered_reports = filters.filter_reports_by_location(filtered_reports,
                                                              location)
    if options.command == "preview":
        counts_json = preview.create_counts_json(reports, filtered_reports)
        print(counts_json)
        print("Running preview")
    else:
        accessions = [r["accession"] for r in reports]
        datasets.get_genomes(accessions)

if __name__ == "__main__":
    main()
