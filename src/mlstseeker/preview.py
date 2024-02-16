import json

def create_counts_json(report, filtered_report) -> str:
    counts = {}
    counts["typed"] = {}
    counts["typed"]["filtered_matches"] = 0
    counts["typed"]["unfiltered_matches"] = 0
    counts["typed"]["filtered_overall"] = 0
    counts["typed"]["unfiltered_overall"] = 0
    counts["untyped"] = {}
    counts["untyped"]["filtered_overall"] = len(filtered_report.records)
    counts["untyped"]["unfiltered_overall"] = len(report.records)
    return json.dumps(counts, indent=2)
