class Luggages:
    """ Keeps track of luggage amount
    """

    _luggage_list = []

    def init(self):
        raise NotImplementedError

    def add(self, luggage: dict):
        """ Append a piece of luggage to self._luggage_list

        :param luggage:
        :return:
        """
        raise NotImplementedError

    def _get_count(self) -> int:
        """ Returns the count for luggages by counting all luggages in self._luggage_list.

        :return:
        """
        raise NotImplementedError

    def _get_weight(self) -> float:
        """ Returns the weight for luggages by accumulating all luggages in self._luggage_list.

        :return:
        """
        raise NotImplementedError

    def from_dict(self):
        """ Creates a Luggages class with a dict presentation of luggages.

        :return:
        """
        raise NotImplementedError

    def to_dict(self) -> dict:
        """ Returns a dict representation of all luggages
        Get value for "total_weight" by self._get_weight() and value for "total_count" by self._get_count().

        :return:
        """
        raise NotImplementedError

    def _add_luggages(self, luggage_storage):
        """ Add luggages from another luggage object

        :return:
        """
        raise NotImplementedError
