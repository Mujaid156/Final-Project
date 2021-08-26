# Mujaid Kariem
# Class 2

# Importing Libraries
import hmac
import sqlite3
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused

# Start flask application
app = Flask(__name__)

CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lifeacademy146@gmail.com'
app.config['MAIL_PASSWORD'] = '08062021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

def fetch_users():
    with sqlite3.connect('furniture.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[1], data[4]))
        return new_data


def register_table():
    conn = sqlite3.connect('furniture.db')
    print("Database opened successfully.")

    conn.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "phone_number TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("User table created successfully.")
    conn.close()


class Store(object):
    def __init__(self, item_id, product_name, product_type, description, product_price):
        self.id = item_id
        self.product_name = product_name
        self.product_type = product_type
        self.description = description
        self.product_price = product_price


def fetch_products():
    with sqlite3.connect('furniture.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store")
        product = cursor.fetchall()

        new_data = []

        for data in product:
            new_data.append(Store(data[0], data[1], data[2], data[3], data[4]))
        return new_data


def product_table():
    conn = sqlite3.connect('furniture.db')
    print("Database opened successfully.")

    conn.execute("CREATE TABLE IF NOT EXISTS store(item_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_name TEXT NOT NULL,"
                 "product_type TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "product_price INTEGER NOT NULL)")
    print("Store table created successfully.")
    conn.close()


register_table()
product_table()

users = fetch_users()

user_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(first_name, password):
    user = user_table.get(first_name, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    id = payload['identity']
    return userid_table.get(id, None)


jwt = JWT(app, authenticate, identity)


@app.route('/')
def home():
    return 'Welcome to the home page.'


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    mail = Mail(app)
    response = {}

    try:
        if request.method == "POST":

            username = request.form['first_name']
            last_name = request.form['last_name']
            phone_number = request.form['phone_number']
            email = request.form['email']
            password = request.form['password']

            with sqlite3.connect("furniture.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "first_name,"
                               "last_name,"
                               "phone_number,"
                               "email,"
                               "password) VALUES(?, ?, ?, ?, ?)", (username, last_name, phone_number, email, password))
                conn.commit()
                response["Message"] = "User registered successfully."
                response["Status_code"] = 201
                msg = Message('Hello' + username, sender='lifeacademy146@gmail.com',
                              recipients=[email])
                msg.body = 'Thank you for registering with Checkers.'
                mail.send(msg)
            return response
    except SMTPRecipientsRefused:
        response["Message"] = "Invalid email used."
        response["Status_code"] = 400
        return response


@app.route('/user-info/<int:user_id>', methods=["GET"])
def user_info(user_id):
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id=" + str(user_id))

        response["Status_code"] = 200
        response["Description"] = "User information retrieved successfully."
        response["Data"] = cursor.fetchone()

    return jsonify(response)

@app.route('/products/', methods=["POST"])
def products():
    response = {}

    try:

        if request.method == "POST":
            product_name = request.form['product_name']
            product_type = request.form['product_type']
            description = request.form['description']
            product_price = request.form['product_price']

            with sqlite3.connect("furniture.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO store("
                               "product_name,"
                               "product_type,"
                               "description,"
                               "product_price) VALUES(?, ?, ?, ?)",
                               (product_name, product_type, description, product_price))
                conn.commit()
                response["Message"] = "Product added successfully."
                response["Status_code"] = 201
                return response
    except Exception as e:
        return e

@app.route('/get-product/<int:item_id>', methods=["GET"])
def get_product(item_id):
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store WHERE item_id=" + str(item_id))

        response["Status_code"] = 200
        response["Description"] = "Cart retrieved successfully."
        response["Data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
