"""Parse command-line arguments."""
import argparse


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(
        prog="mlst-seeker",
        description="Find bacterial genomes on NCBI for a given multi-locus sequence type"
    )

    parser = parse_subcommands(parser)
    options = parser.parse_args()
    return options


def parse_subcommands(parser):
    """Add arguments for preview and fetch subcommands"""
    subparsers = parser.add_subparsers(dest="command")  # TODO: help msg
    subparsers.required = True
    subparsers.add_parser("preview")
    subparsers.add_parser("fetch")

    for _, subparser in subparsers.choices.items():
        subparser.add_argument(
            "-o",
            "--organism", 
            required=True,
            help="organism or NCBI taxonomy ID"
        )

        subparser.add_argument(
            "-t",
            "--type",
            help="multi-locus sequence type (MLST)"
        )

        subparser.add_argument(
            "-s",
            "--scheme",
            help="PubMLST scheme name"
        )

        subparser.add_argument(
            "--collect-start",
            help="earliest collection year"
        )

        subparser.add_argument(
            "--collect-end",
            help="latest collection year"
        )

        subparser.add_argument(
            "--location",
            help="geographic location of where sample was collected"
        )

    return parser
