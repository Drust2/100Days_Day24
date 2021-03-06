from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Creating a login manager
login_manager = LoginManager()
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()

# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html", logged_in = current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        to_hash = request.form.get("password")
        # Check if there exists the input email
        already_exists = User.query.filter_by(email=request.form.get("email")).first()
        if already_exists:
            flash("This email already exists in our database. Please login instead")
            return redirect(url_for('login'))
        new_user = User(
                email = request.form.get("email"),
                password = generate_password_hash(password=to_hash, method='pbkdf2:sha256', salt_length=8),
                name = request.form.get("name")
            )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/secrets')
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form.get("email")
        login_pwd = request.form.get("password")
        print(f"{user_email} - {login_pwd}")
        
        actual_user = User.query.filter_by(email=user_email).first()
        
        if not actual_user:
            flash("The entered email does not exist in our database")
            return redirect(url_for('login'))
        
        if check_password_hash(actual_user.password, login_pwd):            
            login_user(actual_user)
            return redirect(url_for('secrets'))
        else:
            flash("Incorrect password")
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", username=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', filename='files/cheat_sheet.pdf')


if __name__ == "__main__":
    # app.run()
    app.run(debug=True)
