# PLANNERA
#### Video Demo:  <https://youtu.be/LrhIjM2P_a0>
#### Description:
Plannera is a simple plannner that is meant to make palnning easy. The app helps users categorise tasks into four groups.
1. To Do
These are very important and urgent tasks which need to be done immediately.
2. Schedule
These are important tasks that are not urgent. They can be scheduled to another time
3. Deligate
These are non imortant task that are urgent. These tasks may be deligated to someone else of even at a time when the important tasks have been finished.
4. Eliminate
Finally this are tasks that are neither important nor urgent. They are mostly time wasters, you should eliminate this things/habits.

# Features of the project
# User authentication
This includes:
    - Signing up new users and Sending confirmation email to the users
    - Logging in the user
    - Forget password
    - Logging the user out
#### 1. Signing up new user and sending confirmation email to the users
For this project I craedted a database that has two tables in it: users and tasks. The users tables has id, username, email, hash, confirmation_token, confirmed and reset_token. I created a sign up page in 'signup.html' with a form with 'post' method I have also made a route for '/signup' in my 'app.py'.
Once a user fill in the form correctly the field information are extracted and a series of confirmation proccess are done amking sure taht all the fields are provided, the user is then inserted in the database and assign a confirmation token that is generated and using the stmplib module an email with the token is sent to the user once the link is clicked the database is updated and the confirmed column is assigned a value of 1 instead of the default 0. Here is the code:

#### 2. Logging in the user
Once a user inputs their credentials in the log in page, the credentials are searched for in the database using a select statement. If the password does not match the hash or the email does not associate with the provided email or the email is not found in the database a message is passed to the message. This can be done in many ways however I chose flash module in flask since that is more user friendly than lets say having to load another page thus making the user to reload to the previous page each time. By flashing messages the user can just dismiss them and try again since they are not redirected to a new page. If the user is in the database and email is confirmed the session id is set to be the same as the user id to know which user is signed and a success message is flashed else a message is flashed that asks the user to verify their email.

#### 3. Forget password
If a user forgets password they can click on the forget link in the log in page and they are redirected to a page where they can provide and email so that a reset link can be sent. The reset function takes the email provided by the user and quesries the database once the email is there a reset_token is assigned to the user and the reset_token column updated to store the token. An email containing the token in a link is sent to the user. Once the link is clicked a new page is relaoded where the user can put in their new password. The token in the link is passed as a hidden input and once the password is submited the database is queried by the reset_password function and the email is hashed and the hash put into the table. The rest_token column is cleared.

#### 4. Logging the user out
The logout fucntion clears the session once the user clicks on a button. A success message is flashed to the user indicating that they have been logged out successfully.

# Tasks
The database has a tasks table which has the following columns; id, user_id, date_added, title, description, date_due, category and status. The id is the primary key that is used to identify each task, user_id is a foreign key that refers to the user (id) who created the task, date due is timestamp that automatically record the date and time in which the task is added, date_due is the deadline by which the task must be finished, category is the group to which the task belongs and finally status is the status of the task whether it is completed or not it is automatically assigned NULL.
#### 1. New Task
Once the user is signed up or logged in they are redirected to a dashboard for the tasks. They can create a new task, once teh user provides all the fields required teh tasks function extracts the data from the request, after performing a series of checks to ensure all fields are provided it queries the databases and puts the task into the tasks table. A success message is displayed to the user.

#### 2. Task categories filter
After the tasks have been put into the database, four functions are used to filter the categories of the tasks. The todo function selects all the tasks the table with a category of todo and displays it in simple table with two buttons for deleting or completing the tasks. The other three fucntions work similarly each displaying respective category.

#### 2. Updating the task status
The delete and completed fucntions are implemented such that they take and integer after the path, once the user clicks on the respective icon the task id is passed with the request. The database if then queried for that task id, if it is delete the task is deleted from the database else the status is updated to 'Completed'

#### 3. History
This page dispalys all the task whose status is set to 'Completed'. It helps the user refer abck to it.
