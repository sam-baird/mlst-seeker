"""Entrypoint for program."""
from . import cli
from . import datasets


def main():
    options = cli.parse_args()
    reports = datasets.get_taxon_reports(options.organism)
    if options.cmd == "preview":
        print("Running preview")
    else:
        accessions = [r["accession"] for r in reports]
        datasets.get_genomes(accessions)

if __name__ == "__main__":
    main()
