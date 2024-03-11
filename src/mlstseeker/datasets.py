"""Make calls to NCBI's datasets API."""
import gzip
import json
import logging
import shutil
import time
import os

import dateutil.parser
import requests
import zipfile

from tqdm.auto import tqdm
from typing import Optional, Self

BASEURL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha"
TIMEOUT = 30  # seconds until request timeout

class Report:
    """Dataset report from NCBI Genome database.

    View API spec here: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/rest-api/
    """
    NUMREPORTS = 1000 # can only get max 1000 records at a time
    def __init__(
            self,
            organism: Optional[str]=None,
            records: Optional[list[dict]]=None
        ):
        """Get dataset report for an `organism` or create one from `records`.

        If `organism` is provided, call the API and download all records
        for that organism. Otherwise use existing `records`.

        Args:
            organism (str, optional): Valid taxon. Defaults to None.
            records (list[dict], optional): Defaults to None.

        Raises:
            ValueError: Need to provide `organism` or `records` but not both.
        """
        if (organism is not None and records is not None):
            raise ValueError("Must provide organism or records")
        if (organism is None and records is None):
            raise ValueError("Must provide organism or records, but not both")
        if records is not None:
            self.records = records
            return
        self.records: list[dict] = []
        self.index = 0
        url = f"{BASEURL}/genome/taxon/{organism}/dataset_report"
        params = {
            "page_size": self.NUMREPORTS,
            "filters.assembly_source": "genbank"
        }
        num_fetched = 0
        total_count = 0
        logging.info("Downloading genome records from NCBI...")
        while True:
            response = requests.get(url, params=params, timeout=TIMEOUT)
            data = json.loads(response.text)
            total_count = data["total_count"]
            num_records = len(data["reports"])
            num_fetched += num_records
            logging.info("Downloaded %s of %s records", num_fetched, total_count)
            self.records.extend(data["reports"])
            page_token = data.get("next_page_token")
            if page_token is None:
                break
            params["page_token"] = page_token
            time.sleep(0.4)  # respect API request limit

    def filter_by_location(self, location: str) -> Self:
        """Filter based on the geo_loc_name BioSample attribute.

        Args:
            location (str): geo_loc_name following INSDC qualifier formatting

        Returns:
            list[dict]: new Report after filtering
        """
        filtered_records = []
        for record in self.records:
            geo_loc_name = self.get_attribute(record, "geo_loc_name")
            if geo_loc_name and geo_loc_name.startswith(location):
                filtered_records.append(record)
        return Report(records=filtered_records)
    
    def filter_by_year(self, start: int | None, end: int | None) -> Self:
        """Filter based on the collection_date BioSample attribute.

        Args:
            start (str | None): earliest collection year
            end (str | None): latest collection year

        Returns:
            list[dict]: new Report after filtering
        """
        filtered_records = []
        for record in self.records:
            date_str = self.get_attribute(record, "collection_date")
            try:
                year = dateutil.parser.parse(date_str).year
            except (ValueError, TypeError):
                # exclude if an unintelligible date
                continue
            if year and ((start is None or year >= start)
                            and (end is None or year <= end)):
                filtered_records.append(record)
        return Report(records=filtered_records)

    def get_attribute(self, record: dict, attribute: str) -> str | None:
        """Return the value of a BioSample attribute from a taxon record.

        Args:
            record (dict): a taxon record 
            attribute (str): the attribute for which to retrieve a value

        Returns:
            str | None: attribute value (if it exists)
        """
        try:
            attributes = record["assembly_info"]["biosample"]["attributes"]
        except KeyError:
            return None
        record = next((item for item in attributes
                      if item["name"] == attribute), None)
        return record.get("value") if record else None
    
    def get_metadata_dicts(self) -> list[dict]:
        """Get basic metadata as a list of dicts: accession, biosample,
        source_database, organism, location, and collection_date.
        """
        metadata_dicts = []
        for record in self.records:
            metadata = {}
            metadata["biosample"] = (
                record.get("assembly_info", {})
                .get("biosample", {})
                .get("accession")
            )
            metadata["accession"] = record.get("accession")
            metadata["source_database"] = record.get("source_database")
            metadata["organism"] = record.get("organism", {}).get("organism_name")
            metadata["location"] = self.get_attribute(record, "geo_loc_name")
            metadata["collection_date"] = self.get_attribute(record, "collection_date")
            metadata_dicts.append(metadata)
        return metadata_dicts
    
    def __iter__(self):
        """Create iterator for looping over records."""
        self.index = 0
        return self
    
    def __next__(self):
        """Return next record."""
        if self.index < len(self.records):
            record = self.records[self.index]
            self.index += 1
            return record
        raise StopIteration


def get_genomes(accessions: list[str]):
    """Download genomes for the given `accessions` from NCBI Genome database."""
    logging.info("Downloading %s genomes...", len(accessions))
    url = f"{BASEURL}/genome/download"
    obj = {
        "accessions": accessions,
        "include_annotation_type": ["GENOME_FASTA"]
    }
    response = requests.post(url, json=obj, stream=True, timeout=TIMEOUT)
    if response.status_code != 200:
        response.raise_for_status()

    # TODO: Show approximate total file size. No Content-Length header since
    # using chunked Transfer-Encoding, so can maybe base it on genome size?
    with tqdm.wrapattr(response.raw, "read") as raw_response:
        with open("genomes.zip.gz", "wb") as f:
            shutil.copyfileobj(raw_response, f)
    if os.path.exists("genomes"):
        shutil.rmtree("genomes")
    with gzip.open("genomes.zip.gz", "rb") as gz_file:
        with zipfile.ZipFile(gz_file, "r") as temp_file:
            temp_file.extractall("genomes")
