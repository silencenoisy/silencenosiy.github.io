from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, MovieForm
from app.models import Admin, User, Movie, Tag, Comment
from functools import wraps
from app import db, app
import os
import datetime
import uuid
from werkzeug.utils import secure_filename


def admin_login_req(fun):
    @wraps(fun)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return fun(*args, **kwargs)

    return decorated_function


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@admin.route("/")
def home():
    return redirect(url_for("admin.login"))


@admin.route("/index/")
@admin_login_req
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
def logout():
    session.pop("admin", None)
    return redirect(url_for('admin.login'))


@admin.route("/movie/<int:page>/", methods=["GET"])
@admin_login_req
def movie(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    tag = Tag
    return render_template("admin/movie.html", page_data=page_data, tag=tag)


@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.url.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data["title"],
            url=url,
            logo=logo,
            playnum=0,
            commentnum=0,
            author="admin",
            tag_id=int(data["tag"]),
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加成功", "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/del/<int:id>/", methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("admin.movie", page=1))


@admin.route("/user/<int:page>/", methods=["GET"])
@admin_login_req
def user(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/user.html", page_data=page_data)


@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
def user_del(id=None):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("admin.user", page=1))


@admin.route("/comments/<int:page>/",methods=["GET"])
@admin_login_req
def comments(page=None):
    if page is None:
        page = 1
    user = User
    comments = Comment.query.all()

    page_data = Comment.query.order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    tag = Tag
    movie = Movie
    return render_template("admin/comments.html", page_data=page_data, tag=tag, comments=comments,
                           movie=movie,user=user)



@admin.route("/comments/del/<int:id>/", methods=["GET"])
@admin_login_req
def comments_del(id=None):
    comments = Comment.query.filter_by(id=id).first_or_404()
    db.session.delete(comments)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("admin.comments", page=1))



@admin.route("/account/")
@admin_login_req
def account():
    return render_template("admin/account.html")
