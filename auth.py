from flask import request, session, abort
from functools import wraps
from flask_login import current_user
from models import LoginAttempt, ActiveSession, db
from datetime import datetime, timedelta
import sqllite3

def log_login_attempt(username, method, status, user_id=None):
    # create a tuple in database for login attempts
    con = sqllite3.connect("instance/campuskey.db")
    cur = con.cursor()

    # TODO create table (if not exist) using schema

    # inserts into table values depending on if userID is provided
    if user_id is None:
        data = {username, method, status, user_id}
        cur.execute("INSERT INTO table VALUES(?, ?, ?, ?)", data)
    else:
        data = {username, method, status}
        cur.execute("INSERT INTO table VALUES(?, ?, ?, NULL)", data)

    # commits the insert into the database
    con.commit()
    return



def track_session_activity(user_id, session_id):

    con = sqllite3.connect("instance/campuskey.db")
    cur = con.cursor()

    # check if session exists
    cur = cur.execute("SELECT user FROM table WHERE session = ?", session_id)
    result = cur.fetchone()

    if result is None: # Session does not exist
        data = {user_id, session_id}
        cur.execute("INSERT INTO table VALUES(?, ?)", data)
    else: # Session Exists
        cur.execute("UPDATE table SET time=? WHERE session=?", datetime.now().time(), session_id)

    con.commit()
    return

def get_active_session():
    con = sqllite3.connect("instance/campuskey.db")
    cur = con.cursor()

    # get all sessions and current time
    cur.execute("SELECT * FROM table")
    results = cur.fetchall()
    time = datetime.now().time()

    # check for expired sessions, and remove them
    for result in results:
        if (time - result[2]).total_seconds() > 7200: # expire time = 2 hours
            cur.execute("DELETE FROM table WHERE session=?", result[1])
            con.commit()
            results.remove(result)
    return results

# decorator functions to ensure proper role authentication
def role_required(func):
    def wrapper(*args):
        if current_user.is_authenticated:
            if current_user.role in args:
                func()
                return wrapper
    print("Error 403")
    return wrapper


def admin_required(func):
    def wrapper(*args):
        if "admin" in args:
            func()
            return wrapper
    print("Error 403")
    return wrapper

# checks that user exists and has the expected role
def verify_user_role(username, expected_role):
    con = sqllite3.connect("instance/campuskey.db")
    cur = con.cursor()

    # get role for provided user
    cur.execute("SELECT role FROM table WHERE user=?", username)
    result = cur.fetchone()
    
    if result is None or result != expected_role:
        return False
    else:
        return True

def get_user_role(username):
    con = sqllite3.connect("instance/campuskey.db")
    cur = con.cursor()

    # get role for provided user
    cur.execute("SELECT role FROM table WHERE user=?", username)
    result = cur.fetchone()
    
    # Checks if user exists, if they do prints their role
    if result is None:
        print("User does not exist")
    else:
        print(f"The role of {username} is: {result}")
    return
