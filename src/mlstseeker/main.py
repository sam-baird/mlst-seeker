"""Entrypoint for program."""
from . import cli
from . import datasets
from . import filtering


def main():
    options = cli.parse_args()
    reports = datasets.get_taxon_reports(options.organism)
    if options.collect_start or options.collect_end:
        start = options.collect_start
        end = options.collect_end
        reports = filtering.filter_reports_by_date(reports, start, end)
    if options.location:
        location = options.location
        reports = filtering.filter_reports_by_location(reports, location)
    if options.cmd == "preview":
        print("Running preview")
    else:
        accessions = [r["accession"] for r in reports]
        datasets.get_genomes(accessions)

if __name__ == "__main__":
    main()
