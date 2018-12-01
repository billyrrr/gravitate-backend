# from flask_wtf import Form
# Note that Form is now imported from wtforms since it is more relevant to our usage of Form
from wtforms import Form, StringField, PasswordField, DateTimeField, BooleanField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import DataRequired,length

class RideRequestCreationForm():
    flightNumber = None

    airportLocation = None
    flightLocalTime = None

    # Cannot be autofilled
    pickupAddress = None

    # Halted
    # # Used to create Target Object
    # earliest = None
    # latest = None

    toEvent = None
    driverStatus = None


class RideRequestCreationValidateForm(Form):

    # Can be filled with Flightstats API
    flightNumber = StringField(u'Flight Number', validators=[
        DataRequired('Flight Number needs to be specified.'),
        
        ])

    airportLocation = StringField(u'Airport Location', validators=[
        DataRequired('Airport Location needs to be specified.'),
        
        ])
    flightLocalTime = DateTimeField(u'Flight Local Time', validators=[
        DataRequired('Flight Local Time needs to be specified. '),
        
        ])

    # Cannot be autofilled
    pickupAddress = StringField(u'Pickup Address', validators=[
        DataRequired('Pickup address needs to be specified.'),
        
        
        ])

    # Halted
    # # Used to create Target Object
    # earliest = DateTimeField(u'Earliest Arrival Time', validators=[
    #     DataRequired('Earliest Arrival needs to be specified.'),
        
    #     ])

    # latest = DateTimeField(u'Latest Arrival Time', validators=[
    #     DataRequired('Latest Arrival needs to be specified. '),
        
    #     ])

    toEvent = BooleanField(u'wether the ride is heading to the event')

    # TODO update design use case to be more specific about what driverStatus means
    # Since DataRequired is not compatible with value 'False', we won't have any validator for boolean
    # Try to fix their validator if you have time :) 
    # validators=[
    #       DataRequired('driverStatus (wether the user want to be considered as a driver for the event) needs to be specified. ')
    #       ]
    driverStatus = BooleanField(u'wether the user want to be considered as a driver for the event')

    # # TODO: Validate Airport
    # @staticmethod
    # def validate_airport(form, airportLocation):
    #     # Find Airport Code Library
    #     if airportLocation not in PACKAGE_NAME:
    #         raise ValidationError("Not a valid Airport Code")

    
