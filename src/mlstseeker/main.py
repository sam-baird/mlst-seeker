"""Entrypoint for program."""
import copy
import gzip
import pandas as pd
import subprocess
import zipfile

from . import cli
from . import datasets
from . import filters
from . import preview

pd.options.display.max_colwidth = 500

def main():
    options = cli.parse_args()
    report = datasets.Report(options.organism)
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
    else:
        accessions = [r["accession"] for r in filtered_report]
        datasets.get_genomes(accessions)
        with gzip.open("genomes.zip.gz", "rb") as gz_file:
            with zipfile.ZipFile(gz_file, "r") as temp_file:
                temp_file.extractall("genomes")
        sequence_type, scheme = options.type.split('_')
        mlst_command = f"mlst --quiet --scheme {scheme} genomes/ncbi_dataset/*/*/* > mlst.tsv"
        subprocess.run(mlst_command, check=True, shell=True)
        mlst = pd.read_csv("mlst.tsv", sep="\t", header=None, on_bad_lines='warn')
        filtered_mlst = filters.filter_mlst(mlst, sequence_type)
        print(filtered_mlst.iloc[:, 0].to_string(index=False))


if __name__ == "__main__":
    main()
