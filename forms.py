from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, URLField, BooleanField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddCafe(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    map_url = URLField('Map URL', validators=[DataRequired()])
    img_url = URLField('Image URL', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    has_sockets = BooleanField('Sockets?')
    has_toilet = BooleanField('Toilets?')
    has_wifi = BooleanField('Wifi?')
    can_take_calls = BooleanField('Taking Calls?')
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])

    submit = SubmitField('Add Cafe')



    # name: Mapped[str] = mapped_column(String(100))
    # map_url: Mapped[str] = mapped_column(String(100), unique=True)
    # img_url: Mapped[str] = mapped_column(String(100), unique=True)
    # location: Mapped[str] = mapped_column(String(50))
    # has_sockets: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    # has_toilet: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    # has_wifi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # can_take_calls: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    # seats: Mapped[str] = mapped_column(String(25))
    # coffee_price: Mapped[str] = mapped_column(String(25))





