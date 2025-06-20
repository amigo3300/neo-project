"""Extract data on near-Earth objects and close approaches from CSV and JSON
files.

The `load_neos` function extracts NEO data from a CSV file, formatted as
described in the project instructions, into a collection of `NearEarthObject`s.

The `load_approaches` function extracts close approach data from a JSON file,
formatted as described in the project instructions, into a collection of
`CloseApproach` objects.

The main module calls these functions with the arguments provided at the
command line, and uses the resulting collections to build an `NEODatabase`.

You'll edit this file in Task 2.
"""
import csv
import json
from pathlib import Path

from models import NearEarthObject, CloseApproach
from tests.test_data_files import PROJECT_ROOT

# create project and data directory paths
PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'
# paths to data files
neo_csv_path = DATA_ROOT / 'neos.csv'
cad_json_path = DATA_ROOT / 'cad.json'


def load_neos(neo_csv_path):
    """Read near-Earth object information from a CSV file.

    :param neo_csv_path: A path to a CSV file containing data about
    near-Earth objects.
    :return: A collection of `NearEarthObject`s.
    """
    neos = []
    with open(neo_csv_path, 'r') as infile:
        reader = csv.DictReader(infile)  # first row is automatically
        # fieldnames
        for row in reader:
            # create a NEO using dictionary keyword unpacking
            neos.append(NearEarthObject(**row))

    return neos


def load_approaches(cad_json_path):
    """Read close approach data from a JSON file.

    :param neo_csv_path: A path to a JSON file containing data about
    close approaches.
    :return: A collection of `CloseApproach`es.
    """
    close_approaches = []
    with open(cad_json_path, 'r') as file:
        close_approach_data = json.load(file)
        # iterate over the list of close approaches
        for close_approach in close_approach_data['data']:
            # each close approach is passed as a list to the CloseApproach
            # class constructor
            close_approaches.append(CloseApproach(close_approach))
    return close_approaches
