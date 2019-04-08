from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegisterForm, EditProfileForm, CreatePostForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Post
from flask import request
from datetime import datetime


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('p', 1, type=int)
    pages = current_user.followed_posts().paginate(page, 5, True)
    return render_template("index.html", title='Home', posts = pages)


@app.route('/login', methods = ['GET', 'POST'])
def log_in():
    if current_user.is_authenticated:          ###if user already logined
        return redirect(url_for('index'))

    form = LoginForm()                         ### creating login form

    if form.validate_on_submit():            ##if not empty spaces
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid password or username')
            return redirect(url_for('log_in'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('sign_in.html', form=form, title='Sign in' )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('log_in'))

    return render_template('register.html', title='Register', form=form)

@app.route('/users/<username>',methods=['GET','POST'])
@login_required
def user(username):
    u = request.args.get('u')
####### SEARCHING
    if u:
        user = User.query.filter(User.username.contains(u))

        if user == None:
            user = User.query.filter_by(username=username).first_or_404()

        else:
            return render_template('users.html', user_list = user)
    else:
        user = User.query.filter_by(username=username).first_or_404()
########
    form = CreatePostForm()

    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('user', username=current_user.username))

    posts = user.posts

    return render_template('user.html', user=user, form = form, posts = posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changes saved')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))

    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))

    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/followers')
@login_required
def followers():
    u = current_user.followers
    return render_template('followers.html', user_list = u)

@app.route('/following')
@login_required
def following():
    u = current_user.followed
    return render_template('following.html', user_list = u)
