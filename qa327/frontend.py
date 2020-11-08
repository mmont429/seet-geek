from flask import render_template, request, session, redirect, flash
from qa327 import app
import qa327.backend as bn

"""
This file defines the front-end part of the service.
It elaborates how the services should handle different
http requests from the client (browser) through templating.
The html templates are stored in the 'templates' folder. 
"""

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', message='')

@app.route('/register', methods=['GET'])
def register_get():
    # templates are stored in the templates folder
    if 'logged_in' in session:
        return redirect('/')
    return render_template('register.html', message='')

@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    balance = 5000
    error_message = None

    if password != password2:
        error_message = "Passwords must match"

    elif not bn.check_email(email):
        error_message = "Email format is not valid"

    # Username validation
    elif not name:
        error_message = "Username cannot be blank"
    elif set('[~!@#$%^&*()_+{}":;\']+$').intersection(name):
        error_message = "Username must be alphanumeric"
    elif name.startswith(' '):
        error_message = "Username cannot contain leading spaces"
    elif name.endswith(' '):
        error_message = "Username cannot contain trailing spaces"
    elif len(name) < 2:
        error_message = "Username must be longer than 2 characters"
    elif len(name) >= 20:
        error_message = "Username must be less than 20 characters."

    # Password Validation
    elif len(password) < 6:
        error_message = "Password must be 6 or more characters"
    elif not set('[~!@#$%^&*()_+{}":;\']+$').intersection(password):
        error_message = "Password must contain at least one special character"
    elif not any(c.isupper() for c in password):
        error_message = "Password must contain at least one upper case character"
    elif not any(c.islower() for c in password): 
        error_message = "Password must contain at least one lower case character"

    # All checks passed, do final validation and send it
    else:
        user = bn.get_user(email)
        if user:
            error_message = "This email has already been used"
        
        error_message = bn.register_user(email, name, password, password2, balance)

    # if there is any error messages when registering new user
    # at the backend, go back to the register page.
    if error_message:
        return render_template('register.html', message=error_message)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET'])
def login_get():
    if 'logged_in' in session:
        return redirect('/')
    else:
        return render_template('login.html', message='Please login')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    if not bn.check_email(email) or not bn.check_password(password):
        return render_template('login.html', message='email/password format is incorrect.')
    user = bn.login_user(email, password)
    if user:
        session['logged_in'] = user.email
        """
        Session is an object that contains sharing information 
        between browser and the end server. Typically it is encrypted 
        and stored in the browser cookies. They will be past 
        along between every request the browser made to this services.

        Here we store the user object into the session, so we can tell
        if the client has already login in the following sessions.

        """
        # success! go back to the home page
        # code 303 is to force a 'GET' request
        return redirect('/', code=303)
    else:
        return render_template('login.html', message='email/password combination incorrect')


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
    return redirect('/')


def authenticate(inner_function):
    """
    :param inner_function: any python function that accepts a user object

    Wrap any python function and check the current session to see if 
    the user has logged in. If login, it will call the inner_function
    with the logged in user object.

    To wrap a function, we can put a decoration on that function.
    Example:

    @authenticate
    def home_page(user):
        pass
    """

    def wrapped_inner():

        # check did we store the key in the session
        if 'logged_in' in session:
            email = session['logged_in']
            user = bn.get_user(email)
            if user:
                # if the user exists, call the inner_function
                # with user as parameter
                return inner_function(user)
        else:
            # else, redirect to the login page
            return redirect('/login')

    # return the wrapped version of the inner_function:
    return wrapped_inner


@app.route('/')
@authenticate
def profile(user):
    # authentication is done in the wrapper function
    # see above.
    # by using @authenticate, we don't need to re-write
    # the login checking code all the time for other
    # front-end portals
    bn.add_new_ticket(name="test_ticket",quantity=10,price=20,expiration_date=20201231)
    bn.add_new_ticket(name="test_ticket2",quantity=10,price=20,expiration_date=20201231)
    tickets = bn.get_all_tickets()
    return render_template('index.html', user=user, ticket=tickets)

# The sell page reference
@app.route('/sell', methods=['GET', 'POST'])
def sell_post():
    if 'logged_in' in session:
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        expiration_date = request.form.get('expiration_date')
        # templates are stored in the templates folder
        return render_template('sell.html', name=name, quantity=quantity, price=price, expiration_date=expiration_date)
    else:
        flash('You cannot access /sell while being logged out')
        return redirect('/login')


@app.route('/buy', methods=['GET', 'POST'])
def buy_post():
    if 'logged_in' in session:
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        # templates are stored in the templates folder
        return render_template('buy.html', name=name, quantity=quantity)
    else:
        flash('You cannot access /buy while being logged out')
        return redirect('/login')


@app.route('/update', methods=['GET', 'POST'])
def update_post():
    if 'logged_in' in session:
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        expiration_date = request.form.get('expiration_date')
        # templates are stored in the templates folder
        return render_template('update.html', name=name, quantity=quantity, price=price, expiration_date=expiration_date)
    else:
        flash('You cannot access /update while being logged out')
        return redirect('/login')
