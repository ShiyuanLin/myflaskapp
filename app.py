from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import DateField
from datetime import date, datetime
from passlib.hash import sha256_crypt
from functools import wraps
# from web_function import get_activity_dic
import web_function

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1122'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

#Articles = Articles()

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close connection
    cur.close()


#Single Article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    return render_template('article.html', article=article)


# Register Form Class
class RegisterForm(Form):
    # name = StringField('Name', [validators.Length(min=1, max=50)])
    # username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=80)])
    # department = StringField('department', [validators.Length(min=6, max=80)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # name = form.name.data
        email = form.email.data
        # username = form.username.data
        department = request.form.getlist('department')
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(username, department, password) VALUES(%s, %s, %s)", (email, department, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM activities")

    activities = cur.fetchall()

    if result > 0:
        # return render_template('dashboard.html', articles=articles)
        return render_template('dashboard.html', activities=activities)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()


# Activity Form Class
class ActivityForm(Form):
    title = StringField('Name', [validators.Length(min=1, max=200)])
    min_time_start = DateField('Min Start Time', format='%Y-%m-%d') 
    max_time_start = DateField('Max Start Time', format='%Y-%m-%d')
    min_time_end = DateField('Min End Time', format='%Y-%m-%d')
    max_time_end = DateField('Max End Time', format='%Y-%m-%d')
    duration_start = DateField('Duration Start Time', format='%Y-%m-%d')
    duration_end = DateField('Duration End Time', format='%Y-%m-%d')

# Add Activity
@app.route('/add_activity', methods=['GET', 'POST'])
@is_logged_in
def add_activity():
    form = ActivityForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data

        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Execute
        cur.execute("SELECT id, department from users where username = %s", [session['username']])
        result = cur.fetchone()
        userid = result['id']
        department = result['department']
        cur.execute("INSERT INTO activities(user_id, activity) VALUES(%s, %s)", (userid, title))
        # Add to RDF
        web_function.add_activity(title, department, 
            form.min_time_start.data.year, form.min_time_start.data.month, form.min_time_start.data.day, 
            form.max_time_start.data.year, form.max_time_start.data.month, form.max_time_start.data.day,
            form.min_time_end.data.year, form.min_time_end.data.month, form.min_time_end.data.day,
            form.max_time_end.data.year, form.max_time_end.data.month, form.max_time_end.data.day,
            form.duration_start.data.year, form.duration_start.data.month, form.duration_start.data.day,
            form.duration_end.data.year, form.duration_end.data.month, form.duration_end.data.day,)

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()


        flash('Activity Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_activity.html', form=form)


# Show All Activities
@app.route('/show_activity')
@is_logged_in
def show_activity():
    # test_content = {'department1': 'title1', 'department2': 'title2'}
    test_content = web_function.get_activity_dic()
    return render_template('show_activity.html', content=test_content)


# Delete Activity
@app.route('/delete_activity/<string:title>', methods=['GET', 'POST'])
@is_logged_in
def delete_activity(title):
    name=title
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM activities WHERE activity = %s", [title])

    # Delete from RDF
    web_function.delete_activity(name)

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Activity Deleted', 'success')

    return redirect(url_for('dashboard'))


# Edit Article
@app.route('/edit_activity/<string:title>', methods=['GET', 'POST'])
@is_logged_in
def edit_activity(title):
    # print(web_function.get_activity_detail('Sewage_Apr_Activity'))
    [start_min_year, start_min_month, start_min_day, 
     start_max_year, start_max_month, start_max_day,
     end_min_year, end_min_month, end_min_day,
     end_max_year, end_max_month, end_max_day,
     dur_min_year, dur_min_month, dur_min_day,
     dur_max_year, dur_max_month, dur_max_day] = web_function.get_activity_detail(title)
    # Get form
    form = ActivityForm(request.form)
    form.title.data = title
    form.min_time_start.data = date(int(start_min_year), int(start_min_month), int(start_min_day))
    form.max_time_start.data = date(int(start_max_year), int(start_max_month), int(start_max_day))
    form.min_time_end.data = date(int(end_min_year), int(end_min_month), int(end_min_day))
    form.max_time_end.data = date(int(end_max_year), int(end_max_month), int(end_max_day))
    form.duration_start.data = date(int(dur_min_year), int(dur_min_month), int(dur_min_day))
    form.duration_end.data = date(int(dur_max_year), int(dur_max_month), int(dur_max_day))



    if request.method == 'POST' and form.validate():
        # title = form.title.data
        min_time_start = datetime.strptime(request.form['min_time_start'], '%Y-%m-%d')
        max_time_start = datetime.strptime(request.form['max_time_start'], '%Y-%m-%d')
        min_time_end = datetime.strptime(request.form['min_time_end'], '%Y-%m-%d')
        max_time_end = datetime.strptime(request.form['max_time_end'], '%Y-%m-%d')
        duration_start = datetime.strptime(request.form['duration_start'], '%Y-%m-%d')
        duration_end = datetime.strptime(request.form['duration_end'], '%Y-%m-%d')

        # print type(datetime.strptime(min_time_end, '%Y-%m-%d'))
        # print(date(min_time_end))


        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Execute
        cur.execute("DELETE FROM activities where activity = %s", [title])
        cur.execute("SELECT id, department from users where username = %s", [session['username']])
        result = cur.fetchone()
        userid = result['id']
        department = result['department']
        cur.execute("INSERT INTO activities(user_id, activity) VALUES(%s, %s)", (userid, request.form['title']))
        # Add to RDF
        web_function.edit_activity(title, request.form['title'], department, 
            min_time_start.year, min_time_start.month, min_time_start.day, 
            max_time_start.year, max_time_start.month, max_time_start.day,
            min_time_end.year, min_time_end.month, min_time_end.day,
            max_time_end.year, max_time_end.month, max_time_end.day,
            duration_start.year, duration_start.month, duration_start.day,
            duration_end.year, duration_end.month, duration_end.day)

        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()


        flash('Activity Modified', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_activity.html', form=form)



# Article Form Class
# class ArticleForm(Form):
#     title = StringField('Title', [validators.Length(min=1, max=200)])
#     body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
# @app.route('/add_article', methods=['GET', 'POST'])
# @is_logged_in
# def add_article():
#     form = ArticleForm(request.form)
#     if request.method == 'POST' and form.validate():
#         title = form.title.data
#         body = form.body.data

#         # Create Cursor
#         cur = mysql.connection.cursor()

#         # Execute
#         cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

#         # Commit to DB
#         mysql.connection.commit()

#         #Close connection
#         cur.close()

#         flash('Article Created', 'success')

#         return redirect(url_for('dashboard'))

#     return render_template('add_article.html', form=form)


# Edit Article
# @app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
# @is_logged_in
# def edit_article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Get article by id
#     result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

#     article = cur.fetchone()
#     cur.close()
#     # Get form
#     form = ArticleForm(request.form)

#     # Populate article form fields
#     form.title.data = article['title']
#     form.body.data = article['body']

#     if request.method == 'POST' and form.validate():
#         title = request.form['title']
#         body = request.form['body']

#         # Create Cursor
#         cur = mysql.connection.cursor()
#         app.logger.info(title)
#         # Execute
#         cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
#         # Commit to DB
#         mysql.connection.commit()

#         #Close connection
#         cur.close()

#         flash('Article Updated', 'success')

#         return redirect(url_for('dashboard'))

#     return render_template('edit_article.html', form=form)

# Delete Article
# @app.route('/delete_article/<string:id>', methods=['POST'])
# @is_logged_in
# def delete_article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Execute
#     cur.execute("DELETE FROM articles WHERE id = %s", [id])

#     # Commit to DB
#     mysql.connection.commit()

#     #Close connection
#     cur.close()

#     flash('Article Deleted', 'success')

    # return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
