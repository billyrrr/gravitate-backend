class Luggages:
    """ Keeps track of luggage amount
    """

    def __init__(self):
        self._luggage_list = []

    def add(self, luggage: dict):
        """ Append a piece of luggage to self._luggage_list

        :param luggage:
        :return:
        """
        self._luggage_list.append(luggage)

    def _get_count(self) -> int:
        """ Returns the count for luggages by counting all luggages in self._luggage_list.

        :return:
        """
        return len(self._luggage_list)

    def _get_weight(self) -> float:
        """ Returns the weight for luggages by accumulating all luggages in self._luggage_list.

        :return:
        """
        weight = 0

        for i in self._luggage_list:
            for k, v in i.items():
                if k == "weight_in_lbs":
                    weight += v

        return weight

    @staticmethod
    def from_dict(d: dict):
        """ Creates a Luggages class with a dict presentation of luggages.

        :return:
        """

        # Obtain the list from dictionary
        # Create Luggages object
        # Use add_from_list
        # return the Luggages object that you created


        luggagelist = []
        index=0
        for a in d['luggages']:
            luggagelist.insert(index, a)
            index += 1
        updated = Luggages()
        updated.add_from_list(luggagelist)
        return updated


    def to_dict(self) -> dict:
        """ Returns a dict representation of all luggages
        Get value for "total_weight" by self._get_weight() and value for "total_count" by self._get_count().

        :return:
        """

        return {"luggages": self._luggage_list, "total_weight": self._get_weight(), "total_count": self._get_count()}

    def add_from_list(self, l: list):
        """ Add luggages from a list of luggages

        :return:
        """
        for s in l:
            self._luggage_list.append(s)

    def _add_luggages(self, luggages):
        """ Add luggages from another luggages object

        :return:
        """
        luggage_storage = luggages.get_luggage_list()
        for s in luggage_storage:
            self._luggage_list.append(s)

    def get_luggage_list(self):
        """ Return self._luggage_list so that another instance may add luggages in batch
                from this instance.

        :return:
        """
        return self._luggage_list.copy()
