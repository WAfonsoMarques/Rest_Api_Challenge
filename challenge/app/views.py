from os import extsep
from typing import Text
from flask import Flask
from flask import render_template, request, session, redirect, url_for, flash, make_response, escape, abort
from flask_mysqldb import MySQL
import hashlib
from datetime import datetime

from __init__ import app, mysql, current_user, limiter, ip_ban
import model


import logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def filter_scanner_boys():
    user_agent = request.headers.get('User-Agent')
    if "sqlmap" in user_agent:
        return abort(404)


def encrypt_string(hash_string):
    string_data = str(hash_string)
    sha_signature = hashlib.sha256(string_data.encode()).hexdigest()
    return sha_signature

##### auxiliar to render errors
def error(msg):
   return render_template('error_response.html', msg = msg)


##### initializes db
@app.route('/init', methods=['GET', 'POST'])
def init():
   model.init_db()
   flash("Initialisation DONE!", 'error')
   return redirect(url_for('login'))


##### home
### redirects to login
@app.route('/', methods=["GET", "POST"])
def home():
   if 'username' in session:
      username = session['username']
      current_user = model.get_user(username)
      logging.debug("user in homepage: (%s)" % current_user)
         
      if current_user:
         return render_template('home.html', current_user=current_user)
   return redirect(url_for('login'))


##### login user
### in[POST]: username, password
### redirects to home if login is succesful
### redirects to login otherwise
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("1/2second", override_defaults=False)
def login():
   global current_user

   if request.method == 'GET':
      return render_template('login.html')

   username = request.form['username']
   password = request.form['password']

   
   logging.debug("login: Trying (%s, %s)" % (username, password))

   if username == "" or password == "":
      flash("You need to provide a 'username' and a 'password' to login.", 'error')
      return redirect(url_for('login'))

   try:
      user = model.login_user(username, password, request.remote_addr)
   except Exception as e:
      logging.debug("login: Found exception(%s)" % e)
      return error(e)

   if not user:
      count_faults = ip_ban.get_block_list()[request.remote_addr]['count']
      if(count_faults == 2):
         flash('You have 1 more try')
         
      flash('Username or Password are invalid', 'error')
      return redirect(url_for('login'))
   
   
   logging.debug("login: Succesfull (%s, %s)" % (username, password))
   session['username'] = username
   current_user = user
   return redirect(url_for('home'))


##### register a new user
### in[POST]: username, password
### redirects to home if registration is succesful
### redirects to register otherwise
@app.route('/register', methods=['GET', 'POST'])
def register():
   global current_user

   if request.method == 'GET':
      return render_template('register.html')

   username = request.form['username']
   password = request.form['password']
   logging.debug("register: Trying (%s, %s)" % (username, password))

   if username == "" or password == "":
      flash("You need to provide a 'username' and a 'password' to register.", 'error')
      return redirect(url_for('register'))

   try:
      user = model.get_user(username)
   except Exception as e:
      logging.debug("register1: Found exception(%s)" % e)
      return error(e)

   if user:
      flash("User '%s' already exists." % user.username, 'error')
      return redirect(url_for('register'))

   try:
      user = model.register_user(username, password)
   except Exception as e:
      logging.debug("register2 Found exception(%s)" % e)
      return error(e)

   logging.debug("register: Succesfull (%s, %s)" % (username, password))
   session['username'] = username
   current_user = user
   return redirect(url_for('home'))


##### logout
### removes the username from the session if it is there
@app.route('/logout')
def logout():
   global current_user

   session.pop('username', None)
   current_user = None
   return redirect(url_for('login'))