"""REST API for posts."""
import flask
import insta485


class InvalidUsage(Exception):
    """Return an error status code."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """initialize."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Create dictionary and return."""
        response_dict = dict(self.payload or ())
        response_dict['message'] = self.message
        response_dict['status_code'] = self.status_code
        return response_dict


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Return error message."""
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def authenticate():
    """Return logname if user is logged in, request authorization if else."""
    db_connect = insta485.model.get_db()
    if "logname" in flask.session:
        return flask.session["logname"]
    else:
        if flask.request.authorization is None:
            raise insta485.api.api.InvalidUsage('Forbidden', status_code=403)
        else:
            username = flask.request.authorization['username']
            password = flask.request.authorization['password']
            if db_connect.execute(
                "SELECT COUNT(*) AS num FROM users "
                "WHERE username = ?;",
                (username,)
            ).fetchone()["num"] == 0:
                raise insta485.api.api.InvalidUsage(
                    'Forbidden', status_code=403)
                # return flask.jsonify({}), 403
            password_gt = db_connect.execute(
                "SELECT password FROM users "
                "WHERE username = ?;",
                (username,)
            ).fetchone()["password"]
            if not insta485.views.index.password_match(password, password_gt):
                raise insta485.api.api.InvalidUsage(
                    'Forbidden', status_code=403)
                # return flask.jsonify({}), 403

        flask.session["logname"] = username
        return flask.session["logname"]


@insta485.app.route('/api/v1/')
def get_api():
    """Return api when requested."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)
