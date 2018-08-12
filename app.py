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
import tove2

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
    email = StringField('Email', [validators.Length(min=6, max=80)])
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
        result = cur.execute("SELECT * from users where username = %s", [email])
        if result > 0:
            error = 'Username has be taken'
            cur.close()
            return render_template('register.html', error=error, form=form)

        cur.execute("INSERT INTO users(username, department, password) VALUES(%s, %s, %s)", (email, department, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Check if admin login
        if username == "admin" and password_candidate == "admin":
            session['logged_in'] = True
            session['username'] = username

            flash('Welcome back Admin', 'success')
            return redirect(url_for('dashboard'))

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Close connection
            cur.close()

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
        else:
            # Close connection
            cur.close()

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

    if session['username'] == 'admin':
        # Get Activity
        activity_res = cur.execute("SELECT * FROM activities")
        activities = cur.fetchall()

        # Get Message
        message_res = cur.execute("SELECT * FROM inform_admin")
        messages = cur.fetchall()
    else:
        # Get Activity
        activity_res = cur.execute("SELECT * FROM activities where username = %s", [session['username']])
        activities = cur.fetchall()

        # Get Message
        message_res = cur.execute("SELECT * FROM inform_user where username= %s", [session['username']])
        messages = cur.fetchall()

    # Close connection
    cur.close()
    if activity_res > 0:
        activities_detail = []
        for activity in activities:
            activity_detail = []
            act_detail = web_function.get_activity_detail(activity['activity'   ])
            activity_detail.append(activity['activity'])
            activity_detail.append(act_detail[0] + '/' + act_detail[1] + '/' + act_detail[2])
            activity_detail.append(act_detail[3] + '/' + act_detail[4] + '/' + act_detail[5])
            activity_detail.append(act_detail[6] + '/' + act_detail[7] + '/' + act_detail[8])
            activity_detail.append(act_detail[9] + '/' + act_detail[10] + '/' + act_detail[11])
            activities_detail.append(activity_detail)
        # print('e')
        for detail in activities_detail:
            print(detail)
        return render_template('dashboard.html', activities=activities_detail, messages=messages)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg, messages=messages)


# Activity Form Class
class ActivityForm(Form):
    title = StringField('Name', [validators.Length(min=1, max=200)])
    min_time_start = DateField('Min Start Time', format='%Y-%m-%d') 
    max_time_start = DateField('Max Start Time', format='%Y-%m-%d')
    min_time_end = DateField('Min End Time', format='%Y-%m-%d')
    max_time_end = DateField('Max End Time', format='%Y-%m-%d')
    duration_start = DateField('Duration Min', format='%Y-%m-%d')
    duration_end = DateField('Duration Max', format='%Y-%m-%d')

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
        if session['username'] == "admin":
            department = request.form.getlist('department')
        else:
            cur.execute("SELECT department from users where username = %s", [session['username']])
            result = cur.fetchone()
            department = result['department']
            cur.execute("INSERT INTO inform_admin(operation, activity) VALUES('Add', %s)", [title])
        cur.execute("INSERT INTO activities(username, activity) VALUES(%s, %s)", (session['username'], title))
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
    if session['username'] != "admin":
        cur.execute("INSERT INTO inform_admin(operation, activity) VALUES('Delete', %s)", [title])

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
        username = session['username']
        min_time_start = datetime.strptime(request.form['min_time_start'], '%Y-%m-%d')
        max_time_start = datetime.strptime(request.form['max_time_start'], '%Y-%m-%d')
        min_time_end = datetime.strptime(request.form['min_time_end'], '%Y-%m-%d')
        max_time_end = datetime.strptime(request.form['max_time_end'], '%Y-%m-%d')
        duration_start = datetime.strptime(request.form['duration_start'], '%Y-%m-%d')
        duration_end = datetime.strptime(request.form['duration_end'], '%Y-%m-%d')

        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Execute        
        if session['username'] == "admin":
            cur.execute("SELECT username from activities where activity = %s", [title])
            result = cur.fetchone()
            username = result['username']

            # Get Department
            cur.execute("SELECT department from users where username = %s", [username])
            result = cur.fetchone()
            department = result['department']
        else:
            cur.execute("SELECT department from users where username = %s", [username])
            result = cur.fetchone()
            department = result['department']
            cur.execute("INSERT INTO inform_admin(operation, activity) VALUES('Edit', %s)", [request.form['title']])
        
        cur.execute("DELETE FROM activities where activity = %s", [title])
        cur.execute("INSERT INTO activities(username, activity) VALUES(%s, %s)", (username, request.form['title']))
        
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

# Delete Message
@app.route('/delete_message/<string:message>', methods=['GET', 'POST'])
@is_logged_in
def delete_message(message):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    if session['username'] == 'admin':
        cur.execute("DELETE FROM inform_admin WHERE id = %s", [message])
    else:
        cur.execute("DELETE FROM inform_user WHERE id = %s", [message])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Message Deleted', 'success')

    return redirect(url_for('dashboard'))


# TAC Form Class
class TacForm(Form):
    min_time_start = DateField('Min Start Time', format='%Y-%m-%d') 
    max_time_start = DateField('Max Start Time', format='%Y-%m-%d')
    min_time_end = DateField('Min End Time', format='%Y-%m-%d')
    max_time_end = DateField('Max End Time', format='%Y-%m-%d')


# Check TAC
@app.route('/check_tac', methods=['GET', 'POST'])
@is_logged_in
def check_tac():
    form = TacForm(request.form)
    if request.method == 'POST' and form.validate():
        min_time_start = datetime.strptime(request.form['min_time_start'], '%Y-%m-%d')
        max_time_start = datetime.strptime(request.form['max_time_start'], '%Y-%m-%d')
        min_time_end = datetime.strptime(request.form['min_time_end'], '%Y-%m-%d')
        max_time_end = datetime.strptime(request.form['max_time_end'], '%Y-%m-%d')

        result = tove2.TAC(min_time_start.year, min_time_start.month, min_time_start.day, 
            max_time_start.year, max_time_start.month, max_time_start.day,
            min_time_end.year, min_time_end.month, min_time_end.day,
            max_time_end.year, max_time_end.month, max_time_end.day)


        if result[0] == None:
            if len(result) == 4:
                flash(result[1], 'danger')
                # Create cursor
                cur = mysql.connection.cursor()

                # Execute
                cur.execute("SELECT * FROM activities where activity = %s", [result[2]])
                sql_result = cur.fetchone()
                if sql_result != None:
                    user1 = sql_result['username']
                    cur.execute("INSERT INTO inform_user(username, activity) VALUES(%s, %s)", [user1, result[1]])
                    flash("Informed {}".format(user1), 'success')
                else:
                    flash("Cannot find the user of {}".format(result[2]), 'danger')
                cur.execute("SELECT * FROM activities where activity = %s", [result[3]])
                sql_result = cur.fetchone()
                if sql_result != None:
                    user2 = sql_result['username']
                    cur.execute("INSERT INTO activities(username, activity) VALUES(%s, %s)", [user2, result[1]])
                    flash("Informed {}".format(user2), 'success')
                else:
                    flash("Cannot find the user of {}".format(result[3]), 'danger')
                
                # Commit to DB
                mysql.connection.commit()
                cur.close()     
            else:
                # Show Message
                flash(result[1], 'danger')
            # return redirect(url_for('check_tac'))
        else:
            flash("Start time: {}; End time: {}".format(result[0][0], result[0][1]), 'success')

    return render_template('check_tac.html', form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
