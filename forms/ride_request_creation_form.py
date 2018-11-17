from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class RideRequestCreationForm(Form):
    pickupAddress = StringField(validators=[InputRequired('Pickup address needs to be specified. '))
    