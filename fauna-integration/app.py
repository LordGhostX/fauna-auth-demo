from functools import wraps
from flask import *
from flask_bootstrap import Bootstrap
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
from faunadb.errors import BadRequest, Unauthorized

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "APP_SECRET_KEY"
client = FaunaClient(secret="YOUR-SECRET-HERE")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_secret" in session:
            try:
                user_client = FaunaClient(secret=session["user_secret"])
                result = user_client.query(
                    q.current_identity()
                )
            except Unauthorized as e:
                session.clear()
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
        return f(result, *args, **kwargs)

    return decorated


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        fullname = request.form.get("fullname").strip()
        password = request.form.get("password")

        try:
            result = client.query(
                q.create(
                    q.collection("users"), {
                        "credentials": {"password": password},
                        "data": {
                            "email": email,
                            "fullname": fullname
                        }
                    }
                )
            )
        except BadRequest as e:
            flash("The account you are trying to create already exists!", "danger")
            return redirect(url_for("register"))

        flash(
            "You have successfully created your account, you can proceed to login!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        try:
            result = client.query(
                q.login(
                    q.match(q.index("users_by_email"), email), {
                        "password": password}
                )
            )
        except BadRequest as e:
            flash(
                "You have supplied invalid login credentials, please try again!", "danger")
            return redirect(url_for("login"))

        session["user_secret"] = result["secret"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard/", methods=["GET", "POST"])
@login_required
def dashboard(user):
    if request.method == "POST":
        old_password = request.form.get("old-password").strip()
        new_password = request.form.get("new-password").strip()

        try:
            result = client.query(
                q.identify(
                    q.ref(q.collection("users"), user.id()), old_password
                )
            )

            if not result:
                raise Exception()

            result = client.query(
                q.update(
                    q.ref(q.collection("users"), user.id()), {
                        "credentials": {"password": new_password}
                    }
                )
            )
        except Exception as e:
            flash(
                "You have supplied an invalid password!", "danger")
            return redirect(url_for("dashboard"))

        flash(
            "You have successfully changed your account password!", "success")
        return redirect(url_for("dashboard"))

    try:
        user_details = client.query(
            q.get(
                q.ref(q.collection("users"), user.id())
            )
        )
    except BadRequest as e:
        return redirect(url_for("logout", logout_type="current"))

    return render_template("dashboard.html", user_details=user_details)


@app.route("/dashboard/logout/<string:logout_type>/")
@login_required
def logout(user, logout_type):
    if logout_type == "all":
        all_tokens = True
    else:
        all_tokens = False

    try:
        user_client = FaunaClient(secret=session["user_secret"])
        result = user_client.query(
            q.logout(all_tokens)
        )
    except BadRequest as e:
        pass

    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
