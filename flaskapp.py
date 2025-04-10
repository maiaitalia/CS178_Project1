from flask import Flask, render_template
from dbCode import execute_query

app = Flask(__name__)

def get_list_of_dictionaries():
    query = "SELECT * FROM movie LIMIT 10;"
    return execute_query(query)

@app.route("/")
def index():
    movies = get_list_of_dictionaries()
    return render_template("index.html", results=movies)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)