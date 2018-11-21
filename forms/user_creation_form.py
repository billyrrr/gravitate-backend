from flask_wtf import Form
from wtforms import StringField, PasswordField
#### DateTimeField does not have Timezone #### 


from wtforms.validators import InputRequired,length

class UserCreation(Form):

    # Can be filled with Flightstats API
    uid = StringField(u'UID', validators=[
        InputRequired('UID needs to be specified.'),

        
        ])

    membership = StringField(u'Membership', validators=[
        InputRequired('Membership needs to be specified.'),
        
        
        ])

    firstName = StringField(u'First Name', validators=[
        InputRequired('First Name needs to be specified.'),
        
        ])
        
    lastName = DateTimeField(u'Last Name', validators=[
        InputRequired('Last Name needs to be specified. '),
        
        ])

    image        = FileField(u'Image File', validators=[
        validators.regexp(u'^[^/\\]\.jpg$'),
        
        ])