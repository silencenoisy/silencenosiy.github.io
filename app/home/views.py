from . import home
from flask import render_template, redirect, url_for, flash, session, request, Response
from app.home.forms import LoginForm, RegistForm, UserdetailForm, PasswordChangeForm, MovieForm, CommentForm
from app.models import User, Movie, Tag, Likes, Moviecol, Comment
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db, app, rd
import uuid
import os
import datetime


def user_login_req(fun):
    @wraps(fun)
    def decorated_function(*args, **kwargs):
        if "id" not in session:
            return redirect(url_for("home.login", next=request.url))
        return fun(*args, **kwargs)

    return decorated_function


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(id=data["account"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误")
            return redirect(url_for("home.login"))
        session["id"] = user.id
        session["user_id"] = user.id
        return redirect(request.args.get("next") or url_for("home.user"))
    return render_template("home/login.html", form=form)


@home.route("/logout/")
def logout():
    session.pop("id", None)
    return redirect(url_for('home.index', page=1))


@home.route("/regist/", methods=["GET", "POST"])
def regist():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        return render_template("home/registed.html", id=user.id)
    return render_template("home/regist.html", form=form)


@home.route("/registed/")
def registed():
    return render_template("home/registed.html")


@home.route("/user/", methods=["POST", "GET"])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.phone.data = user.phone
        form.email.data = user.email
        form.info.data = user.info
        form.face.data = user.face
    if form.validate_on_submit():
        data = form.data
        if form.face.data:
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])
                os.chmod(app.config["FC_DIR"], "rw")
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"] + user.face)

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称重复", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("电话重复", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱重复", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功", "ok")
        return redirect(url_for("home.user"))

    return render_template("home/user.html", form=form, user=user)


@home.route("/mymovie/<int:page>/", methods=["GET"])
@user_login_req
def mymovie(page=None):
    if page is None:
        page = 1
    user = User.query.get(int(session["user_id"]))
    movie = Movie.query.filter_by(author=user.name)
    page_data = movie.order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    tag = Tag
    return render_template("home/mymovie.html", page_data=page_data, tag=tag)


@home.route("/mymovie/add/", methods=["GET", "POST"])
@user_login_req
def movie_add():
    form = MovieForm()
    user = User.query.get(int(session["user_id"]))
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
            author=user.name,
            tag_id=int(data["tag"]),
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加成功", "ok")
        return redirect(url_for('home.movie_add'))

    return render_template("home/movie_add.html", form=form)


@home.route("/mymovie/del/<int:id>/", methods=["GET"])
@user_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("home.mymovie", page=1))


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PasswordChangeForm()
    user = User.query.get(int(session["user_id"]))
    if form.validate_on_submit():
        data = form.data
        if not user.check_pwd(data["oldpwd"]):
            flash("密码错误")
            return redirect(url_for("home.pwd"))
        user.pwd = generate_password_hash(data["newpwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改成功")
        return redirect(url_for("home.pwd"))

    return render_template("home/pwd.html", form=form)


@home.route("/comments/<int:page>/", methods=["GET"])
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
    user = User.query.get(int(session["user_id"]))
    comments = Comment.query.filter_by(user_id=user.id)

    page_data = comments.order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    tag = Tag
    movie = Movie
    return render_template("home/comments.html", page_data=page_data, tag=tag, comments=comments,
                           movie=movie)


@home.route("/comments/del/<int:id>/", methods=["GET"])
@user_login_req
def comments_del(id=None):
    comments = Comment.query.filter_by(id=id).first_or_404()
    db.session.delete(comments)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("home.comments", page=1))


@home.route("/moviecol/add/", methods=["GET"])
@user_login_req
def moviecol_add():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    moviecol = Moviecol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid)
    ).count()
    if moviecol == 1:
        data = dict(ok=0)
    else:
        moviecol = Moviecol(
            user_id=int(uid),
            movie_id=int(mid)
        )
        data = dict(ok=1)
        db.session.add(moviecol)
        db.session.commit()
    import json
    return json.dumps(data)


@home.route("/moviecol/<int:page>/", methods=["GET"])
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
    user = User.query.get(int(session["user_id"]))

    page_data = Moviecol.query.filter(
        User.id == session["user_id"]
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


@home.route("/moviecol/del/<int:id>/", methods=["GET"])
@user_login_req
def moviecol_del(id=None):
    moviecol = Moviecol.query.filter_by(id=id).first_or_404()
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除成功", "ok")
    return redirect(url_for("home.moviecol", page=1))


@home.route("/like/add/", methods=["GET"])
@user_login_req
def like_add():
    uid = request.args.get("uid", "")
    mid = request.args.get("mid", "")
    like = Likes.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid)
    ).count()
    if like == 1:
        data = dict(ok=0)
    else:
        like = Likes(
            user_id=int(uid),
            movie_id=int(mid)
        )
        data = dict(ok=1)
        db.session.add(like)
        db.session.commit()
    import json
    return json.dumps(data)


# @home.route("/tm/", methods=["GET", "POST"])
# def tm():
#     import json
#     if request.method == "GET":
#         id = request.args.get("id")
#         key = "movie" + str(id)
#         if rd.llen(key):
#             msgs = rd.lrange(key, 0, 2999)
#             res = {
#                 "code": 1,
#                 "danmaku": [json.loads(v) for v in msgs]
#             }
#         else:
#             res = {
#                 "code": 1,
#                 "danmaku": []
#             }
#         resp = json.dumps(res)
#     if request.method == "POST":
#         data = json.loads(request.get_data())
#         msg = {
#             "__v": 0,
#             "author": data["author"],
#             "time": data["time"],
#             "text": data["text"],
#             "color": data["color"],
#             "type": data["type"],
#             "ip": request.remote_addr,
#             "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
#             "player": [
#                 data["player"]
#             ]
#         }
#         res = {
#             "code": 1,
#             "data": msg
#         }
#         resp = json.dumps(res)
#         rd.lpush("movie" + str(data["player"]), json.dumps(msg))
#
#     return Response(resp, mimetype="application/json")


@home.route("/")
def first():
    return render_template("home/first.html")


@home.route("/index/<int:page>/", methods=["GET"])
def index(page=None):
    if page is None:
        page = 1
    tags = Tag.query.all()
    page_data = Movie.query

    tag_id = request.args.get("tag_id", 0)
    if int(tag_id) != 0:
        page_data = page_data.filter_by(tag_id=int(tag_id))

    time = request.args.get("time", 1)
    if time != 0:
        if time == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )

    movie = Movie.query.all()
    page_data = page_data.paginate(page=int(page), per_page=10)
    p = dict(
        tag_id=tag_id,
        time=time
    )

    return render_template("home/index.html", tags=tags, page_data=page_data, movie=movie, p=p)


@home.route("/play/<int:id>/<int:page>/", methods=["GET", "POST"])
def play(id=None, page=None):
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first()
    like = Likes.query.filter_by(movie_id=id).count()
    col = Moviecol.query.filter_by(movie_id=id).count()
    movie.playnum = movie.playnum + 1

    form = CommentForm()
    if "id" in session:
        user = User.query.get(int(session["user_id"]))

    if ("id" in session) and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["comment"],
            movie_id=movie.id,
            user_id=user.id
        )
        db.session.add(comment)
        db.session.commit()
        movie.playnum = movie.playnum + 1
        db.session.add(movie)
        flash("添加评论成功", "ok")
        return redirect(url_for('home.play', id=movie.id, page=1))
    db.session.add(movie)
    db.session.commit()
    users = User
    if page is None:
        page = 1
    page_data = Comment.query.filter_by(movie_id=movie.id)
    page_data = page_data.order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/play.html", movie=movie, like=like, users=users,
                           col=col, form=form, page=page, page_data=page_data, mimetype='application/json')


@home.route("/tm/v3/", methods=["GET", "POST"])
def tm():
    import json
    if request.method == "GET":
        # 获取弹幕消息队列
        mid = request.args.get("id")
        key = "movie" + str(mid)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 0,
                "data": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data["type"],
            "ip": request.remote_addr,
            "player": data["id"]
        }
        res = {
            "code": 0,
            "danmaku": msg
        }
        resp = json.dumps(res)
        msg = [data["time"], data["type"], data["color"], data["author"], data["text"]]
        rd.lpush("movie" + str(data["id"]), json.dumps(msg))
    return Response(resp, mimetype="application/json")

