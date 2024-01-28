import json

def create_counts_json(reports, filtered_reports) -> str:
    counts = {}
    counts["typed"] = {}
    counts["typed"]["filtered_matches"] = 0
    counts["typed"]["unfiltered_matches"] = 0
    counts["typed"]["filtered_overall"] = 0
    counts["typed"]["unfiltered_overall"] = 0
    counts["untyped"] = {}
    counts["untyped"]["filtered_overall"] = len(filtered_reports)
    counts["untyped"]["unfiltered_overall"] = len(reports)
    return json.dumps(counts, indent=2)
