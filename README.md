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
`"typed"` includes includes genomes that have already had MLST performed. In the above example, `"unfiltered matches"` indicates there are 412 ST5 genomes in the whole dataset, and `"filtered_matches"` indicates 4 of those genomes have metadata that match our location and collection date criteria. `"untyped"` includes genomes on NCBI that have not had MLST performed, which is only 1 genome in this case.

To download the 4 genome matches to a `genomes` directory and output a summary TSV, replace `preview` with `fetch`. This will also download the 1 untyped genome and perform MLST on it unless the `--cached-only` option is used.
```bash
% mlst-seeker fetch \
    --organism "Mycobacteroides abscessus" \
    --type 5 \
    --scheme mabscessus \
    --location USA \
    --collect-start 2020 \
    --quiet
        accession       biosample       source_database location        collection_date scheme  sequence_type   argH    cya     gnd     murC    pta     purH    rpoB    last_updated    organism        year
17      GCA_017183895.1 SAMN16828770    SOURCE_DATABASE_GENBANK USA: Philadelphia, PA   2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-26 22:06:31.776969+00:00        Mycobacteroides abscessus subsp. abscessus    2020.0
34      GCA_017175945.1 SAMN16839166    SOURCE_DATABASE_GENBANK USA: Dallas, TX 2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-27 00:45:10.189040+00:00        Mycobacteroides abscessus subsp. abscessus    2020.0
45      GCA_017183875.1 SAMN16828771    SOURCE_DATABASE_GENBANK USA: Philadelphia, PA   2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-26 22:06:31.776969+00:00        Mycobacteroides abscessus subsp. abscessus    2020.0
51      GCA_017175975.1 SAMN16839163    SOURCE_DATABASE_GENBANK USA: Charleston, SC     2020    mabscessus      5       3       1       4       3       1       2       1       2024-02-27 01:03:56.867363+00:00        Mycobacteroides abscessus subsp. abscessus    2020.0
0       GCA_900134485.1 SAMEA2275688    SOURCE_DATABASE_GENBANK United Kingdom  2010    mabscessus      5       3       1       4       3       1       2       1               Mycobacteroides abscessus subsp. abscessus
```
