from flask_wtf import Form
from wtforms import StringField, PasswordField, DateTimeField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import InputRequired,length

class RideRequestCreationForm(Form):
    # Flight Information (can be filled with Flightstats API)
    pickupAddress = StringField(validators=[
        InputRequired('Pickup address needs to be specified.'),
        
        
        ])
    airportLocation = StringField(validators=[
        InputRequired('Airport Location needs to be specified.'),
        
        ])
    flightLocalTime = DateTimeField(validators=[
        InputRequired('Flight Local Time needs to be specified. '),
        
        ])

    # Used to create Target Object
    earliest = DateTimeField(validators=[
        InputRequired('Earliest Arrival needs to be specified.'),
        
        ])

    latest = DateTimeField(validators=[
        InputRequired('Latest Arrival needs to be specified. '),
        
        ])


    # # TODO: Validate Airport
    # @staticmethod
    # def validate_airport(form, airportLocation):
    #     # Find Airport Code Library
    #     if airportLocation not in PACKAGE_NAME:
    #         raise ValidationError("Not a valid Airport Code")

    