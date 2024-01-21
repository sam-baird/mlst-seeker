"""Make calls to NCBI's datasets API."""
import json
import shutil
import time
import requests


BASEURL = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha"
TIMEOUT = 30  # seconds until request timeout
NUMREPORTS = 1000 # can only get max 1000 records at a time


def get_taxon_reports(organism):
    url = f"{BASEURL}/genome/taxon/{organism}/dataset_report"
    params = {"page_size": NUMREPORTS}
    reports = []
    while True:
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
        except requests.exceptions.Timeout:
            print("Failed to connect to NCBI datasets API")
        data = json.loads(response.text)
        reports.extend(data["reports"])
        page_token = data.get("next_page_token")
        if page_token is None:
            break
        params["page_token"] = page_token
        time.sleep(0.4)  # respect API request limit
    return reports


def get_genomes(accessions):
    url = f"{BASEURL}/genome/download"
    obj = {
        "accessions": accessions,
        "include_annotation_type": ["GENOME_FASTA"]
    }
    with requests.post(url, json=obj, stream=True, timeout=TIMEOUT) as response:
        response.raise_for_status()
        with open("genomes.zip", "wb") as f:
            shutil.copyfileobj(response.raw, f)
