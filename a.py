from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bokstore.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    books = Book.query.all()
    return render_template('dashboard.html', books=books, username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin'))
            db.session.add(admin)
            db.session.commit()
        if not Book.query.first():
            db.session.add_all([
                Book(title='Book 1', author='Author 1', price=10.99),
                Book(title='Book 2', author='Author 2', price=15.99)
            ])
            db.session.commit()
    app.run(debug=True)



# base.html

# <!doctype html>
# <html lang="en">
# <head>
#     <meta charset="utf-8">
#     <title>Bookstore</title>
# </head>
# <body>
#     {% block content %}{% endblock %}
# </body>
# </html>

# dashboard.html

# {% extends "base.html" %}
# {% block content %}
#   <h1>Welcome, {{ username }}!</h1>
#   <ul>
#     {% for book in books %}
#       <li>{{ book.title }} by {{ book.author }} - ${{ book.price }}</li>
#     {% endfor %}
#   </ul>
#   <a href="{{ url_for('logout') }}">Logout</a>
# {% endblock %}


# login.html

# <!doctype html>
# <html lang="en">
# <head>
#     <meta charset="utf-8">
#     <title>Login</title>
# </head>
# <body>
#     <form method="POST">
#         <p>
#             <label for="username">Username:</label><br>
#             <input type="text" name="username" required>
#         </p>
#         <p>
#             <label for="password">Password:</label><br>
#             <input type="password" name="password" required>
#         </p>
#         <p><input type="submit" value="Login"></p>
#     </form>
#     {% for message in get_flashed_messages() %}
#         <p>{{ message }}</p>
#     {% endfor %}
# </body>
# </html>