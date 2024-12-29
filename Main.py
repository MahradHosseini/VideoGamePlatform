import traceback
from logging import exception

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
    msg = "Error"
    try:
        username = request.form["username"]
        password = request.form["pwd"]
        fullname = request.form["fullname"]
        emailaddress = request.form["emailaddress"]

        isadmin = bool(re.search(r"\w+@game\.metu\.edu\.tr", emailaddress))
        if not re.match(r"\w+@\w+\.\w+",emailaddress):
            msg = "Please enter a correct email"
            raise Exception

        msg = checkPassword(password)
        if not msg=="success":
            raise Exception

        conn = sqlite3.connect("PlatformDB.db")
        c = conn.cursor()
        c.execute("SELECT * FROM User WHERE username=?", (username,))
        row = c.fetchone()
        if row is not None:
            msg = "User already exist!"
            return render_template("registration.html", msg=msg)

        c.execute("INSERT INTO User VALUES(?,?,?,?,?)", (username, password, fullname, emailaddress, isadmin))
        conn.commit()
        conn.close()
        return render_template("registrationConfirmation.html")

    except:
        return render_template("registration.html", msg=msg)

def checkPassword(password):
    count_uppercase = 0
    count_lowercase = 0
    count_digit = 0

    if len(password) < 10:
        msg = "Password length must be at least 10 digits"
        return msg

    for char in password:
        if char.isdigit():
            count_digit += 1
        if char.islower():
            count_lowercase += 1
        if char.isupper():
            count_uppercase += 1

    if count_digit < 1 or count_lowercase < 1 or count_uppercase < 1:
        msg = "Password must contain at least 1 uppercase, 1 lowercase, 1 digit."
        return msg
    return "success"


@app.route("/")
@app.route("/homepage")
def homePage():

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()

    c.execute("SELECT name FROM Genre")

    genres = [row[0] for row in c.execute("SELECT name FROM Genre").fetchall()]

    conn.close()
    if "username" in session:
        is_admin = session.get("isAdmin", False)
        return render_template(
            "homepage.html",
            username=session["username"],
            isAdmin=is_admin,
            genres=genres)
    else:
        return render_template("homepage.html",genres=genres)


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
    session.pop("username", "")
    return redirect(url_for("homePage"))


@app.route("/publishGames",methods=["GET","POST"])
def publishedGames():
    try:
        # Establish connection with the database
        conn = sqlite3.connect("PlatformDB.db")
        c = conn.cursor()

        # Fetching all the genres to display then in checkboxs
        c.execute("SELECT * FROM Genre")
        rows = c.fetchall()

        # Storing genres in session
        session["genres"] = [row[1] for row in rows]


        # Fetching Table information
        c.execute("SELECT * FROM Game WHERE PublishedBy = ?", (session["username"],))
        games = c.fetchall()

        gameInfo = []
        for game in games:
            genreNames = []
            c.execute("SELECT genreID FROM GameGenre WHERE gameID = ?",(game[0],))
            genreids = c.fetchall()
            for genreid in genreids:
                c.execute("SELECT name FROM Genre WHERE genreID= ? ",genreid)
                gname = c.fetchone()
                if gname:
                    genreNames.append(gname[0])

            genreNames= ",".join(genreNames)

            gameInfo.append((game[0],game[1],game[3],genreNames))

        session["publishedGames"] = gameInfo
        conn.close()
        return render_template("publishGames.html", genres=session["genres"], publishedGames=session["publishedGames"])

    except Exception as e:
        return render_template("publishGames.html", msg="Error", genres=session["genres"], publishedGames=session["publishedGames"])


@app.post("/createGame")
def createGame():
    try:
        # Establish Connection with the database
        conn = sqlite3.connect("PlatformDB.db")
        c = conn.cursor()

        # Taking the input from Form
        title = request.form["title"]
        price = request.form["price"]
        selectedGenres = request.form.getlist("genres[]")
        description = request.form["description"]
        fullRelease = request.form["release"]

        # Adding the game to Game table
        c.execute(
            "INSERT INTO Game(title, price, description, isFullReleased, publishedBy) VALUES(?,?,?,?,?) RETURNING gameID, title"
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
                c.execute("INSERT INTO gameGenre(gameID,genreID) VALUES (?,?)", (gameID, genre[0]))

        conn.commit()
        conn.close()

        return redirect(url_for("publishedGames"))
    except Exception as e:
        msg = "An Error Occurred!"
        return render_template("publishGames.html", genres=session["genres"], msg=msg)

@app.route("/deleteGame",methods=["GET"])
def deleteGame():
    # request the game id from the form
    gameID = request.args.get("gameID")

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()

    # Delete game from Game table
    c.execute("DELETE FROM Game WHERE gameID = ?",gameID)
    # Delete game from GameGenre table
    c.execute("DELETE FROM GameGenre WHERE gameID = ?",gameID)

    conn.commit()
    conn.commit()
    return redirect(url_for("publishedGames"))

@app.route("/manageGenres", methods=["GET", "POST"])
def manageGenres():
    username = session.get("username", None)
    isAdmin = session.get("isAdmin", False)

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()

    genres = c.execute("SELECT name FROM Genre").fetchall()
    genreList = [row[0] for row in genres]

    conn.close()
    return render_template("manageGenres.html", username=username, genres=genreList, isAdmin=isAdmin)


@app.route("/addGenre", methods=["POST"])
def addGenre():
    if 'username' not in session or not session.get("isAdmin", False):
        return "Access denied", 403

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()

    genreName = request.form["genre"]
    c.execute("INSERT INTO Genre(name) VALUES(?)", (genreName,))

    conn.commit()
    conn.close()
    return redirect(url_for("manageGenres"))


@app.route("/deleteGenre", methods=["POST"])
def deleteGenre():
    if 'username' not in session or not session.get("isAdmin", False):
        return "Access denied", 403

    genreToDelete = request.form["genre"]
    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()
    c.execute("DELETE FROM Genre Where name = ?", (genreToDelete,))
    conn.commit()
    conn.close()

    return redirect(url_for("manageGenres"))


@app.route("/myProfile", methods=["GET", "POST"])
def myProfile():
    username = session.get("username", None)

    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()
    c.execute("SELECT name, email FROM User WHERE username = ?", (username,))

    row = c.fetchone()
    name = row[0]
    email = row[1]

    conn.close()
    return render_template("myProfile.html", username=username, name=name, email=email)


@app.route("/changePassword", methods=["POST"])
def changePassword():
    try:
        newPassword = request.form["password"]
        username = session.get("username", None)

        conn = sqlite3.connect("PlatformDB.db")
        c = conn.cursor()
        c.execute("UPDATE User SET password = ? WHERE username = ?", (newPassword, username))

        conn.commit()
        conn.close()
        return redirect(url_for("myProfile") + "?status=success")
    except Exception as e:
        print(e)
        return redirect(url_for("myProfile" + "?status=failure"))


@app.route("/querySearch", methods=["POST"])
def querySearch():
    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()

    c.execute("SELECT name FROM Genre")
    genres = [row[0] for row in c.fetchall()]

    results = None
    selectedGenre = "All Genres"

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        selectedGenre = request.form.get("genre", "All Genres")

        query = """
        SELECT g.title, g.description, g.isFullReleased, group_concat(ge.name) AS genres, g.gameID
        FROM Game g
        JOIN GameGenre gg ON g.gameID = gg.gameID
        JOIN Genre ge ON gg.genreID = ge.genreID
        WHERE (g.title LIKE ? OR g.description LIKE ?)"""

        params = [f"%{keyword}%", f"%{keyword}%"]

        if selectedGenre != "All Genres":
            query += " AND ge.name = ?"
            params.append(selectedGenre)

        query += "GROUP BY g.gameID"

        c.execute(query, params)
        games = c.fetchall()

        if selectedGenre == "All Genres":
            categorizedResults = {}
            for genre in genres:
                categorizedResults[genre] = [
                    game for game in games if genre in game[3].split(",")
                ]
            results = categorizedResults
        else:
            results = games

    conn.close()

    if "username" in session:
        is_admin = session.get("isAdmin", False)
        return render_template(
            "homepage.html",
            username=session["username"],
            isAdmin=is_admin,
            genres=genres,
            results=results,
            categorizedResults=categorizedResults if selectedGenre == "All Genres" else None,
            selectedGenre=selectedGenre)
    else:
        return render_template(
            "homepage.html",
            genres=genres,
            results=results,
            categorizedResults=categorizedResults if selectedGenre == "All Genres" else None,
            selectedGenre=selectedGenre)

@app.route("/seeSelectedGame/<int:gameID>")
def seeSelectedGame(gameID):
    conn = sqlite3.connect("PlatformDB.db")
    c = conn.cursor()
    c.execute("""
        SELECT 
            g.title,
            g.description,
            group_concat(ge.name) AS genres,
            g.isFullReleased,
            g.price
        FROM Game g
        JOIN GameGenre gg ON g.gameID = gg.gameID
        JOIN Genre ge ON gg.genreID = ge.genreID
        WHERE g.gameID = ?
    """, (gameID,))

    game = c.fetchone()
    conn.close()

    if game:
        return render_template("seeSelectedGame.html",
                               game=game)
    else:
        return "Game not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

