import sqlite3
import time
import datetime
import os

DBFILENAME = "fast_typing.db"
TABLES = {}
TABLES["history"] = """CREATE TABLE history(time BIGINT, dictionary VARCHAR(30), speed INT, misstakes INT)"""


def create_db():

    con = sqlite3.connect(DBFILENAME)
    cur = con.cursor()
    for i in TABLES:
        cur.execute(TABLES[i])
    con.commit()
    con.close()


def check_db():
    con = sqlite3.connect(DBFILENAME)
    cur = con.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    if not len(tables) == len(TABLES):
        con.close()
        os.remove(DBFILENAME)
        return create_db()
    for i in tables:
        if i[1] != TABLES[i[0]]:
            con.close()
            os.remove(DBFILENAME)
            return create_db()


def add_result(speed, misstakes, type_of_dictionary):
    check_db()
    con = sqlite3.connect(DBFILENAME)
    cur = con.cursor()
    curtime = time.time_ns() // 1e9
    cur.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
                (curtime, type_of_dictionary, speed, misstakes))
    con.commit()
    con.close()


def get_data():
    check_db()
    con = sqlite3.connect(DBFILENAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM history")
    res = cur.fetchall()
    res = [[datetime.datetime.fromtimestamp(i[0]).strftime("%c"), *i[1:]]
           for i in sorted(res, key=lambda x: -x[0])]
    for i in range(len(res)):
        res[i].insert(0, i + 1)
    return res
