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
