from flask import Flask, render_template, request, redirect, url_for
from dbCode import execute_query, get_conn
import boto3

# initializing Flask app
app = Flask(__name__)


# connecting to DynamoDB for ratings
table_name = "movie_ratings"
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table(table_name)


# home
@app.route('/')
def home():
    genres = execute_query("SELECT genre_name FROM genre")
    return render_template('index.html', genres=genres)


# recommendations based on genre
@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form['genre']

    query = """
        SELECT DISTINCT m.title 
        FROM movie m 
        JOIN movie_genres mg ON m.movie_id = mg.movie_id 
        JOIN genre g ON mg.genre_id = g.genre_id 
        WHERE g.genre_name = %s
        ORDER BY m.popularity DESC
        LIMIT 5
    """
    recommendations = execute_query(query, (genre,))
    return render_template('recommendations.html', recommendations=recommendations, genre=genre)


# rating a movie
@app.route('/rate_movie', methods=['GET', 'POST'])
def rate_movie():
    if request.method == 'POST':
        user_id = request.form['user_id']
        movie_name = request.form['movie_name']
        rating = int(request.form['rating'])

        query = "SELECT movie_id FROM movie WHERE title = %s LIMIT 1"
        result = execute_query(query, (movie_name,))

        if not result:
            error_msg = f"Error: Movie '{movie_name}' not found."   # from ChatGPT
            return render_template('movie_ratings.html', error=error_msg)

        movie_id = result[0]['movie_id']

        try:
            table.put_item(Item={
                'movie_id': str(movie_id),
                'user_id': user_id,
                'rating': rating,
                'movie_name': movie_name
            })
            return render_template('adding_success.html')

        except Exception as e:
            error_msg = f"Error adding rating: {str(e)}"    # from ChatGPT
            return render_template('movie_ratings.html', error=error_msg)

    return render_template('movie_ratings.html')


# get all ratings that a user has stored
from boto3.dynamodb.conditions import Key   # from ChatGPT

@app.route('/user_ratings', methods=['GET', 'POST'])
def user_ratings():
    if request.method == 'POST':
        user_id = request.form['user_id']
        try:
            response = table.scan(
                FilterExpression=Key('user_id').eq(user_id)
            )
            ratings = response['Items']
            return render_template('user_ratings.html', user_id=user_id, ratings=ratings)
        except Exception as e:
            return f"Error retrieving ratings: {str(e)}", 500

    return render_template('user_ratings_form.html')


# delete a rating
@app.route('/delete_rating', methods=['GET', 'POST'])
def delete_rating():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        user_id = request.form['user_id']

        query = "SELECT movie_id FROM movie WHERE title = %s LIMIT 1"
        result = execute_query(query, (movie_name,))

        if not result:
            error_msg = f"Error: Movie '{movie_name}' not found in the database."
            return render_template('delete_rating.html', error=error_msg)

        movie_id = result[0]['movie_id']

        try:
            table.delete_item(
                Key={
                    'movie_id': str(movie_id),
                    'user_id': user_id
                }
            )
            return render_template('delete_success.html', movie_name=movie_name)
        except Exception as e:
            error_msg = f"Error deleting rating: {str(e)}"
            return render_template('delete_rating.html', error=error_msg)

    return render_template('delete_rating.html')


# update a rating
@app.route('/update_rating', methods=['GET', 'POST'])
def update_rating():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        user_id = request.form['user_id']
        new_rating = int(request.form['rating'])

        query = "SELECT movie_id FROM movie WHERE title = %s LIMIT 1"
        result = execute_query(query, (movie_name,))

        if not result:
            error_msg = f"Error: Movie '{movie_name}' not found in the database."
            return render_template('update_rating.html', error=error_msg)

        movie_id = result[0]['movie_id']

        try:
            table.update_item(
                Key={
                    'movie_id': str(movie_id),
                    'user_id': user_id
                },
                UpdateExpression="SET rating = :r",
                ExpressionAttributeValues={
                    ':r': new_rating
                }
            )
            return render_template('update_success.html', movie_name=movie_name, rating=new_rating)
        except Exception as e:
            error_msg = f"Error updating rating: {str(e)}"
            return render_template('update_rating.html', error=error_msg)

    return render_template('update_rating.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
