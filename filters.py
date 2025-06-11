"""Provide filters for querying close approaches and limit the generated results.

The `create_filters` function produces a collection of objects that is used by
the `query` method to generate a stream of `CloseApproach` objects that match
all of the desired criteria. The arguments to `create_filters` are provided by
the main module and originate from the user's command-line options.

This function can be thought to return a collection of instances of subclasses
of `AttributeFilter` - a 1-argument callable (on a `CloseApproach`) constructed
from a comparator (from the `operator` module), a reference value, and a class
method `get` that subclasses can override to fetch an attribute of interest from
the supplied `CloseApproach`.

The `limit` function simply limits the maximum number of values produced by an
iterator.

You'll edit this file in Tasks 3a and 3c.
"""
import operator
from itertools import islice

class UnsupportedCriterionError(NotImplementedError):
    """A filter criterion is unsupported."""


class AttributeFilter:
    """A general superclass for filters on comparable attributes.

    An `AttributeFilter` represents the search criteria pattern comparing some
    attribute of a close approach (or its attached NEO) to a reference value. It
    essentially functions as a callable predicate for whether a `CloseApproach`
    object satisfies the encoded criterion.

    It is constructed with a comparator operator and a reference value, and
    calling the filter (with __call__) executes `get(approach) OP value` (in
    infix notation).

    Concrete subclasses can override the `get` classmethod to provide custom
    behavior to fetch a desired attribute from the given `CloseApproach`.
    """
    def __init__(self, op, value):
        """Construct a new `AttributeFilter` from an binary predicate and a reference value.

        The reference value will be supplied as the second (right-hand side)
        argument to the operator function. For example, an `AttributeFilter`
        with `op=operator.le` and `value=10` will, when called on an approach,
        evaluate `some_attribute <= 10`.

        :param op: A 2-argument predicate comparator (such as `operator.le`).
        :param value: The reference value to compare against.
        """
        self.op = op
        self.value = value

    def __call__(self, approach):
        """Invoke `self(approach)`."""
        #compare the extracted attribute to the comparison value using the stored operator
        return self.op(self.get(approach), self.value)

    '''override this method in subclasses to extract the target attribute'''
    @classmethod
    def get(cls, approach):
        """Get an attribute of interest from a close approach.

        Concrete subclasses must override this method to get an attribute of
        interest from the supplied `CloseApproach`.

        :param approach: A `CloseApproach` on which to evaluate this filter.
        :return: The value of an attribute of interest, comparable to `self.value` via `self.op`.
        """
        raise UnsupportedCriterionError

    def __repr__(self):
        return f"{self.__class__.__name__}(op=operator.{self.op.__name__}, value={self.value})"


class DateFilter(AttributeFilter):
    '''filter by date: exact match, less than and greater than'''
    def __init__(self, op, value):
        super().__init__(op, value)

    @classmethod
    def get(cls, approach):
        return approach.time.date()

    @classmethod
    def on(cls, date):
        return cls(operator.eq, date)

    @classmethod
    def before(cls, end_date):
        return cls(operator.le, end_date)

    @classmethod
    def after(cls, start_date):
        return cls(operator.ge, start_date)


class DistanceFilter(AttributeFilter):
    '''filter by distance'''
    def __init__(self, op, value):
        super().__init__(op, value)

    @classmethod
    def get(cls, approach):
        return approach.distance

    @classmethod
    def distance_min_filter(cls, distance_min):
        return cls(operator.ge, distance_min)

    @classmethod
    def distance_max_filter(cls, distance_max):
        return cls(operator.le, distance_max)


class VelocityFilter(AttributeFilter):
    '''filter by velocity'''
    def __init__(self, op, value):
        super().__init__(op, value)

    @classmethod
    def get(cls, approach):
        return approach.velocity

    @classmethod
    def velocity_min_filter(cls, velocity_min):
        return cls(operator.ge, velocity_min)

    @classmethod
    def velocity_max_filter(cls, velocity_max):
        return cls(operator.le, velocity_max)


class DiameterFilter(AttributeFilter):
    '''filter by diameter'''
    def __init__(self, op, value):
        super().__init__(op, value)

    @classmethod
    def get(cls, approach):
        return approach.neo.diameter

    @classmethod
    def diameter_min_filter(cls, diameter_min):
        return cls(operator.ge, diameter_min)

    @classmethod
    def diameter_max_filter(cls, diameter_max):
        return cls(operator.le, diameter_max)


class HazardousFilter(AttributeFilter):
    '''filter opn whether hazardous or not'''
    def __init(self, op, value):
        super().__init__(op, value)

    @classmethod
    def get(cls, approach):
        return approach.neo.hazardous

    @classmethod
    def hazardous_filter(cls, hazardous):
        return cls(operator.eq, hazardous)


def create_filters(date=None, start_date=None, end_date=None,
                   distance_min=None, distance_max=None,
                   velocity_min=None, velocity_max=None,
                   diameter_min=None, diameter_max=None,
                   hazardous=None):
    """Create a collection of filters from user-specified criteria.

    Each of these arguments is provided by the main module with a value from the
    user's options at the command line. Each one corresponds to a different type
    of filter. For example, the `--date` option corresponds to the `date`
    argument, and represents a filter that selects close approaches that occured
    on exactly that given date. Similarly, the `--min-distance` option
    corresponds to the `distance_min` argument, and represents a filter that
    selects close approaches whose nominal approach distance is at least that
    far away from Earth. Each option is `None` if not specified at the command
    line (in particular, this means that the `--not-hazardous` flag results in
    `hazardous=False`, not to be confused with `hazardous=None`).

    The return value must be compatible with the `query` method of `NEODatabase`
    because the main module directly passes this result to that method. For now,
    this can be thought of as a collection of `AttributeFilter`s.

    :param date: A `date` on which a matching `CloseApproach` occurs.
    :param start_date: A `date` on or after which a matching `CloseApproach` occurs.
    :param end_date: A `date` on or before which a matching `CloseApproach` occurs.
    :param distance_min: A minimum nominal approach distance for a matching `CloseApproach`.
    :param distance_max: A maximum nominal approach distance for a matching `CloseApproach`.
    :param velocity_min: A minimum relative approach velocity for a matching `CloseApproach`.
    :param velocity_max: A maximum relative approach velocity for a matching `CloseApproach`.
    :param diameter_min: A minimum diameter of the NEO of a matching `CloseApproach`.
    :param diameter_max: A maximum diameter of the NEO of a matching `CloseApproach`.
    :param hazardous: Whether the NEO of a matching `CloseApproach` is potentially hazardous.
    :return: A collection of filters for use with `query`.
    """
    filters = []

    #date filters
    if date:
        filters.append(DateFilter.on(date))
    if start_date:
        filters.append(DateFilter.after(start_date))
    if end_date:
        filters.append(DateFilter.before(end_date))

    #distance filters
    if distance_min:
        filters.append(DistanceFilter.distance_min_filter(distance_min))
    if distance_max:
        filters.append(DistanceFilter.distance_max_filter(distance_max))

    #velocity filters
    if velocity_min:
        filters.append(VelocityFilter.velocity_min_filter(velocity_min))
    if velocity_max:
        filters.append(VelocityFilter.velocity_max_filter(velocity_max))

    #diameter filters
    if diameter_min:
        filters.append(DiameterFilter.diameter_min_filter(diameter_min))
    if diameter_max:
        filters.append(DiameterFilter.diameter_max_filter(diameter_max))

    #hazardous filter
    if hazardous is not None:
        filters.append(HazardousFilter.hazardous_filter(hazardous))

    return filters


def limit(iterator, n=None):
    """Produce a limited stream of values from an iterator.

    If `n` is 0 or None, don't limit the iterator at all.

    :param iterator: An iterator of values.
    :param n: The maximum number of values to produce.
    :yield: The first (at most) `n` values from the iterator.
    """
    n = None if n == 0 else n
    return islice(iterator, n)
