from flask import Flask, render_template, request, redirect, Blueprint, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Database(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Database %r>' % self.id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


@app.route('/')
def index():
    return render_template("root.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/login', methods=['POST'] )
def login():
    
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()


    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))


    return redirect(url_for('profile'))

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: 
        flash('Email адрес занят')
        return redirect(url_for('signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    return 'Logout'

@app.route('/about')
def about():
    return render_template("about.html")

    
@app.route('/feed')
def feed():
    posts = Database.query.order_by(Database.date.desc()).all()
    return render_template("feed.html", posts = posts)

@app.route('/feed/id=<int:id>')
def post_on_feed(id):
    post = Database.query.get(id)
    return render_template("full_post.html", post = post)

@app.route('/create-article',methods=['POST','GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        article = Database(title = title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/feed')
        except Exception as e:
            return "АШЫБКА "+ e.__class__
    else:
        return render_template("create-article.html")


if __name__ == "__main__":
    app.run(debug=True)