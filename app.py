# Import required libraries
import os
import random
import string
import smtplib

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from email.message import EmailMessage


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///plannera.db")

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


# Register New Users
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if (request.method == "POST"):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Confirming that the user provides all fields
        if not username:
            flash('Enter a username please!', category='error')
            return render_template("signup.html")
        elif not email:
            flash('Email is required!', category='error')
            return render_template("signup.html")
        elif not password:
            flash('Password is required!', category='error')
            return render_template("signup.html")
        elif not confirmation:
            flash('Please confirm your password!', category='error')
            return render_template("signup.html")

        # Making sure that the confirmation and password match
        if password != confirmation:
            flash('Passwords do not match!', category='error')
            return render_template("signup.html")

        # Ensure that password is Eight characters
        if len(password) != 8:
            flash('Password must be eight chracters long', category='error')
            return render_template("signup.html")


        # Checking if the user already exists
        user_name = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if user_name:
            flash('Username has already been taken!', category='error')
            return render_template("signup.html")

        user_mail = db.execute("SELECT * FROM users WHERE email = :email", email=email)
        if user_mail:
            flash('This email is associated with an existing account!', category='error')
            return render_template("signup.html")

        # Hashing the password
        hash = generate_password_hash(password)

        # Generate a random confirmation token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Inserting the data into the database
        db.execute("INSERT INTO users (username, email, hash, confirmation_token) VALUES(?, ?, ?, ?)", username, email, hash, token)


        # Create a new email message
        msg = EmailMessage()

        # Set the subject and recipient of the message
        msg['Subject'] = 'Confirm your email address'
        msg['To'] = email

        # Set the message body
        msg.set_content("Click the link to confirm your email address:\n\nhttp://localhost:5000/confirm_email?token=" + token)

        # Send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("plannerateams@gmail.com", "tnzubrhcuxvlwstz")
        server.send_message(msg)
        server.quit()

        flash('A confirmation link has been sent to your email address at. Click the link to confirm your email address and complete your sign up.')
        return redirect("/login")

    else:
        return render_template("signup.html")


# Confirm user email
@app.route("/confirm_email", methods=["GET"])
def confirm_email():
    # Retrieve the confirmation token from the query string
    token = request.args.get("token")

    # Query the database for the user's account, using the confirmation token as a search parameter
    user = db.execute("SELECT * FROM users WHERE confirmation_token = :confirmation_token", confirmation_token=token)

    if len(user) == 1:
        # If the user's account is found and the confirmation token is still valid, update the user's account in the database to indicate that they have confirmed their email address
        db.execute("UPDATE users SET confirmed = 1 WHERE confirmation_token = :confirmation_token", confirmation_token=token)
        flash('Email confirmed successfully', category='success')

        # Redirect the user to a page that indicates that their email address has been confirmed
        return redirect("/login")
    else:
        # If the user's account is not found or the confirmation token is invalid, display an error message
        flash('Inavlid token', category='error')
        return redirect("/login")

# Route for password reset form
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        # Get email from form
        email = request.form.get('email')

        # Check if email exists in the database
        user = db.execute("SELECT * FROM users WHERE email = :email", email=email)
        if user:
            # Generate a random token
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

            # Update the token in the database
            db.execute("UPDATE users SET reset_token = :token WHERE email = :email", token=token, email=email)

            # Create a new email message
            msg = EmailMessage()

            # Set the subject and recipient of the message
            msg['Subject'] = 'Reset your password'
            msg['To'] = email

            # Set the message body
            msg.set_content("Click the link to reset your password:\n\nhttp://localhost:5000/reset_password?token=" + token)

            # Send the message
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("plannerateams@gmail.com", "tnzubrhcuxvlwstz")
            server.send_message(msg)
            server.quit()

            # return a message to the user
            flash('An email has been sent to your address with instructions to reset your password', category='success')
            return render_template("reset.html")
        else:
            flash('No account with the provided email address exists', category='error')
            return render_template('reset.html')
    else:
        return render_template('reset.html')


# Route for reset password form
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')  # Default value for token when request method is GET
    if request.method == 'POST':
        # Get token and new password from form
        token = request.form.get('token')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Check if the password and the confirmation are matching
        if password != confirmation:
            flash('Passwords do not match!', category='error')

        # Check if token is valid
        user = db.execute("SELECT * FROM users WHERE reset_token = :token", token=token)
        if user:
            # Hash the new password
            hash = generate_password_hash(password)

            # Update the password and clear the reset token in the database
            db.execute("UPDATE users SET hash = :hash, reset_token = NULL WHERE reset_token = :token", hash=hash, token=token)

            # Return a message to the user
            flash('Your password has been reset successfully', category='success')
            return render_template('reset_password.html')
        else:
            # Token is invalid, display error message
            flash('Invalid or expired reset token', category='error')
            return render_template('reset_password.html')
    else:
        # Display the reset password form
        return render_template('reset_password.html', token=token)




@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")

# Log the user out
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash('User Logged out successfully!', category='success')
    return redirect("/login")

# Add new tasks
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "POST":
        user_id = session["user_id"]
        title = request.form.get('title')
        description = request.form.get('description')
        due = request.form.get('due')
        category = request.form.get('category')

        # Ensure all fields are provided
        if not title:
            flash('Please input task tile', category='error')
            return redirect('/tasks')
        elif not description:
            flash('Please input a description for your task', category='error')
            return redirect('/tasks')
        elif not due:
            flash('Please select a date', category='error')
            return redirect('/tasks')
        elif not category:
            flash('Please choose a category for your task', category='error')

        # Adding task to the database
        db.execute("INSERT INTO tasks (user_id, title, description, due_date, category) VALUES (?, ?, ?, ?, ?)", user_id, title, description, due, category)
        flash('Task added successfully!', category='success')
        return redirect('/tasks')
    else:
        return render_template('new_task.html')


# Delete tasks
@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete(id):
    # delete the task here
    user_id = session['user_id']
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", id, user_id)
    flash('Task deleted permanently', category='error')
    return redirect(request.referrer)


# Mark tasks as completed
@app.route("/completed/<int:id>", methods=["POST", "GET"])
def completed(id):
    # delete the task here
    user_id = session['user_id']
    db.execute("UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?", id, user_id)
    flash('Task completed successfully', category='success')
    return redirect(request.referrer)

@app.route("/todo", methods=["GET", "POST"])
def todo():
    # Display the buser task
    user_id = session['user_id']
    todos = db.execute ("SELECT id, date_added, title, description, due_date FROM tasks WHERE user_id = ? AND category = 'To Do' AND status IS NULL", user_id)
    return render_template('todo.html', todos=todos)

@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    user_id = session['user_id']
    schedules = db.execute ("SELECT id, date_added, title, description, due_date FROM tasks WHERE user_id = ? AND category = 'Schedule' AND status IS NULL", user_id)
    return render_template('schedule.html', schedules=schedules)

@app.route("/deligate", methods=["GET", "POST"])
def deligate():
    user_id = session['user_id']
    deligates = db.execute ("SELECT id, date_added, title, description, due_date FROM tasks WHERE user_id = ? AND category = 'Deligate' AND status IS NULL", user_id)
    return render_template('deligate.html', deligates=deligates)

@app.route("/eliminate", methods=["GET", "POST"])
def eliminate():
    user_id = session['user_id']
    eliminates = db.execute ("SELECT id, date_added, title, description, due_date FROM tasks WHERE user_id = ? AND category = 'Eliminate' AND status IS NULL ", user_id)
    return render_template('eliminate.html', eliminates=eliminates)

@app.route("/history", methods=["GET", "POST"])
def history():
    user_id = session['user_id']
    records = db.execute ("SELECT id, date_added, title, description, category, status FROM tasks WHERE user_id = ? AND status = 'Completed' ", user_id)
    return render_template('history.html', records=records)


# Log in the user
@app.route("/login", methods=["GET", "POST"])
def login():
     # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("Please input your email", category='error')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please input your password", category='error')
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password", category='error')
            return render_template("login.html")

        # Ensure that the email is verified
        if rows[0]['confirmed']:
            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to the dashboard
            flash("Logged in successfully!", category='success')
            return redirect("/tasks")
        else:
            flash('Please verify your email', category='error')
            return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
