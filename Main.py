import traceback

from flask import *
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "123"


@app.route("/registration")
def showRegistration():
    return render_template("registration.html")


@app.route("/applyregistration", methods=["POST"])
def applyregistration():
    try:
        username = request.form["username"]
        password = request.form["pwd"]
        fullname = request.form["fullname"]
        emailaddress = request.form["emailaddress"]
        isadmin = bool(re.search(r"\w+@game\.metu\.edu\.tr", emailaddress))
        # check password

        conn = sqlite3.connect("PlatformDB")
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE username=?", (username,))
        row = c.fetchone()
        if row != None:
            return render_template("registration.html", msg="User already exist!")

        c.execute("INSERT INTO User VALUES(?,?,?,?,?)", (username, password, fullname, emailaddress, isadmin))
        conn.commit()
        conn.close()
        return render_template("registrationConfirmation.html")
        # Hint: Check |safe for the template to be able to consider HTML tags
    except:
        return render_template("registration.html", msg="Error")


@app.route("/")
@app.route("/homepage")
def homePage():
    print(session)
    if "username" in session:
        is_admin = session.get("isAdmin", False)
        return render_template("homepage.html", username=session["username"], isAdmin=is_admin)
    else:
        return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form["username"]
    pwd = request.form["pwd"]

    conn = sqlite3.connect("PlatformDB")
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
    session.pop("username", "")
    return redirect(url_for("homePage"))


@app.route("/publishGames")
def publishedGames():
    try:
        # Establish connection with the database
        conn = sqlite3.connect("PlatformDB")
        c = conn.cursor()

        # Fetching all the genres to display then in checkboxs
        c.execute("SELECT * FROM Genre")
        rows = c.fetchall()

        # Storing genres in session
        session["genres"] = [row[1] for row in rows]

        conn.close()
        return render_template("publishGames.html", genres = session["genres"])

    except Exception as e:
        return render_template("publishGames.html", msg = "Error", genres = session["genres"])


@app.post("/createGame")
def createGame():
    try:
        # Establish Connection with the database
        conn = sqlite3.connect("PlatformDB")
        c = conn.cursor()

        # Taking the input from Form
        title = request.form["title"]
        price = request.form["price"]
        selectedGenres = request.form.getlist("genres[]")
        description = request.form["description"]
        fullRelease = request.form["release"]

        genresString = ','.join(selectedGenres)

        # Adding the game to Game table
        c.execute("INSERT INTO Game(title, price, description, isFullReleased, publishedBy) VALUES(?,?,?,?,?) RETURNING gameID, title"
                  , (title, price, description, fullRelease, session["username"]))

        # Retrieving the last entered game to get its ID
        game = c.fetchone()
        gameID = game[0]
        gamename = game[1]

        # Finding the Genre ID to add both genre and game to genreGame Table (relationship)
        c.execute("SELECT * FROM Genre")
        genreRows = c.fetchall()

        # Making the relationship between genre and game
        for genre in genreRows:
            if genre[1] in selectedGenres:
                c.execute("INSERT INTO gameGenre(gameID,genreID) VALUES (?,?)", (gameID,genre[0]))

        conn.commit()
        conn.close()

        msg = "Game was added successfully!"
        return render_template("publishGames.html",msg = msg, genres = session["genres"])

    except Exception as e:
        msg = "An Error Occurred!"
        return render_template("publishGames.html", genres = session["genres"], msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
