from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newf.db'
db = SQLAlchemy(app)


class Graf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(300), nullable=False)
    lastname = db.Column(db.String(300), nullable=False)


@app.route("/index")
@app.route("/")
def index():
    return render_template('index.html')


@app.route("/posts")
def posts():
    return render_template('posts.html')


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        
        post = Graf(firstname=firstname, lastname=lastname)
        
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
           return 'При вводе Фамилии произошла ошибка!'
            
    else:
        return render_template('create.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/abot")
def abot():
    return render_template('abot.html')

if __name__ == '__main__':
    app.run(debug=True)
    