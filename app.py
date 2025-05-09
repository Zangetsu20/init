from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from markupsafe import escape #XSS защита
#from flask_wtf.csrf import CSRFProtect #CSRF защита
#from flask_wtf.csrf import generate_csrf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newf.db'
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
#csrf = CSRFProtect(app) #csrf защита
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#@app.context_processor
#def inject_csrf():
#    return dict(csrf_token=generate_csrf)  

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id')) 

# Graf model
class Graf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(300), nullable=False)
    lastname = db.Column(db.String(300), nullable=False)
    d = db.Column(db.String(300), nullable=False)

# создание teachers таблицы
class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    
# создание teachers_subject таблицы
class Teacher_subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, nullable=False)

# создание subject таблицы
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.Text, nullable=False, unique=True)

# создание teachers_subject таблицы
class Teacher_subject_class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_subject_id = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Integer, nullable=False)    

# создание classes таблицы
class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.Text, nullable=False, unique=True)

# создание students таблицы
class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)   
    class_id = db.Column(db.Integer)
    
# создание grades таблицы
class Grades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    teacher_subject_class_id = db.Column(db.Integer, nullable=False)   
    grade = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)


# Create database tables (применить создание таблиц, должно быть в конце после создания всех таблиц)
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# запрос данных с таблицы
@app.route("/create")
def show_teachers():
    teachers = Teachers.query.all()
    return render_template('create.html', teachers=teachers)

#тест выода\редактирования
#@csrf.exempt #разкоментировать для отключения csrf 
@app.route('/update_teacher', methods=['POST'])
def update_teacher():
    try:
        data = request.get_json()
        
        # Проверка наличия всех необходимых полей
        if not data or 'id' not in data or 'field' not in data or 'value' not in data:
            return jsonify(error="Неверный формат данных: отсутствуют обязательные поля"), 400
        
        teacher = Teachers.query.get(data['id'])
        if not teacher:
            return jsonify(error="Учитель не найден"), 404
          
        # Обновляем поле 
        if data['field'] == 'first_name':
            teacher.first_name = escape(data['value'])
        elif data['field'] == 'last_name':
            teacher.last_name = escape(data['value']) 
        else:
            return jsonify(error="Недопустимое поле"), 400
        
        db.session.commit()
        return jsonify(success=True)
    
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500




#что это?
@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')

#данные к тестовой первой таблицы из БД
@app.route("/posts")
@login_required
def posts():
    # Получаем все записи Graf
    posts = Graf.query.all()
    
        # Проверяем, есть ли у пользователя привязанный teacher_id
    if not current_user.teacher_id:
        flash('У вас нет привязанного профиля учителя', 'error')
        return redirect(url_for('index'))
    
    # Получаем связки teacher-subject для текущего учителя
    teacher_subjects = Teacher_subject.query.filter_by(teacher_id=current_user.teacher_id).all()
    
    subject_ids = [ts.subject_id for ts in teacher_subjects]
    subjects = Subjects.query.filter(Subjects.id.in_(subject_ids)).all()
    
    return render_template('posts.html', posts=posts, subjects=subjects)


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