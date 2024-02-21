"""
Insta485 index (main) view.

URLs include:
/
"""
from pathlib import Path

import os
import uuid
import hashlib
import flask
import arrow
import insta485


def uuid_gen():
    """Generate UUID."""
    # Unpack flask object
    fileobj = flask.request.files["file"]
    filename = fileobj.filename

    stem = uuid.uuid4().hex
    suffix = Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


def password_gen(password):
    """Generate password."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def password_match(password, password_gt):
    """Match password."""
    [algorithm, salt, password_hash] = password_gt.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    return hash_obj.hexdigest() == password_hash


@insta485.app.route('/', methods=['GET'])
def show_index():
    """Display / route."""
    # if "logname" not in flask.session:
    #     return flask.redirect(flask.url_for("show_login"))
    # logname = flask.session['logname']
    # context = {}
    # context['logname'] = logname

    # # Connect to database
    # db_connect = insta485.model.get_db()
    # posts = db_connect.execute(
    #     "SELECT postid, filename AS img_url, owner, created AS timestamp "
    #     "FROM posts "
    #     "WHERE owner = ? OR owner IN "
    #     "(SELECT username2 FROM following WHERE username1 = ?) "
    #     "ORDER BY postid DESC;",
    #     (logname, logname)
    # ).fetchall()

    # for post in posts:
    #     upload_file(post["img_url"])
    #     post["img_url"] = upload_url(post["img_url"])
    #     post['timestamp'] = arrow.get(post['timestamp']).humanize()
    #     post["owner_img_url"] = db_connect.execute(
    #         "SELECT filename as owner_img_url FROM users "
    #         "WHERE username = ?;",
    #         (post["owner"],)
    #     ).fetchone()["owner_img_url"]
    #     upload_file(post["owner_img_url"])
    #     post["owner_img_url"] = upload_url(post["owner_img_url"])
    #     post["likes"] = db_connect.execute(
    #         "SELECT COUNT(*) AS num FROM likes "
    #         "WHERE postid = ?;",
    #         (post["postid"],)
    #     ).fetchone()["num"]
    #     post["like"] = db_connect.execute(
    #         "SELECT COUNT(*) AS num FROM likes "
    #         "WHERE postid = ? AND owner = ?;",
    #         (post["postid"], logname)
    #     ).fetchone()["num"]
    #     post["comments"] = db_connect.execute(
    #         "SELECT owner, text, commentid FROM comments "
    #         "WHERE postid = ? "
    #         "ORDER BY commentid;",
    #         (post["postid"],)
    #     ).fetchall()
    # context["posts"] = posts
    return flask.render_template("index.html")


@insta485.app.route('/uploads/<filename>')
def upload_file(filename):
    """Upload file."""
    if "logname" not in flask.session:
        flask.abort(403)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], filename)


def upload_url(filename):
    """Change url."""
    return str(Path("/uploads") / filename)


@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def show_user(user_url_slug):
    """Display /users/<user_url_slug>/ route."""
    username = user_url_slug
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    db_connect = insta485.model.get_db()
    valid_username = db_connect.execute(
        "SELECT * FROM users "
        "WHERE username = ?",
        (username,)
    ).fetchall()
    if (len(valid_username)) == 0:
        flask.abort(404)
    logname = flask.session['logname']
    context = {}
    context['logname'] = logname
    context['username'] = username
    context["logname_follows_username"] = db_connect.execute(
        "SELECT COUNT(*) AS num FROM following "
        "WHERE username1 = ? AND username2 = ?;",
        (logname, username)
    ).fetchone()["num"] > 0
    posts = db_connect.execute(
        "SELECT postid, filename AS img_url FROM posts "
        "WHERE owner = ?;",
        (username,)
    ).fetchall()
    for post in posts:
        upload_file(post["img_url"])
        post["img_url"] = upload_url(post["img_url"])
    context["posts"] = posts
    context["total_posts"] = len(context["posts"])
    context["followers"] = db_connect.execute(
        "SELECT COUNT(*) AS num FROM following "
        "WHERE username2 = ?;",
        (username,)
    ).fetchone()["num"]
    context["following"] = db_connect.execute(
        "SELECT COUNT(*) AS num FROM following "
        "WHERE username1 = ?;",
        (username,)
    ).fetchone()["num"]
    context["fullname"] = db_connect.execute(
        "SELECT fullname FROM users "
        "WHERE username = ?",
        (username,)
    ).fetchone()["fullname"]

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/', methods=['GET'])
def show_followers(user_url_slug):
    """Display /users/<user_url_slug>/followers/ route."""
    username = user_url_slug
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    db_connect = insta485.model.get_db()
    valid_username = db_connect.execute(
        "SELECT * FROM users "
        "WHERE username = ?",
        (username,)
    ).fetchall()
    if (len(valid_username)) == 0:
        flask.abort(404)
    logname = flask.session['logname']
    context = {}
    context['logname'] = logname
    context['username'] = username
    followers = db_connect.execute(
        "SELECT username1 AS username FROM following "
        "WHERE username2 = ?;",
        (username,)
    ).fetchall()
    for follower in followers:
        follower["user_img_url"] = db_connect.execute(
            "SELECT filename AS user_img_url FROM users "
            "WHERE username = ?",
            (follower["username"],)
        ).fetchone()["user_img_url"]
        upload_file(follower["user_img_url"])
        follower["user_img_url"] = upload_url(follower["user_img_url"])
        follower["logname_follows_username"] = db_connect.execute(
            "SELECT COUNT(*) AS num FROM following "
            "WHERE username1 = ? AND username2 = ?;",
            (logname, follower["username"])
        ).fetchone()["num"] > 0

    context["followers"] = followers
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/', methods=['GET'])
def show_following(user_url_slug):
    """Display /users/<user_url_slug>/following/ route."""
    username = user_url_slug
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    db_connect = insta485.model.get_db()
    valid_username = db_connect.execute(
        "SELECT * FROM users "
        "WHERE username = ?",
        (username,)
    ).fetchall()
    if (len(valid_username)) == 0:
        flask.abort(404)

    logname = flask.session['logname']
    context = {}
    context['logname'] = logname
    context['username'] = username

    db_connect = insta485.model.get_db()
    following = db_connect.execute(
        "SELECT username2 AS username FROM following "
        "WHERE username1 = ?;",
        (username,)
    ).fetchall()

    for follower in following:
        follower["user_img_url"] = db_connect.execute(
            "SELECT filename AS user_img_url FROM users "
            "WHERE username = ?",
            (follower["username"],)
        ).fetchone()["user_img_url"]
        upload_file(follower["user_img_url"])
        follower["user_img_url"] = upload_url(follower["user_img_url"])
        if username == logname:
            follower["logname_follows_username"] = True
        else:
            follower["logname_follows_username"] = db_connect.execute(
                "SELECT COUNT(*) AS num FROM following "
                "WHERE username1 = ? AND username2 = ?;",
                (logname, follower["username"])
            ).fetchone()["num"] > 0

    context["following"] = following
    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/', methods=['GET'])
def show_explore():
    """Display /explore/ route."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session['logname']
    context = {}
    context['logname'] = logname

    db_connect = insta485.model.get_db()
    not_following = db_connect.execute(
        "SELECT username, filename AS user_img_url FROM users "
        "WHERE username NOT IN "
        "(SELECT username2 FROM following WHERE username1 = ?) "
        "AND username != ?;",
        (logname, logname)
    ).fetchall()

    for follower in not_following:
        upload_file(follower["user_img_url"])
        follower["user_img_url"] = upload_url(follower["user_img_url"])

    context["not_following"] = not_following
    return flask.render_template("explore.html", **context)


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Display /posts/<postid_url_slug>/ route."""
    postid = postid_url_slug
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session['logname']
    context = {}
    context['logname'] = logname
    context['postid'] = postid

    db_connect = insta485.model.get_db()
    post = db_connect.execute(
        "SELECT filename AS img_url, owner, created AS timestamp FROM posts "
        "WHERE postid = ?;",
        (postid,)
    ).fetchone()

    context["owner"] = post["owner"]
    upload_file(post["img_url"])
    context["img_url"] = upload_url(post["img_url"])
    context['timestamp'] = arrow.get(post['timestamp']).humanize()
    context["owner_img_url"] = db_connect.execute(
        "SELECT filename as owner_img_url FROM users "
        "WHERE username = ?;",
        (post["owner"],)
    ).fetchone()["owner_img_url"]
    upload_file(context["owner_img_url"])
    context["owner_img_url"] = upload_url(context["owner_img_url"])
    context["likes"] = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE postid = ?;",
        (postid,)
    ).fetchone()["num"]
    context["like"] = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE postid = ? AND owner = ?;",
        (postid, logname)
    ).fetchone()["num"]
    context["comments"] = db_connect.execute(
        "SELECT owner, text, commentid FROM comments "
        "WHERE postid = ? "
        "ORDER BY commentid;",
        (postid,)
    ).fetchall()

    return flask.render_template("post.html", **context)


@insta485.app.route('/likes/', methods=['POST'])
def handle_like():
    """Enable like."""
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    postid = flask.request.form["postid"]
    db_connect = insta485.model.get_db()
    if flask.request.form["operation"] == "like":
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM likes "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()["num"] > 0:
            flask.abort(409)
        db_connect.execute(
            "INSERT INTO likes (owner,postid) SELECT ?,? "
            "WHERE NOT EXISTS "
            "(SELECT * FROM likes "
            "WHERE owner = ? AND postid = ?);",
            (logname,
                flask.request.form['postid'],
                logname,
                flask.request.form['postid'])
        )
    elif flask.request.form["operation"] == "unlike":
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM likes "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()["num"] == 0:
            flask.abort(409)
        db_connect.execute(
            "DELETE FROM likes "
            "WHERE owner = ? AND postid = ?;",
            (logname, flask.request.form['postid'])
        )
    return flask.redirect(
        flask.request.args.get("target", default=flask.url_for("show_index")))


@insta485.app.route('/comments/', methods=['POST'])
def handle_comment():
    """Enable comment."""
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    db_connect = insta485.model.get_db()
    if flask.request.form["operation"] == "create":
        postid = flask.request.form["postid"]
        if ("text" not in flask.request.form) or \
                (len(flask.request.form["text"]) == 0):
            flask.abort(400)
        db_connect.execute(
            "INSERT INTO comments(owner, postid, text) "
            "VALUES (?, ?, ?);",
            (logname, postid, flask.request.form["text"])
        )
    elif flask.request.form["operation"] == "delete":
        commentid = flask.request.form["commentid"]
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM comments "
            "WHERE commentid = ? AND owner = ?;",
            (commentid, logname)
        ).fetchone()["num"] == 0:
            flask.abort(403)
        db_connect.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?;",
            (commentid,)
        )
    return flask.redirect(
        flask.request.args.get("target", default=flask.url_for("show_index")))


@insta485.app.route('/posts/', methods=['POST'])
def handle_post():
    """Enable post."""
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    db_connect = insta485.model.get_db()
    if flask.request.form["operation"] == "create":
        if ("file" not in flask.request.files) or \
                (len(flask.request.files["file"].filename) == 0):
            flask.abort(400)
        filename = uuid_gen()
        # flask.request.files["file"].save(
        #     str(insta485.app.config["UPLOAD_FOLDER"] / filename))
        #     os.path.join(insta485.config.UPLOAD_FOLDER, filename))
        db_connect.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (?, ?);",
            (filename, logname)
        )
    elif flask.request.form["operation"] == "delete":
        postid = flask.request.form["postid"]
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM posts "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()["num"] == 0:
            flask.abort(403)
        filename = db_connect.execute(
            "SELECT filename FROM posts "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()["filename"]
        os.remove(
            str(insta485.app.config["UPLOAD_FOLDER"] / filename))
        db_connect.execute(
            "DELETE FROM posts "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        )
    return flask.redirect(
        flask.request.args.get(
            "target",
            default=flask.url_for("show_user", user_url_slug=logname)))


@insta485.app.route('/following/', methods=['POST'])
def handle_follow():
    """Enable follow."""
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    username = flask.request.form["username"]
    db_connect = insta485.model.get_db()
    if flask.request.form["operation"] == "follow":
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM following "
            "WHERE username1 = ? AND username2 = ?;",
            (logname, username)
        ).fetchone()["num"] > 0:
            flask.abort(409)
        db_connect.execute(
            "INSERT INTO following (username1, username2) "
            "VALUES (?, ?);",
            (logname, username)
        )
    elif flask.request.form["operation"] == "unfollow":
        if db_connect.execute(
            "SELECT COUNT(*) AS num FROM following "
            "WHERE username1 = ? AND username2 = ?;",
            (logname, username)
        ).fetchone()["num"] == 0:
            flask.abort(409)
        db_connect.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?;",
            (logname, username)
        )
    return flask.redirect(
        flask.request.args.get("target", default=flask.url_for("show_index")))


@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /accounts/login/ route."""
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("login.html")


@insta485.app.route('/accounts/logout/', methods=['POST'])
def handle_logout():
    """Enable logout."""
    flask.session.clear()
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /accounts/create/ route."""
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("show_edit"))
    return flask.render_template("create.html")


@insta485.app.route('/accounts/delete/', methods=['GET'])
def show_delete():
    """Display /accounts/delete/ route."""
    if "logname" in flask.session:
        context = {"logname": flask.session["logname"]}
        return flask.render_template("delete.html", **context)
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /accounts/edit/ route."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session['logname']
    context = {}
    context['logname'] = logname

    db_connect = insta485.model.get_db()
    user = db_connect.execute(
        "SELECT fullname, email, filename AS user_img_url "
        "FROM users "
        "WHERE username = ?",
        (logname,)
    ).fetchone()
    context["fullname"] = user["fullname"]
    context["email"] = user["email"]
    upload_file(user["user_img_url"])
    context["user_img_url"] = upload_url(user["user_img_url"])
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/', methods=['GET'])
def show_password():
    """Display /accounts/password/ route."""
    if "logname" in flask.session:
        context = {"logname": flask.session["logname"]}
        return flask.render_template("password.html", **context)
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/', methods=['POST'])
def handle_account():
    """Enable account."""
    if flask.request.form["operation"] == "login":
        handle_login()
    elif flask.request.form["operation"] == "create":
        handle_create()
    elif flask.request.form["operation"] == "delete":
        handle_delete()
    elif flask.request.form["operation"] == "edit_account":
        handle_edit_account()
    elif flask.request.form["operation"] == "update_password":
        handle_update_password()
    return flask.redirect(
        flask.request.args.get("target", default=flask.url_for("show_index")))


def handle_login():
    """Handle login."""
    db_connect = insta485.model.get_db()
    if ("username" not in flask.request.form) or \
            (len(flask.request.form["username"]) == 0):
        flask.abort(400)
    if ("password" not in flask.request.form) or \
            (len(flask.request.form["password"]) == 0):
        flask.abort(400)
    if db_connect.execute(
        "SELECT COUNT(*) AS num FROM users "
        "WHERE username = ?;",
        (flask.request.form["username"],)
    ).fetchone()["num"] == 0:
        flask.abort(403)
    password_gt = db_connect.execute(
        "SELECT password FROM users "
        "WHERE username = ?;",
        (flask.request.form["username"],)
    ).fetchone()["password"]
    if not password_match(flask.request.form["password"], password_gt):
        flask.abort(403)
    flask.session["logname"] = flask.request.form["username"]


def handle_create():
    """Handle create."""
    db_connect = insta485.model.get_db()
    if ("username" not in flask.request.form) or \
            (len(flask.request.form["username"]) == 0):
        flask.abort(400)
    if ("password" not in flask.request.form) or \
            (len(flask.request.form["password"]) == 0):
        flask.abort(400)
    if ("fullname" not in flask.request.form) or \
            (len(flask.request.form["fullname"]) == 0):
        flask.abort(400)
    if ("email" not in flask.request.form) or \
            (len(flask.request.form["email"]) == 0):
        flask.abort(400)
    if ("file" not in flask.request.files) or \
            (len(flask.request.files["file"].filename) == 0):
        flask.abort(400)
    if db_connect.execute(
        "SELECT COUNT(*) AS num FROM users "
        "WHERE username = ?;",
        (flask.request.form["username"],)
    ).fetchone()["num"] > 0:
        flask.abort(409)
    filename = uuid_gen()
    # flask.request.files["file"].save(
    #     str(insta485.app.config["UPLOAD_FOLDER"] / filename))
    db_connect.execute(
        "INSERT INTO users "
        "(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?);",
        (flask.request.form["username"],
            flask.request.form["fullname"],
            flask.request.form["email"],
            filename,
            password_gen(flask.request.form["password"]))
    )
    flask.session["logname"] = flask.request.form["username"]


def handle_delete():
    """Handle delete."""
    db_connect = insta485.model.get_db()
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    old_filename = db_connect.execute(
        "SELECT filename FROM users "
        "WHERE username = ?;",
        (logname,)
    ).fetchone()["filename"]
    os.remove(
        str(insta485.app.config["UPLOAD_FOLDER"] / old_filename))

    posts = db_connect.execute(
        "SELECT filename FROM posts WHERE owner = ?;",
        (logname,)
    ).fetchall()
    for post in posts:
        os.remove(
            str(insta485.app.config["UPLOAD_FOLDER"] /
                post["filename"]))
    db_connect.execute(
        "DELETE FROM users WHERE username = ?;",
        (logname,)
    )
    flask.session.clear()


def handle_edit_account():
    """Handle edit_account."""
    db_connect = insta485.model.get_db()
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    if ("fullname" not in flask.request.form) or \
            (len(flask.request.form["fullname"]) == 0):
        flask.abort(400)
    if ("email" not in flask.request.form) or \
            (len(flask.request.form["email"]) == 0):
        flask.abort(400)
    if ("file" in flask.request.files) and \
            (len(flask.request.files["file"].filename) != 0):
        filename = uuid_gen()
        old_filename = db_connect.execute(
            "SELECT filename FROM users "
            "WHERE username = ?;",
            (logname,)
        ).fetchone()["filename"]
        os.remove(
            insta485.app.config["UPLOAD_FOLDER"] /
            old_filename)
        # flask.request.files["file"].save(
        #     insta485.app.config["UPLOAD_FOLDER"] / filename)
        db_connect.execute(
            "UPDATE users "
            "SET filename = ?, fullname = ?, email = ? "
            "WHERE username = ?;",
            (filename,
                flask.request.form["fullname"],
                flask.request.form["email"],
                logname)
        )
    else:
        db_connect.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?;",
            (flask.request.form["fullname"],
                flask.request.form["email"],
                logname)
        )


def handle_update_password():
    """Handle update_password."""
    db_connect = insta485.model.get_db()
    if "logname" not in flask.session:
        flask.abort(403)
    logname = flask.session["logname"]
    if ("password" not in flask.request.form) or \
            (len(flask.request.form["password"]) == 0):
        flask.abort(400)
    if ("new_password1" not in flask.request.form) or \
            (len(flask.request.form["new_password1"]) == 0):
        flask.abort(400)
    if ("new_password2" not in flask.request.form) or \
            (len(flask.request.form["new_password2"]) == 0):
        flask.abort(400)
    password_gt = db_connect.execute(
        "SELECT password FROM users "
        "WHERE username = ?;",
        (logname,)
    ).fetchone()["password"]
    if not password_match(flask.request.form["password"], password_gt):
        flask.abort(403)
    if flask.request.form["new_password1"] != \
            flask.request.form["new_password2"]:
        flask.abort(401)
    new_password = password_gen(flask.request.form["new_password1"])
    db_connect.execute(
        "UPDATE users SET password = ? "
        "WHERE username = ?;",
        (new_password, logname)
    )
