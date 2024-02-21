"""REST API for posts."""
import flask
import insta485
import arrow


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_posts():
    """Display 10 newest posts."""
    size_param = flask.request.args.get("size", default=10, type=int)
    if (size_param <= 0):
        # raise insta485.api.api.InvalidUsage('Bad Request', status_code=400)
        return flask.jsonify({}), 400
    page_param = flask.request.args.get(
        "page", default=0, type=int) * size_param
    if (page_param < 0):
        # raise insta485.api.api.InvalidUsage('Bad Request', status_code=400)
        return flask.jsonify({}), 400
    postid_lte_param = flask.request.args.get(
        "postid_lte", default=200, type=int)
    if (postid_lte_param < 0):
        return flask.jsonify({}), 400
    # 200 was chosen for arbitrarily large num, later changed below

    next = ""
    context = {}

    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    posts = db_connect.execute(
        "SELECT postid "
        "FROM posts "
        "WHERE (owner = ? OR owner IN "
        "(SELECT username2 FROM following WHERE username1 = ?)) "
        "AND postid <= ?"
        "ORDER BY postid DESC "
        "LIMIT ? OFFSET ?;",
        (logname, logname, postid_lte_param, size_param, page_param)
    ).fetchall()

    first_post_id = 0
    for post in posts:
        first_post_id = max(post["postid"], first_post_id)
        post["url"] = "/api/v1/posts/" + str(post["postid"]) + "/"

    if postid_lte_param == 200:
        postid_lte_param = first_post_id
    if len(posts) >= size_param:
        next = "/api/v1/posts/?size=" + \
            str(size_param) + "&page=" + str(page_param+1) + \
            "&postid_lte=" + str(postid_lte_param)
    context["next"] = next
    context["results"] = posts[:10]
    temp = flask.request.query_string.decode("utf-8")
    if temp == "":
        context["url"] = flask.request.path
    else:
        context["url"] = flask.request.path + "?" + temp
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Display details for one post."""
    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    postid = postid_url_slug
    context = {}

    context['postid'] = postid
    context['postShowUrl'] = "/posts/" + str(context['postid']) + "/"
    context["url"] = "/api/v1" + context['postShowUrl']

    db_connect = insta485.model.get_db()
    post = db_connect.execute(
        "SELECT filename AS img_url, owner, created FROM posts "
        "WHERE postid = ?;",
        (postid,)
    ).fetchone()
    if post is None:
        return flask.jsonify({}), 404
    context["owner"] = post["owner"]
    context["imgUrl"] = insta485.views.index.upload_url(post["img_url"])
    context["comments_url"] = "/api/v1/comments/?postid=" + str(postid)
    context['created'] = post['created']
    context["ownerImgUrl"] = db_connect.execute(
        "SELECT filename as owner_img_url FROM users "
        "WHERE username = ?;",
        (post["owner"],)
    ).fetchone()["owner_img_url"]
    context["ownerImgUrl"] = insta485.views.index.upload_url(
        context["ownerImgUrl"])
    context["ownerShowUrl"] = "/users/" + context["owner"] + "/"
    numLikes = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE postid = ?;",
        (postid,)
    ).fetchone()["num"]
    lognameLikesThis = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE postid = ? AND owner = ?;",
        (postid, logname)
    ).fetchone()["num"]
    likeurl = None
    if lognameLikesThis:
        likeid = db_connect.execute(
            "SELECT likeid FROM likes "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()['likeid']
        # likeid = likeid['likeid']
        likeurl = "/api/v1/likes/" + str(likeid) + "/"
        lognameLikesThis = True
    else:
        lognameLikesThis = False

    context["likes"] = {"lognameLikesThis": lognameLikesThis,
                        "numLikes": numLikes, "url": likeurl}

    context["comments"] = db_connect.execute(
        "SELECT owner, text, commentid FROM comments "
        "WHERE postid = ? "
        "ORDER BY commentid;",
        (postid,)
    ).fetchall()
    for i in context["comments"]:
        if (logname == i["owner"]):
            i["lognameOwnsThis"] = True
        else:
            i["lognameOwnsThis"] = False
        i["url"] = "/api/v1/comments/" + str(i["commentid"]) + "/"
        i["ownerShowUrl"] = "/users/" + i["owner"] + "/"
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_likes():
    """Create one like for a specific post."""
    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    postid = flask.request.args.get("postid", type=int)
    if postid < 1:
        # raise insta485.api.api.InvalidUsage('Bad Request', status_code=400)
        return flask.jsonify({}), 400
    context = {}
    lognameLikesThis = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE postid = ? AND owner = ?;",
        (postid, logname)
    ).fetchone()["num"]
    if lognameLikesThis:
        like_id = db_connect.execute(
            "SELECT likeid FROM likes "
            "WHERE postid = ? AND owner = ?;",
            (postid, logname)
        ).fetchone()["likeid"]
        context["likeid"] = like_id
        context["url"] = "/api/v1/likes/" + str(like_id) + "/"
        return flask.jsonify(**context)
    db_connect.execute(
        "INSERT INTO likes(owner,postid) "
        "VALUES (?,?);",
        (logname, postid)
    )
    like_id = db_connect.execute(
        "SELECT likeid FROM likes "
        "WHERE postid = ? AND owner = ?;",
        (postid, logname)
    ).fetchone()["likeid"]
    context["likeid"] = like_id
    context["url"] = "/api/v1/likes/" + str(like_id) + "/"
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/likes/<int:likeid_url_slug>/', methods=['DELETE'])
def delete_like(likeid_url_slug):
    """Delete one like on a post."""
    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    context = {}
    likeid = likeid_url_slug
    likeid_exists = db_connect.execute(
        "SELECT COUNT(*) AS num FROM likes "
        "WHERE likeid = ?;",
        (likeid,)
    ).fetchone()["num"]
    if not likeid_exists:
        return flask.jsonify({}), 404
    else:
        likeid_from_owner = db_connect.execute(
            "SELECT COUNT(*) AS num FROM likes "
            "WHERE likeid = ? AND owner = ?;",
            (likeid, logname)
        ).fetchone()["num"]
        if not likeid_from_owner:
            return flask.jsonify({}), 403
        else:
            db_connect.execute(
                "DELETE FROM likes "
                "WHERE likeid = ?;",
                (likeid,)
            )
            return flask.jsonify({}), 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment():
    """Add one comment to a post."""
    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    postid = flask.request.args.get("postid", type=int)
    # try:
    text = flask.request.json["text"]
    # except (RuntimeError, TypeError, NameError):
    #   print("AAAUUGGHHHHGHH")
    context = {}
    if postid < 1:
        return flask.jsonify({}), 400
    db_connect.execute(
        "INSERT INTO comments(owner,postid,text) "
        "VALUES (?,?,?);",
        (logname, postid, text)
    )
    commentid = db_connect.execute(
        "SELECT last_insert_rowid() AS num;",
    ).fetchone()["num"]
    context["commentid"] = commentid
    context["lognameOwnsThis"] = True
    context["owner"] = logname
    context["ownerShowUrl"] = "/users/" + logname + "/"
    context["text"] = text
    context["url"] = "/api/v1/comments/" + str(commentid) + "/"
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid_url_slug>/',
                    methods=['DELETE'])
def delete_comment(commentid_url_slug):
    """Delete one comment."""
    logname = insta485.api.api.authenticate()
    db_connect = insta485.model.get_db()
    commentid = commentid_url_slug
    context = {}
    comment_exists = db_connect.execute(
        "SELECT COUNT(*) AS num FROM comments "
        "WHERE commentid = ?;",
        (commentid,)
    ).fetchone()["num"]
    if not comment_exists:
        return flask.jsonify({}), 404
    logname_owns_comment = db_connect.execute(
        "SELECT COUNT(*) AS num FROM comments "
        "WHERE commentid = ? AND owner = ?;",
        (commentid, logname)
    ).fetchone()["num"]
    if not logname_owns_comment:
        return flask.jsonify({}), 403
    else:
        db_connect.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?;",
            (commentid,)
        )
    return flask.jsonify({}), 204
