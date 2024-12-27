import sqlite3


def createDB(dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    # Enable foreign key constraint enforcement
    c.execute("PRAGMA foreign_keys = ON;")

    c.execute("""
    CREATE TABLE User(
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        isAdmin BOOLEAN NOT NULL
    )""")

    c.execute("""
    CREATE TABLE Game(
        gameID INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price DOUBLE,
        description TEXT,
        isFullReleased BOOLEAN,
        publishedBy TEXT,
        FOREIGN KEY (publishedBy) REFERENCES User(username)
    )""")

    c.execute("""
    CREATE TABLE Genre(
        genreID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )""")

    c.execute("""
    CREATE TABLE GameGenre(
        gameID INTEGER NOT NULL,
        genreID INTEGER NOT NULL,
        FOREIGN KEY (gameID) REFERENCES Game(gameID),
        FOREIGN KEY (genreID) REFERENCES Genre(genreID)
    )""")

    conn.commit()
    conn.close()


def insertRecords(dbName):
    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    # Enable foreign key constraint enforcement
    c.execute("PRAGMA foreign_keys = ON;")

    users = [
        ("MahradH", "123", "Mahrad Hosseini", "mahrad.hosseini@game.metu.edu.tr", 1),
        ("HayaA", "123", "Haya Arabikatibi", "haya.arabikatibi@game.metu.edu.tr", 1),
        ("Serendipity", "321", "Homa Zabihi", "homa.zabihi@metu.edu.tr", 0),
        ("SerhanT", "312", "Serhan Turgul", "serhan.turgul@metu.edu.tr", 0)
    ]

    games = [
        ("AIBERG", 50, "AI-Based Endless Runner Game", 1, "SerhanT"),
        ("Pubg", 30, "Online Multiplayer Combat Game", 1, "Serendipity"),
        ("Drift Crazy", 40.5, "Realistic Drift Simulator", 1, "Serendipity")
    ]

    genres = [
        ("Simulation",),
        ("Action",),
        ("Casual",),
        ("Racing",)
    ]

    gameGenres = [
        (1, 3),
        (2, 2),
        (3, 1),
        (3, 4)
    ]

    c.executemany("INSERT INTO User VALUES (?, ?, ?, ?, ?)", users)
    c.executemany("INSERT INTO Game(title, price, description, isFullReleased, publishedBy) VALUES (?, ?, ?, ?, ?)",
                  games)
    c.executemany("INSERT INTO Genre(name) VALUES (?)", genres)
    c.executemany("INSERT INTO GameGenre(gameID, genreID) VALUES (?, ?)", gameGenres)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    createDB("PlatformDB.db")
    insertRecords("PlatformDB.db")
