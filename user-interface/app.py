from flask import *
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    return render_template("register.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/dashboard/", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/logout/<string:logout_type>/")
def logout(logout_type):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
