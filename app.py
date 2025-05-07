from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newf.db'
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Graf model
class Graf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(300), nullable=False)
    lastname = db.Column(db.String(300), nullable=False)
    d = db.Column(db.String(300), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/posts")
@login_required
def posts():
    posts = Graf.query.all()
    return render_template('posts.html', posts=posts)

@app.route("/create", methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        d = request.form['d']
        
        post = Graf(firstname=firstname, lastname=lastname, d=d)
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Данные успешно добавлены!', 'success')
            return redirect('/')
        except:
            flash('При добавлении данных произошла ошибка!', 'error')
            return render_template('create.html')
            
    return render_template('create.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/abot")
def abot():
    return render_template('abot.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято!', 'error')
            return render_template('register.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно! Пожалуйста, войдите.', 'success')
            return redirect(url_for('login'))
        except:
            flash('При регистрации произошла ошибка!', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль!', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)