"""A database encapsulating collections of NEOs and their close approaches.

A `NEODatabase` holds an interconnected data set of NEOs and close approaches.
It provides methods to fetch an NEO by primary designation or by name, as well
as a method to query the set of close approaches that match a collection of
user-specified criteria.

Under normal circumstances, the main module creates one NEODatabase from the
data on NEOs and close approaches extracted by `extract.load_neos` and
`extract.load_approaches`.

You'll edit this file in Tasks 2 and 3.
"""
from extract import neo_csv_path
from filters import DistanceFilter
from models import NearEarthObject, CloseApproach


class NEODatabase:
    """A database of near-Earth objects and their close approaches.

    A `NEODatabase` contains a collection of NEOs and a collection of close
    approaches. It additionally maintains a few auxiliary data structures to
    help fetch NEOs by primary designation or by name and to help speed up
    querying for close approaches that match criteria.
    """

    def __init__(self, neos, approaches):
        """Create a new `NEODatabase`.

        As a precondition, this constructor assumes that the collections of
        NEOs and close approaches haven't yet been linked - that is, the
        `.approaches` attribute of each `NearEarthObject` resolves to an empty
        collection, and the `.neo` attribute of each `CloseApproach` is None.

        However, each `CloseApproach` has an attribute (`._designation`) that
        matches the `.designation` attribute of the corresponding NEO. This
        constructor modifies the supplied NEOs and close approaches to link
        them together - after it's done, the `.approaches` attribute of each
        NEO has a collection of that NEO's close approaches, and the `.neo`
        attribute of each close approach references the appropriate NEO.

        :param neos: A collection of `NearEarthObject`s.
        :param approaches: A collection of `CloseApproach`es.
        """
        self._neos = neos
        self._approaches = approaches
        # create fast lookup dictionaries by primary designation and name
        # (most NEOs don't have a name)
        self.neos_by_pdes = {neo.designation: neo for neo in self._neos}
        self.neos_by_name = {neo.name: neo for neo in self._neos}

        for approach in self._approaches:
            # link neos to approaches
            approach.neo = self.neos_by_pdes[approach._designation]
            # link approaches to neos
            self.neos_by_pdes[approach._designation].approaches.append(
                approach
            )

    def get_neo_by_designation(self, designation):
        """Find and return an NEO by its primary designation.

        If no match is found, return `None` instead.

        Each NEO in the data set has a unique primary designation, as a string.

        The matching is exact - check for spelling and capitalization if no
        match is found.

        :param designation: The primary designation of the NEO to search for.
        :return: The `NearEarthObject` with the desired primary designation,
        or `None`.
        """
        return self.neos_by_pdes.get(designation)

    def get_neo_by_name(self, name):
        """Find and return an NEO by its name.

        If no match is found, return `None` instead.

        Not every NEO in the data set has a name. No NEOs are associated with
        the empty string nor with the `None` singleton.

        The matching is exact - check for spelling and capitalization if no
        match is found.

        :param name: The name, as a string, of the NEO to search for.
        :return: The `NearEarthObject` with the desired name, or `None`.
        """
        return self.neos_by_name.get(name.capitalize())

    def query(self, filters=()):
        """Query close approaches to generate those that match a collection of
        filters.

        This generates a stream of `CloseApproach` objects that match all of
        the provided filters.

        If no arguments are provided, generate all known close approaches.

        The `CloseApproach` objects are generated in internal order, which
        isn't guaranteed to be sorted meaninfully, although is often sorted
        by time.

        :param filters: A collection of filters capturing user-specified
        criteria.
        :return: A stream of matching `CloseApproach` objects.
        """
        for approach in self._approaches:
            # all filters need to be True for an approach to be included
            # in the results
            if all([filter(approach) for filter in filters]):
                yield approach
