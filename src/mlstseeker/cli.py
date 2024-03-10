"""Parse command-line arguments."""
import argparse


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(
        prog="mlst-seeker",
        description="Find bacterial genomes on NCBI for a given multi-locus sequence type"
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action=argparse.BooleanOptionalAction,
        help="do not print log messages"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action=argparse.BooleanOptionalAction,
        help="print DEBUG-level log messages"
    )
    parser = parse_subcommands(parser)
    options = parser.parse_args()
    return options


def parse_subcommands(parser):
    """Add arguments for preview, fetch, and cache subcommands"""
    subparsers = parser.add_subparsers(dest="command")  # TODO: help msg
    subparsers.required = True
    subparsers.add_parser("preview")
    subparsers.add_parser("fetch")
    subparsers.add_parser("cache")

    for subcommand in ("preview", "fetch", "cache"):
        parser.add_argument(
            "-o",
            "--organism", 
            required=True,
            help="organism or NCBI taxonomy ID"
        )
        parser.add_argument(
            "-t",
            "--type",
            help="multi-locus sequence type (MLST)"
        )
        parser.add_argument(
            "-s",
            "--scheme",
            required=True,
            help="PubMLST scheme name"
        )

    for subcommand in ("preview", "fetch"):
        subparsers.choices[subcommand].add_argument(
            "--collect-start",
            help="earliest collection year"
        )

        subparsers.choices[subcommand].add_argument(
            "--collect-end",
            help="latest collection year"
        )
        
        subparsers.choices[subcommand].add_argument(
            "--location",
            help="geographic location of where sample was collected"
        )

    subparsers.choices["cache"].add_argument(
        "--cached-only",
        action=argparse.BooleanOptionalAction,
        help="only report cached MLST results"
    )

    return parser
