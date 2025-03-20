# Main flask
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_bootstrap import Bootstrap5

# Database control
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, ForeignKey
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Login and security
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import *


# APP with BOOTSTRAP
app = Flask(__name__)

"""--------------------------------------- Login Manager ---------------------------------------"""
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Replace with your user loading logic
    return User.query.get(int(user_id))
"""--------------------------------------- Login Manager ---------------------------------------"""



"""--------------------------------------- Bootstrap ---------------------------------------"""
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = 'bootstrap'
"""--------------------------------------- Bootstrap ---------------------------------------"""



"""--------------------------------------- Database ---------------------------------------"""
# DATABASE
class Base(DeclarativeBase):
    pass

# Configuration
db = SQLAlchemy(model_class=Base)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db.init_app(app)
"""--------------------------------------- Database---------------------------------------"""



"""--------------------------------------- Tables ---------------------------------------"""
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), unique=True)

    user_id = relationship("Cafe", back_populates="cafe")


class Cafe(db.Model):
    __tablename__ = 'cafe'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String(100))
    map_url: Mapped[str] = mapped_column(String(100))
    img_url: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(50))
    has_sockets: Mapped[bool] = mapped_column(Boolean, default=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, default=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_take_calls: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)  ### OPTIONAL FIELD EXAMPLE
    seats: Mapped[str] = mapped_column(String(25))
    coffee_price: Mapped[str] = mapped_column(String(25))

    cafe = relationship("User", back_populates="user_id")


"""--------------------------------------- Tables ---------------------------------------"""



"""--------------------------------------- Additional Functions ---------------------------------------"""
def get_cafe_list():
    return db.session.execute(db.select(Cafe)).scalars().all()

def get_table_by_attr(Entity, attribute, value):
    query = db.select(Entity).where(getattr(Entity, attribute) == value)
    return db.session.execute(query).scalar()

"""--------------------------------------- Additional Functions ---------------------------------------"""




"""--------------------------------------- Route Functions [START] ---------------------------------------"""
# ---------- HOME ---------- #
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", cafes=get_cafe_list())


# ---------- REGISTER ---------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        if get_table_by_attr(User, "email", register_form.email.data):
            flash("User already exists", "register_error")
        # NEW USER
        else:
            new_user = User()
            new_user.name = register_form.name.data
            new_user.email = register_form.email.data
            # Password security
            hashed_password = generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)
            new_user.password = hashed_password
            # ADD NEW_USER to DATABASE
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('home'))


    return render_template("register.html", register_form=register_form)


# ---------- LOGIN ---------- #
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        selected_user = get_table_by_attr(User, "email", form.email.data)
        if not selected_user:
            flash("Incorrect email", "login_error")
            redirect(url_for('login'))
        elif check_password_hash(selected_user.password, form.password.data):
            login_user(selected_user)
            return redirect(url_for('home'))
        else:
            flash("Incorrect password", "login_error")


    return render_template("login.html", form=form)


# ---------- LOGOUT ---------- #
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- CAFE DETAILS ---------- #
@app.route('/cafe-detail/<int:cafe_id>', methods=['GET', 'POST'])
def get_cafe_details(cafe_id):
    cafe = get_table_by_attr(Cafe, "id", cafe_id)
    return render_template("cafe-detail.html", cafe=cafe)


# ---------- ADD CAFE ---------- #
@app.route('/add_cafe', methods=['GET', 'POST'])
def add_cafe():
    add_cafe_form = AddCafe()

    if add_cafe_form.validate_on_submit():
        if current_user.is_authenticated:
            new_cafe = Cafe(
                name=add_cafe_form.name.data,
                user_id=current_user.id,
                map_url=add_cafe_form.map_url.data,
                img_url=add_cafe_form.img_url.data,
                location=add_cafe_form.location.data,
                has_sockets=add_cafe_form.has_sockets.data,
                has_toilet=add_cafe_form.has_toilet.data,
                has_wifi=add_cafe_form.has_wifi.data,
                can_take_calls=add_cafe_form.can_take_calls.data,
                seats=add_cafe_form.seats.data,
                coffee_price=add_cafe_form.coffee_price.data,
            )
            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for('home'))


        else:
            flash("Log in first, to add a cafe", "login_error")
            return redirect(url_for('login'))


    return render_template("add-cafe.html", add_cafe_form=add_cafe_form)


# ---------- UPDATE CAFE DETAILS ---------- #
@app.route("/change_cafe_details/<int:cafe_id>", methods=['GET', 'POST'])
def change_cafe_details(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)

    form = AddCafe()

    if request.method == 'GET':
        form.process(obj=cafe)
        form.submit.label.text = "Update Cafe"
        return render_template('edit-cafe.html', form=form, cafe=cafe)

    if form.validate_on_submit():
        for field_name, field in form._fields.items():
            if hasattr(cafe, field_name) and field_name != 'submit':
                if getattr(cafe, field_name) != field.data:
                    setattr(cafe, field_name, field.data)
        db.session.commit()
        return redirect(url_for('get_cafe_details', cafe_id=cafe_id))



@app.route('/delete_cafe/<int:cafe_id>', methods=['GET', 'POST'])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('home'))

"""--------------------------------------- Route Functions [END] ---------------------------------------"""



"""--------------------------------------- Run Application ---------------------------------------"""
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()

    app.run(debug=True)








