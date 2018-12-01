from flask_wtf import Form
from wtforms import StringField, PasswordField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import InputRequired,length

class UserCreationForm():
    uid = None
    membership = None
    fullName = None
    phoneNumber = None
    picture = None

class UserCreationValidateForm(Form):

    # Can be filled with Flightstats API
    uid = StringField(u'UID', validators=[
        InputRequired('UID needs to be specified.')])

    phoneNumber = StringField(u'Phone Number',  validators=[
        InputRequired('Phone Number needs to be specified.')])

    membership = StringField(u'Membership', validators=[
        InputRequired('Membership needs to be specified.')])

    fullName = StringField(u'Name', validators=[
        InputRequired('Name needs to be specified.')])