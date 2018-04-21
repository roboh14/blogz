# Imports all necessary Flask modules
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQL Alchemy Configuration --Standard
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# Needed to secure application and database
app.secret_key = 'y337kGcys&zP3B'

# First Table (3 Columns - id, title, post)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Numerical id list
    btitle = db.Column(db.String(120))            # Title
    entry = db.Column(db.String(240))             # Blog post contained here
    pub_date = db.Column(db.DateTime)             # Time stamp

    # Initilize Function - No clue what it does, but you need it
    def __init__(self, btitle, entry, pub_date = None):
        self.btitle = btitle
        self.entry = entry
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

# Query to return full list of entries by Pub date
def getall():
    return Task.query.order_by(Task.pub_date.desc())


# Main App Route
@app.route('/', methods=['POST','GET'])     # Both methods needed, to filter requests
def index():
    return render_template('entry.html', title = "Build-a-Blog!", allblogs = getall())  # This populates main blog page



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
            new_post = Task(blog_title, task_name)          # Sets up columns with values
            db.session.add(new_post)                        # Adds title, entry to database
            db.session.commit()                             # Commits all session changes
            new_id = new_post.id                            # Collects newly added post Id
            return redirect('/blog?id={0}'.format(new_id))  # String format to redirect to individual page (Use case 2)
 
    return render_template('new-post.html', title_error = title_error, post_error= post_error, blog_title = blog_title, task_name = task_name)

# App Route for Individual Posts
@app.route('/blog', methods=['POST','GET'])     # Both methods needed, to filter requests
def single():
    blog_id = request.args.get('id')                                            # Collects id tag
    post = Task.query.filter_by(id=blog_id).first()                             # Filters Table by id
    return render_template("blog.html", btitle=post.btitle, entry=post.entry, pub_date = post.pub_date)   # Renders template based on individual id (Use case 1)



# I need to review what this really does....lol
if __name__ == '__main__':
    app.run()