# Imports all necessary Flask modules
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQL Alchemy Configuration --Standard
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# Needed to secure application and database
app.secret_key = 'y337kGcys&zP3B'

# First Table (3 Columns - id, title, post)
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Numerical id list
    title = db.Column(db.String(120))            # Title
    body = db.Column(db.String(240))             # Blog post contained here
    pub_date = db.Column(db.DateTime)             # Time stamp
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    # Initilize Function - No clue what it does, but you need it
    def __init__(self, title, body, owner, pub_date = None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['username'] = user.username
                flash('welcome back, '+user.username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')

# Query to return full list of entries by Pub date
def getall():
    return Task.query.order_by(Task.pub_date.desc())

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    # posts = Blog.query.all()
    # Recent blog posts order to top.
    posts = Blog.query.order_by(Blog.pub_date.desc())

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("post.html", title=post.title, body=post.body, user=post.owner.username, pub_date=post.pub_date, user_id=post.owner_id)
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', entries=entries)

    return render_template('blog.html', posts=posts)


# Main App Route
@app.route('/', methods=['POST','GET'])     # Both methods needed, to filter requests
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# New Post App Route
@app.route('/new-post', methods=['POST','GET'])     # Both methods needed, to filter requests
def new_post():
    # Initialize variables as empty strings
    title_error = ''
    post_error = ''
    blog_title = ''
    task_name = ''
    if request.method == 'POST':
        blog_title = request.form['task'] # Grabs Title
        task_name = request.form['task1'] # Grabs Entry
        if blog_title == '':
            title_error = 'Please enter a title'   # Title Error Message
            blog_title = ''

        if task_name == '':
            post_error = 'You have to write something!'  # Post Error Message
            task_name = ''

        if not title_error and not post_error:              # If no errors are present
            owner = User.query.filter_by(username = session['username']).first()
            new_post = Blog(blog_title, task_name, owner)          # Sets up columns with values
            db.session.add(new_post)                        # Adds title, entry to database
            db.session.commit()                             # Commits all session changes
            new_id = new_post.id                            # Collects newly added post Id
            return redirect('/blog?id={0}'.format(new_id))  # String format to redirect to individual page (Use case 2)
 
    return render_template('new-post.html', title_error = title_error, post_error= post_error, blog_title = blog_title, task_name = task_name)


@app.route("/logout")
def logout():
    del session['username']
    return redirect("/login")

# I need to review what this really does....lol
if __name__ == '__main__':
    app.run()