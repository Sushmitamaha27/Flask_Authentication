from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from flask_login import UserMixin,login_user,LoginManager,login_required,current_user,logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE TABLE IN DB
class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated)


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        email=request.form.get('email')
        result=db.session.execute(db.select(User).where(User.email==email))
        user=result.scalar()
        if user:
            flash("You Have already signed up with this email,log in instead!")
            return redirect(url_for('login'))

        #Hashing the salting the password entered by the user
        hash_and_sailted_password=generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user=User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=hash_and_sailted_password
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template("secrets.html",name=request.form.get('name'))
    return render_template("register.html",logged_in=current_user.is_authenticated)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist,Please try again!!")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password,password):
            flash("password incorrect,please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('secrets'))

    return render_template('login.html', logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html",logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('home')


@app.route('/download')
def download():
    return send_from_directory('static',path='files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
