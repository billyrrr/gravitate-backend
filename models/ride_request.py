class RideRequest:
    
    
    """ Description	
        This class represents a RideRequest object
    
    """

    # TODO delete demo
    demoVariable = None


    def __init__(self, dictionary, demoParameter):

        """ Description
            Initializes a RideRequest Object with python dictionary


        :type self:
        :param self:
    
        :type dictionary:
        :param dictionary:
    
        :raises:
    
        :rtype:
        """        

        # TODO delete demo
        self.demoVariable = demoParameter

        for k, v in dictionary.items():
            setattr(self, k, v)

    def todict(self):
        return vars(self)