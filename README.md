# mlst-seeker
Find bacterial genomes on NCBI's GenBank with a given multi-locus sequence type. Pre-determined MLST results are stored in a central BigQuery table.

## Basic usage examples
To preview the number of *Mycobacteroides abscessus* ST5 genomes collected in the USA since 2020:
```bash
% mlst-seeker preview \
    --organism "Mycobacteroides abscessus" \
    --type 5 \
    --scheme mabscessus \
    --location USA \
    --collect-start 2020 \
    --quiet  # hides logging output
{
  "typed": {
    "filtered_matches": 4,
    "unfiltered_matches": 412,
    "filtered_overall": 17,
    "unfiltered_overall": 2252
  },
  "untyped": {
    "filtered_overall": 0,
    "unfiltered_overall": 1
  }
}
```
To download the 4 `"filtered_matches"` to a `genomes` directory and output a summary TSV, replace `preview` with `fetch`. This will also download the 1 untyped genome, perform MLST on it, and include it if it's also a match.
```bash
% mlst-seeker fetch \
    --organism "Mycobacteroides abscessus" \
    --type 5 \
    --scheme mabscessus \
    --location USA \
    --collect-start 2020 \
    --quiet
accession       biosample       source_database location        collection_date scheme  sequence_type   argH    cya     gnd     murC    pta     purH    rpoB    last_updated    organism
GCA_017183895.1 SAMN16828770    SOURCE_DATABASE_GENBANK USA: Philadelphia, PA   2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-26 22:06:31.776969+00:00        Mycobacteroides abscessus subsp. abscessus
GCA_017175945.1 SAMN16839166    SOURCE_DATABASE_GENBANK USA: Dallas, TX 2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-27 00:45:10.189040+00:00        Mycobacteroides abscessus subsp. abscessus
GCA_017183875.1 SAMN16828771    SOURCE_DATABASE_GENBANK USA: Philadelphia, PA   2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-26 22:06:31.776969+00:00        Mycobacteroides abscessus subsp. abscessus
GCA_017175975.1 SAMN16839163    SOURCE_DATABASE_GENBANK USA: Charleston, SC     2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-27 01:03:56.867363+00:00        Mycobacteroides abscessus subsp. abscessus
```

## Installation
To install using Conda:
```
git clone https://github.com/sam-baird/mlst-seeker.git
cd mlst-seeker
conda env create --name mlst-seeker --file=environment.yml
conda activate mlst-seeker
```
Currently, a Google Cloud Platform project with BigQuery enabled is required to create and use MLST result caches. There are plans to create a central public API to make the below steps unnecessary.

To set up BigQuery, create an `.env` file with the name of your GCP project:
```
echo GCP_PROJECT="my-project" > .env
```
Then login using a user account (not recommended) or a [service account](https://cloud.google.com/bigquery/docs/use-service-accounts) with BigQuery read/write permissions.
```
gcloud auth application-default --impersonate-service-account my-service-account@my-project.iam.gserviceaccount.com login
```

## Usage
To view available subcommands and program-level options:
```
% mlst-seeker --help
usage: mlst-seeker [-h] [-q | --quiet | --no-quiet] [-v | --verbose | --no-verbose] {preview,fetch,cache} ...

Find bacterial genomes on NCBI for a given multi-locus sequence type

positional arguments:
  {preview,fetch,cache}
    preview             Output JSON with genome counts
    fetch               Download genomes and output TSV with MLST and metadata
    cache               Create or update BigQuery MLST cache

options:
  -h, --help            show this help message and exit
  -q, --quiet, --no-quiet
                        do not print log messages
  -v, --verbose, --no-verbose
                        print DEBUG-level log messages
```
All subcommands require the `--organism` option to specify the taxon, and the `--scheme` option to specify the PubMLST scheme. The preview and fetch subcommands require the `--type` option to specify the specific sequence type number. The `--collect-start` and/or `--collect-end` can be optionally applied to the `preview` and `fetch` subcommands to limit the collection year range, as well as `--location` to limit the location of collection. Note that many samples on GenBank are missing sample collection information, so applying these filters may filter out many samples of unkown origin.
### mlst-seeker preview
Use `mlst-seeker preview` to preview the number of genomes matching a given sequence type.
```
% mlst-seeker preview --help
usage: mlst-seeker preview [-h] -o ORGANISM [-t TYPE] -s SCHEME [--collect-start COLLECT_START] [--collect-end COLLECT_END] [--location LOCATION]

options:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism ORGANISM
                        organism or NCBI taxonomy ID
  -t TYPE, --type TYPE  multi-locus sequence type (MLST)
  -s SCHEME, --scheme SCHEME
                        PubMLST scheme name
  --collect-start COLLECT_START
                        earliest collection year
  --collect-end COLLECT_END
                        latest collection year
  --location LOCATION   geographic location of where sample was collected
```

This command outputs a JSON with the number of genomes on GenBank matching certain criteria:
- `"typed"` includes all genomes which have had MLST already performed
  - `"filtered_matches"`: number of MLST matches after applying any metadata filtering
  - `"unfiltered_matches"`: total number of MLST matches on GenBank
  - `"filtered_overall"`: number of total genomes (regardless of MLST) after applying metadata filtering
  - `"unfiltered_overall"`: total number of genomes on GenBank
- `"untyped"` includes any genomes on GenBank that have not had MLST performed (uncached)
  - `"filtered_overall"`: number of untyped genomes after applying metadata filtering
  - `"unfiltered overall"`: total number of untyped genomes on GenBank

### mlst-seeker fetch
Use `mlst-seeker fetch` to download genomes to a `genomes` directory matching a given sequence type. This command also outputs a TSV file with accession IDs, location, collection date, sequence type, allele numbers, species and other metadata.
```
% mlst-seeker fetch --help
usage: mlst-seeker fetch [-h] -o ORGANISM [-t TYPE] -s SCHEME [--collect-start COLLECT_START] [--collect-end COLLECT_END] [--location LOCATION] [--cached-only | --no-cached-only]

options:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism ORGANISM
                        organism or NCBI taxonomy ID
  -t TYPE, --type TYPE  multi-locus sequence type (MLST)
  -s SCHEME, --scheme SCHEME
                        PubMLST scheme name
  --collect-start COLLECT_START
                        earliest collection year
  --collect-end COLLECT_END
                        latest collection year
  --location LOCATION   geographic location of where sample was collected
  --cached-only, --no-cached-only
                        only report cached MLST results
```
### mlst-seeker cache
Use `mlst-seeker cache` to create a BigQuery cache with MLST results and metadata for a particular species and PubMLST scheme.

```
% mlst-seeker cache --help
usage: mlst-seeker cache [-h] -o ORGANISM -s SCHEME

options:
  -h, --help            show this help message and exit
  -o ORGANISM, --organism ORGANISM
                        organism or NCBI taxonomy ID
  -s SCHEME, --scheme SCHEME
                        PubMLST scheme name
```