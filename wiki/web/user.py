"""
    User classes & helpers
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import os
import json
import binascii
import hashlib
import sqlite3

from functools import wraps

from flask import current_app
from flask_login import current_user

from config import USER_DIR


class UserManager(object):
    """A very simple user Manager, that saves it's data as json."""

    def __init__(self, path):
        self.file = os.path.join(USER_DIR, 'users.json')
        self.dbConnection = sqlite3.connect(USER_DIR + '/Users.sqlite')

    def read(self):
        if not os.path.exists(self.file):
            return {}
        with open(self.file) as f:
            data = json.loads(f.read())
        return data

    def write(self, data):
        with open(self.file, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def add_user(self, name, password,
                 active=True, roles=[], authentication_method=None):
        users = self.read()
        if authentication_method is None:
            authentication_method = get_default_authentication_method()

        """
        This is the Only information that is stored in users.json now. The passwords are only in the database now. 
        Removing this information from the JSON and putting it in the database was causing a lot of errors with Jinja, so I kept
        this Json here to keep the login functionality working. Ideally everything would just be in the database, but then the
        entire login system would have to be completely overhauled, so I left it as is for simplicity. 
        """
        new_user = {
            'active': active,
            'roles': roles,
            'authenticated': False
        }

        users[name] = new_user
        self.write(users)
        userdata = users.get(name)

        """
        This opens a connection to the database, and inserts the new user.
        The new user is not inserted into the database if someone has the same
        username.
        """
        try:
            dbCur = self.dbConnection.cursor()
            dbCur.execute("""
            INSERT INTO users (username,password)
            VALUES( (?) , (?));
            """, (name, password))
            self.dbConnection.commit()
            dbCur.close()

            dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
            dbCur = dbCon.cursor()
            dbCur.execute("SELECT username FROM users WHERE username = ?", name)
            userdata = dbCur.fetchone()

            return User(self, name, userdata)
        except:
            return

    def get_user(self, name):
        users = self.read()
        userdata = users.get(name)
        if not userdata:
            return None
        return User(self, name, userdata)

    def delete_user(self, name):

        dbCur = self.dbConnection.cursor()
        dbCur.execute("""
               DELETE FROM users
               WHERE username = ?
               """, (name,))
        self.dbConnection.commit()
        dbCur.close()

    def update(self, name, userdata):
        data = self.read()
        data[name] = userdata
        self.write(data)


class User(object):
    def __init__(self, manager, name, data):
        self.manager = manager
        self.name = name
        self.data = data

    def get(self, option):
        return self.data.get(option)

    def set(self, option, value):
        self.data[option] = value
        self.save()

    def save(self):
        self.manager.update(self.name, self.data)

    def is_authenticated(self):
        return self.data.get('authenticated')

    def is_active(self):
        return self.data.get('active')

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name

    """Not Used"""
    def check_password(self, password):
        """Return True, return False, or raise NotImplementedError if the
        authentication_method is missing or unknown."""
        authentication_method = self.data.get('authentication_method', None)
        if authentication_method is None:
            authentication_method = get_default_authentication_method()
        # See comment in UserManager.add_user about authentication_method.
        if authentication_method == 'hash':
            result = check_hashed_password(password, self.get('hash'))
        elif authentication_method == 'cleartext':
            result = (self.get('password') == password)
        else:
            raise NotImplementedError(authentication_method)
        return result


def get_default_authentication_method():
    return current_app.config.get('DEFAULT_AUTHENTICATION_METHOD', 'cleartext')


def make_salted_hash(password, salt=None):
    if not salt:
        salt = os.urandom(64)
    d = hashlib.sha512()
    d.update(salt[:32])
    d.update(password)
    d.update(salt[32:])
    return binascii.hexlify(salt) + d.hexdigest()


def check_hashed_password(password, salted_hash):
    salt = binascii.unhexlify(salted_hash[:128])
    return make_salted_hash(password, salt) == salted_hash


def protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_app.config.get('PRIVATE') and not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return wrapper
