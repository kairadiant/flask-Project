import pymysql
from flask import Flask
from flask import Flask, render_template, request, redirect, url_for, session

logged_in = False
app = Flask(__name__)


def get_password():
    with open('password.txt', 'r') as file:
        return file.read().strip()


password = get_password()
user = "Kayla"


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/hello/<name>')
def hello_name(name):
    return 'Hello %s!' % name


@app.route('/login/', methods=['GET', 'POST'])
def login():
    global logged_in
    print(request)
    status = request.form['status']
    logn = request.form['login']
    pwd = request.form['password']
    query = f"SELECT COUNT(*) FROM {status} WHERE name = %s and id = %s"
    conn = pymysql.connect(host="localhost", user="root", passwd=get_password(), db="udb")
    cursor = conn.cursor()
    cursor.execute(query, (logn, pwd))
    rows = cursor.fetchall()
    if len(rows) > 0:
        logged_in = True
        # return f"Successfully logged in as {status} {logn}"
        query - f"SELECT DISTINCT table_name FROM v_udb_table_columns"
        headers, data = retrieve_data(query)
        tables = [row[0] for row in data]
        return render_template('Tables.html', tables=tables)
    else:
        return f"Could not login as {status} {logn}"


@app.route('/table/<table>')
def table(table):
    if logged_in:
        return show_tables_in_browser(table)


def show_tables_in_browser(table):
    query = f"SELECT * FROM {table}"
    headers, data = retrieve_data(query)
    return render_template('Results.html', headers=headers, data=data)


@app.route('/table/>')
def select_table():
    if logged_in:
        return show_tables_in_browser(table)


def retrieve_data(query):
    conn = pymysql.connect(host="localhost", user="root", passwd=password, db=query_db)
    cursor = conn.cursor()
    # query = f"SELECT * FROM {table}"
    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    data = [[str(col) for col in row] for row in rows]
    conn.close()
    return headers, data


if __name__ == '__main__':
    app.run()
