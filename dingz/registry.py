from typing import Generic, TypeVar, List, Dict, Optional


def organize_by_absolute_index(items):
    result = []
    for item in items:
        result.append((item['index']['absolute'], item))

    return result


T = TypeVar("T")


class BaseRegistry(Generic[T]):
    """
    A registry stores dimmers and shades and provides access ot them by a key.

    >>> shades.get(1) # get second shade

    Note, the absolute index remains the same, regardless of deactivation by the dip switch.
    So shade 1 is always the shade operated by output 2&3, even if it is the only shade.
    """
    _registry: Dict[int, T]

    def __init__(self, factory):
        """
        :param factory: call that is being used to create new instances,
                        will be given the key as argument:
                          - the key
                        the returned object must have a boolean attribute seen_state
                        which defines if this object will be returned when fetched externally.

        """
        self._registry = {}
        self._factory = factory

    def get(self, absolute_index) -> Optional[T]:
        """
        Get object in this registry by absolute_index.
        :param absolute_index: see BaseRegistry class docstring a for a definition of the absolute index
        :return: the obj, or None if disabled by DIP switch or the current state was never
                 fetched.
        """
        obj = self._get_or_create(absolute_index)
        if obj.seen_state:
            return obj
        else:
            return None

    def all(self) -> List[T]:
        """
        Return all known dimmers/shades.
        """
        return [o for o in self._registry.values() if o.seen_state]

    def _get_or_create(self, absolute_index) -> T:
        obj = self._registry.get(absolute_index)
        if obj is None:
            obj = self._registry[absolute_index] = self._factory(absolute_index)

        return obj
