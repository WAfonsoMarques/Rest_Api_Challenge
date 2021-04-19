from flask_mysqldb import MySQL

from jinja2 import utils

from __init__ import app, mysql, ip_ban
from views import error
import hashlib
from datetime import datetime
import itertools 

import logging
logging.basicConfig(level=logging.DEBUG)

user_bad_access = {}
# fetchall, fetchmany(), fetchone()

# INIT DB
def init_db():
    hash_pass_afonso = encrypt_string("AVeryL33tPasswd")
    hash_pass_admin = encrypt_string("sporting123")
    hash_pass_fast = encrypt_string("1")
    cur = mysql.connection.cursor()
    cur.execute("DROP DATABASE IF EXISTS %s;" % app.config['MYSQL_DB'])
    cur.execute("CREATE DATABASE %s;" % app.config['MYSQL_DB'])
    cur.execute("USE %s;" % app.config['MYSQL_DB'])
    cur.execute("DROP TABLE IF EXISTS Users;")
    cur.execute('''CREATE TABLE Users (
                    username VARCHAR(20) NOT NULL,
                    password VARCHAR(256) NOT NULL,
                    name TEXT, 
                    is_blocked VARCHAR(1),
                    PRIMARY KEY (username)
                    );''')
    cur.execute("INSERT INTO Users(username, password, name, is_blocked) VALUES (%s, %s, %s, %s)", ('administrator', hash_pass_admin, "Admin", '0'))
    cur.execute("INSERT INTO Users(username, password, name, is_blocked) VALUES (%s, %s, %s, %s)", ('afonso', hash_pass_afonso, "Mr. Afonso", '0'))
    cur.execute("INSERT INTO Users(username, password, name, is_blocked) VALUES (%s, %s, %s, %s)", ('1', hash_pass_fast, "Mr. Afonso", '0'))
    
    mysql.connection.commit()
    cur.close()


# Function to encript password
def encrypt_string(hash_string):
    string_data = str(hash_string)
    sha_signature = hashlib.sha256(string_data.encode()).hexdigest()
    return sha_signature


# SELECT QUERIES
def get_all_results(q):
    cur = mysql.connection.cursor()
    cur.execute(q)
    mysql.connection.commit()
    data = cur.fetchall()
    cur.close()
    return data


# UPDATE and INSERT QUERIES
def commit_results(q):
    cur = mysql.connection.cursor()
    cur.execute(q)
    mysql.connection.commit()
    cur.close()


##### Returns a user for a given username
### in: username
### out: User
def get_user(username):
    username=str(utils.escape(username))
    q = "SELECT * FROM Users"
    q+= " WHERE username = '%s'" % (username)

    logging.debug("get_user query: %s" % q)
    data = get_all_results(q)

    if len(data) == 1:
        user = User(*(data[0]))
        return user
    else:
        logging.debug("get_user: Something wrong happened with (username):(%s)" % (username))
        return None

##### Block a user
### in: username
### out: Void
def block_user(username):

    username=str(utils.escape(username))
    q = "UPDATE Users"
    q+= " SET is_blocked = '1'"
    q+= " WHERE username = '%s'" % (username)
    

    logging.debug("get_user query: %s" % q)
    data = get_all_results(q)

    if len(data) == 1:
        user = User(*(data[0]))
        return user
    else:
        logging.debug("get_user: Something wrong happened with (username):(%s)" % (username))
        return None




##### Returns a user for a given pair username:password
### in: username, password
### out: User
def login_user(username, password, ip):
    atual_time = datetime.now()

    username=str(utils.escape(username))
    hash_password = encrypt_string(password)
    q = "SELECT * FROM Users"
    q+= " WHERE username = '%s'" % (username)
    q+= " AND password = '%s'" % (hash_password)
    q+= " AND is_blocked <> '1'"
    
    logging.debug("login_user query: %s" % q)
    data = get_all_results(q)

    #Reset the fault counter
    if ip_ban.get_block_list():
      if(ip in ip_ban.get_block_list()):
         elapsed_time = atual_time - ip_ban.get_block_list()[ip]['timestamp']
         elapsed_min = elapsed_time.seconds / 60
         if(elapsed_min > 30):
            ip_ban.remove(ip)

    if len(data) == 1:
        ip_ban.remove(ip)

        user = User(*(data[0]))
        return user
    else:
        ip_ban.add(ip)
        update_user_bad_access(username)

        logging.debug("login_user: Something wrong happened with (username, password):(%s %s)" % (username, hash_password))
        return None

#Update user timestamps
def update_user_bad_access(username):
    # If user exist
    if(get_user(username) != None):
        timestamps = user_bad_access.get(username) 

        if(timestamps == None):
            timestamps = [datetime.now()]
        else:
            # Remove timestamps older than 1h
            timestamps = clean_timestamps(timestamps, 30)

            timestamps.append(datetime.now())
        
        user_bad_access[username] = timestamps

        # That means at least 2 ip's
        if(len(timestamps) > 20 or check_multiple_ips(timestamps)):
            block_user(username)

# Check timestamps in order to find multiple ips
def check_multiple_ips(timestamps):
    for x,y in itertools.combinations(timestamps, 2):
        result = abs(x - y)
        if(result.seconds < 2):
            return True
    
    return False


def clean_timestamps(timestamps, time_min):
    atual_time = datetime.now()
    updated_timestamps = []

    for timestamp in timestamps:
        elapsed_time = atual_time - timestamp
        elapsed_in_min = elapsed_time.seconds / 60
        
        # Discard the old timestamps  
        if elapsed_in_min < time_min:
            updated_timestamps.append(timestamp)
    
    return updated_timestamps




##### Registers a new user with a given pair username:password
### in: username, password
### out: User
def register_user(username, password):
    username=str(utils.escape(username))
    hash_password = encrypt_string(password)
    q = "INSERT INTO Users (username, password)"
    q+= " VALUES ('%s', '%s')" % (username, hash_password)

    logging.debug("register_user query: %s" % q)
    commit_results(q)
    return User(username, password)


##### class User
class User():
    def __init__(self, username, password, name='', is_blocked='0'):
        self.username = username
        self.password = password
        self.name = name
        self.is_blocked = is_blocked

    def __repr__(self):
        return '<User: username=%s, password=%s, name=%s>' % (self.username, self.password, self.name)
