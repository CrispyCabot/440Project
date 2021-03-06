"""
    Forms
    ~~~~~
"""
import sqlite3

from flask_wtf import Form
from wtforms import BooleanField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError

from config import USER_DIR
from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import UserManager


class URLForm(Form):
    url = TextField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(Form):
    term = TextField('', [InputRequired()])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(Form):
    title = TextField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = TextField('')


class LoginForm(Form):
    name = TextField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    # This now queries to see if a user with the given username exists in the database
    def validate_name(form, field):
        dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
        dbCur = dbCon.cursor()
        dbCur.execute("SELECT username FROM users WHERE username = ?", (field.data,))
        data = dbCur.fetchone()
        # user = current_users.get_user(field.data)
        if not data:
            raise ValidationError('Incorrect Username')

    # This now queries to check and see if the password in the database matches the one given.
    def validate_password(form, field):
        dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
        dbCur = dbCon.cursor()
        dbCur.execute("SELECT * FROM users WHERE username = ?", (form.name.data,))
        data = dbCur.fetchone()
        if not data:
            raise ValidationError('That User Does Not Exist')
        if data[1] != form.password.data:
            raise ValidationError('Incorrect Password')


"""New form for registering new users"""


class RegisterForm(Form):
    name = TextField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    """Checks database to see if a user with the entered username exists"""

    def validate_name(form, field):
        dbCon = sqlite3.connect(USER_DIR + '/Users.sqlite')
        dbCur = dbCon.cursor()
        dbCur.execute("SELECT username FROM users WHERE username = ?", (field.data,))
        data = dbCur.fetchone()
        # user = current_users.get_user(field.data)
        if data:
            raise ValidationError('Someone Already has registered with this username')

    def add_new_user(self, name, password):
        userManager = UserManager(self)
        userManager.add_user(name, password)
