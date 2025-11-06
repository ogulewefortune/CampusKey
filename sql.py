import sqlite3

# create database if not made (connect otherwise): create cursor to work with
con = sqlite3.connect("database.db")
cur = con.cursor()

# create databse table if it does not exist
# need to confirm attributes later
cur.execute("CREATE TABLE IF NOT EXISTS info(studentID INTEGER PRIMARY KEY, code INTEGER, role TEXT)")

# simple login function
# TODO needs to be refined later
def login(ID, code):
    # connects to database: create cursor to work with
    con_login = sqlite3.connect("database.db")
    cur_login = con.cursor()

    # uses "?" to avoid sql injection attacks (is the case in all executes)
    actual_code = cur_login.execute("SELECT code FROM info WHERE studentID = ?", ID)

    # checks if student exists and is logging into their own account
    if not actual_code:
        print("Error: student does not exist")
    else:
        if code == actual_code:
            print("Success!")
        else:
            print("Error: Wrong student")
    return

# basic add person function
def add_person(ID, code, role):

    data = {ID: code: role}

     # connects to database: create cursor to work with
    con_add = sqlite3.connect("database.db")
    cur_add = con.cursor()
    
    # using things like ":id" is equivalent to "?" just more clear in this case
    cur_add.execute("INSERT INTO info VALUES(:id, :code, :role)", data)
    return

# function outline to remove a student
def remove_person(ID):

     # connects to database: create cursor to work with
    con_rem = sqlite3.connect("database.db")
    cur_rem = con.cursor()
    
    cur_rem.execute("DELETE FROM info WHERE studentID = ?", ID)
    return
