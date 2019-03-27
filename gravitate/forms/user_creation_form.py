from wtforms import Form, StringField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import DataRequired


class UserCreationForm:
    uid = None
    membership = None
    display_name = None
    phone_number = None
    photo_url = None
    pickupAddress = None

class UserCreationValidateForm(Form):

    # Can be filled with Flightstats API
    uid = StringField(u'UID', validators=[
        DataRequired('UID needs to be specified.')])

    phone_number = StringField(u'Phone Number',  validators=[
        DataRequired('Phone Number needs to be specified.')])

    membership = StringField(u'Membership', validators=[
        DataRequired('Membership needs to be specified.')])

    display_name = StringField(u'Name', validators=[
        DataRequired('Name needs to be specified.')])

    photo_url = StringField(u'Photo URL', validators=[
        DataRequired('Photo URL needs to be specified.')])

    pickupAddress = StringField(u'Pickup Address', validators=[
        DataRequired('Pickup Address needs to be specified.')])