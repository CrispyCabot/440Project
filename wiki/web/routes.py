"""
    Routes
    ~~~~~~
"""
import os.path
from werkzeug.utils import secure_filename

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_file
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.forms import EditorForm, RegisterForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect, User
from wiki.web.user import UserManager

bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'], data['headers'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


"""Route used for creating a new user"""


@bp.route('/user/create/', methods=['GET', 'POST'])
def user_create():
    form = RegisterForm()
    if form.validate_on_submit():
        form.add_new_user(form.name.data, form.password.data)
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('register.html', form=form)


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass



@bp.route('/upload/', methods=['GET', 'POST'])
@protect
def upload():
    """
    This function uploads a given file if all requirements are met.
    """
    # Check if they are trying to "POST" a file
    if request.method == 'POST':
        # Get the file and assign it to a variable
        f = request.files['file']

        # Make sure the filename is secure (e.g. no spaces in name) and then split it
        filename = secure_filename(f.filename)
        file, extension = os.path.splitext(filename)

        # Run a while loop to check if name already exists.
        counter = 1
        while os.path.exists(os.path.join('content', filename)):
            # If name already exists, rename it with a number.
            filename = file + "(" + str(counter) + ")" + extension
            counter += 1

        # Check to see if the extension is indeed a markdown file.
        if filename.split('.')[-1] == 'md':
            # The next three lines reads the whole file, finds the size, and then converts it back to normal.
            f.seek(0, 2)
            size = f.tell()
            f.seek(0, 0)
            # Check to see if file size is under 100MB.
            if size <= 100:
                # If all requirements are met, save the file under the content folder and print a success message.
                f.save(os.path.join('content', filename))
                flash(f"File {filename} uploaded successfully")
                return render_template('upload.html')
            # If size is not under 100MB, print an error message.
            else:
                flash("Error: file size must be under 100MB")
                return render_template('upload.html')
        # If file extension not .md, print an error message.
        else:
            flash("Error: file extension must be .md")
            return render_template('upload.html')
    # Render upload.html when first viewing page
    else:
        return render_template('upload.html')


@bp.route('/tomd/<path:url>')
def tomd(url):
    """
    This function grabs the url of the file and allows you to download it
    """
    # Path from current directory to content directory
    path = f"../../content/{url}.md"
    # the send_file() function is built-in to Flask to download files
    return send_file(path, as_attachment=True)

@bp.route('/topdf/<path:url>/')
def topdf(url):
    page = current_wiki.get(url)
    file = current_wiki.topdf(page)
    return send_file(file, as_attachment=True)


@bp.route('/totxt/<path:url>/')
def totxt(url):
    page = current_wiki.get(url)
    file = current_wiki.totxt(page)
    return send_file(file, as_attachment=True)

@bp.route('/tohtml/<path:url>')
def tohtml(url):
    page = current_wiki.get(url)
    file = current_wiki.tohtml(page)
    return send_file(file, as_attachment=True)

"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

