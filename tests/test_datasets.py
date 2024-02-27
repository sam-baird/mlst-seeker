import pytest
import requests
from unittest.mock import patch, Mock
from src.mlstseeker.datasets import Report, TIMEOUT

class TestReport:

    @pytest.fixture
    def mock_response(self):
        response = Mock()
        response.text = '{"reports": [{"assembly_info": {"biosample": {"attributes": []}}}], "next_page_token": null}'
        return response

    @patch('src.mlstseeker.datasets.requests.get')
    def test_init_with_organism(self, mock_get, mock_response):
        mock_get.return_value = mock_response
        report = Report(organism="example_organism")
        assert len(report.records) == 1
        url = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/taxon/example_organism/dataset_report"
        mock_get.assert_called_once_with(url, params={"page_size": 1000}, timeout=TIMEOUT)

    @patch('src.mlstseeker.datasets.requests.get')
    def test_init_with_records(self, mock_get, mock_response):
        mock_get.return_value = mock_response
        records = [{"assembly_info": {"biosample": {"attributes": []}}}]
        report = Report(records=records)
        assert report.records == records
        mock_get.assert_not_called()

    @patch('src.mlstseeker.datasets.requests.get', side_effect=requests.exceptions.Timeout)
    def test_init_timeout_exception(self, _):
        with pytest.raises(requests.exceptions.Timeout):
            Report(organism="example_organism")

    def test_init_invalid_arguments(self):
        with pytest.raises(ValueError, match="Must provide organism or records"):
            Report()

    def test_filter_by_location(self):
        records = [
            {"assembly_info": {"biosample": {"attributes": [{"name": "geo_loc_name", "value": "USA"}]}}},
            {"assembly_info": {"biosample": {"attributes": [{"name": "geo_loc_name", "value": "Canada"}]}}},
        ]
        report = Report(records=records)
        filtered_report = report.filter_by_location("USA")
        assert len(filtered_report.records) == 1
        assert filtered_report.records[0]["assembly_info"]["biosample"]["attributes"][0]["value"] == "USA"

    def test_filter_by_year(self):
        records = self.build_records_from_dates(["2022-01-01", "2023-01-01"])
        report = Report(records=records)
        filtered_report = report.filter_by_year(start=2022, end=2022)
        assert len(filtered_report.records) == 1
        assert filtered_report.records[0]["assembly_info"]["biosample"]["attributes"][0]["value"] == "2022-01-01"

    def test_filter_by_year_with_invalid_date(self):
        records = self.build_records_from_dates(["invalid_date", "2023-01-01"])
        report = Report(records=records)
        filtered_report = report.filter_by_year(start=2022, end=2023)
        assert len(filtered_report.records) == 1
        assert filtered_report.records[0]["assembly_info"]["biosample"]["attributes"][0]["value"] == "2023-01-01"

    def test_filter_by_year_with_missing_date(self):
        records = self.build_records_from_dates(["2023-01-01"])
        records.append({"assembly_info": {"biosample": {"attributes": []}}})
        report = Report(records=records)
        filtered_report = report.filter_by_year(start=2022, end=2023)
        assert len(filtered_report.records) == 1
        assert filtered_report.records[0]["assembly_info"]["biosample"]["attributes"][0]["value"] == "2023-01-01"

    def test_filter_by_year_with_same_start_and_end(self):
        records = self.build_records_from_dates(["2022-01-01", "2022-02-01"])
        report = Report(records=records)
        filtered_report = report.filter_by_year(start=2022, end=2022)
        assert len(filtered_report.records) == 2

    def test_filter_by_year_with_end_before_start(self):
        records = self.build_records_from_dates(["2022-01-01", "2022-02-01"])
        report = Report(records=records)
        filtered_report = report.filter_by_year(start=2023, end=2022)
        assert len(filtered_report.records) == 0

    def test_get_attribute(self):
        record = {"assembly_info": {"biosample": {"attributes": [{"name": "attribute1", "value": "value1"}]}}}
        report = Report(records=[record])
        attribute_value = report.get_attribute(record, "attribute1")
        assert attribute_value == "value1"

    def test_get_attribute_not_found(self):
        record = {"assembly_info": {"biosample": {"attributes": [{"name": "attribute1", "value": "value1"}]}}}
        report = Report(records=[record])
        attribute_value = report.get_attribute(record, "attribute2")
        assert attribute_value is None

    def build_records_from_dates(self, dates):
        """Helper method for creating record lists more easily"""
        records = []
        for date in dates:
            record = {
                "assembly_info": {"biosample": {"attributes": [{"name": "collection_date", "value": date}]}}}
            records.append(record)
        return records