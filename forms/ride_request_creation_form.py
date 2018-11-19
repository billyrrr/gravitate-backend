from flask_wtf import Form
from wtforms import StringField, PasswordField, DateTimeField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import InputRequired,length

class RideRequestCreationForm(Form):

    # Can be filled with Flightstats API
    flightNumber = StringField(u'Flight Number', validators=[
        InputRequired('Flight Number needs to be specified.'),

        
        ])

    airportLocation = StringField(u'Airport Location', validators=[
        InputRequired('Airport Location needs to be specified.'),
        
        ])
    flightLocalTime = DateTimeField(u'Flight Local Time', validators=[
        InputRequired('Flight Local Time needs to be specified. '),
        
        ])

    # Cannot be autofilled
    pickupAddress = StringField(u'Pickup Address', validators=[
        InputRequired('Pickup address needs to be specified.'),
        
        
        ])

    # Used to create Target Object
    earliest = DateTimeField(u'Earliest Arrival Time', validators=[
        InputRequired('Earliest Arrival needs to be specified.'),
        
        ])

    latest = DateTimeField(u'Latest Arrival Time', validators=[
        InputRequired('Latest Arrival needs to be specified. '),
        
        ])


    # # TODO: Validate Airport
    # @staticmethod
    # def validate_airport(form, airportLocation):
    #     # Find Airport Code Library
    #     if airportLocation not in PACKAGE_NAME:
    #         raise ValidationError("Not a valid Airport Code")

    
