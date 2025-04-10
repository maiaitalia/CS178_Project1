from Flask import Flask, render_template, request, redirect, url_for
import pymysql
import creds
from dbCode import *
import pymysql.cursors
import boto3

def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        passwor=creds.password,
        db=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, args=()):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
        return rows
    finally:
        conn.close()

app = Flask(__name__)

@app.route("/")
def index():
    movies = get_list_of_dictionaries()
    return render_template("index.html", results=movies)

