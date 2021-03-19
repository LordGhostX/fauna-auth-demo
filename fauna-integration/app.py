from flask import *
from flask_bootstrap import Bootstrap
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
from faunadb.errors import BadRequest

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = "APP_SECRET_KEY"
client = FaunaClient(secret="fnAEEmRX2dACBZAC9gXCXZLbMPPcCMQL7ut1-sH8")


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
    return render_template("login.html")


@app.route("/dashboard/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/logout/<string:logout_type>/")
def logout(logout_type):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
