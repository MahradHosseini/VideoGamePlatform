from flask import *
import sqlite3
import re
app = Flask(__name__)
app.secret_key="123"

@app.route("/register")
def showRegistration():
    return render_template("registration.html")

@app.route("/applyregistration", methods=["GET", "POST"])
def applyregistration():
    try:
        username = request.form["username"]
        password = request.form["pwd"]
        fullname = request.form["fullname"]
        emailaddress = request.form["emailaddress"]
        isadmin = bool(re.search("\w+@game.metu.edu.tr",emailaddress))
        #check password

        conn = sqlite3.connect("PlatformDB.db")
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        if row != None:
            return render_template("registration.html", msg="User already exist!")

        c.execute("INSERT INTO User VALUES(?,?,?,?,?)", (username, password, fullname, emailaddress, isadmin))
        conn.commit()
        conn.close()
        return render_template("registrationConfirmation.html")
        #Hint: Check |safe for the template to be able to consider HTML tags
    except:
        return render_template("registration.html", msg="Error")

@app.route("/")
@app.route("/homepage")
def homePage():
    print(session)
    if "username" in session:
        is_admin = session.get("isAdmin", False)
        return render_template("homepage.html", username=session["username"],isAdmin = is_admin)
    else:
        return render_template("homepage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form["username"]
    pwd = request.form["pwd"]

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()
    c.execute("SELECT * FROM User WHERE username=? AND password=?", (username, pwd))
    row = c.fetchone()
    if row:
        session["username"] = username
        session["isAdmin"] = row[4]  # Store the isAdmin value in the session
        return redirect(url_for("homePage"))
    else:
        return render_template("homepage.html", msg="Invalid login credentials!")
@app.route("/logout")
def logout():
    session.pop("username","")
    return redirect(url_for("homePage"))

if __name__ == "__main__":
    app.run()