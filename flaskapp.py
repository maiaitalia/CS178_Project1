def get_list_of_dictionaries():
    query = "SELECT * FROM movie LIMIT 10"
    return execute_query(query)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)