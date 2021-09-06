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


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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
    def __init__(self, item_id, product_name, image, description, product_price):
        self.id = item_id
        self.product_name = product_name
        self.image = image
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
                 "image TEXT NOT NULL,"
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
        # if request.method == "POST":
        #     email = request.json["email"]
        #     password = request.json["password"]
        #
        #     with sqlite3.connect("furniture.db") as conn:
        #         conn.row_factory = dict_factory
        #         cursor = conn.cursor()
        #         cursor.execute("SELECT * FROM user WHERE email=? and password=?", (email, password))
        #         user = cursor.fetchone()
        #
        #         response['Status_code'] = 200
        #         response['data'] = user
        #         return response

        if request.method == "POST":
            username = request.json['first_name']
            last_name = request.json['last_name']
            phone_number = request.json['phone_number']
            email = request.json['email']
            password = request.json['password']

            with sqlite3.connect("furniture.db") as conn:
                conn.row_factory = dict_factory
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
                msg = Message('Hello ' + username, sender='lifeacademy146@gmail.com',
                              recipients=[email])
                msg.body = 'Thank you for registering with Checkers.'
                mail.send(msg)
            return response
    except SMTPRecipientsRefused:
        response["Message"] = "Invalid email used."
        response["Status_code"] = 400
        return response


@app.route('/login', methods=["PATCH"])
def login():
    response = {}
    # Login using patch method
    if request.method == "PATCH":
        email = request.json["email"]
        password = request.json["password"]

        with sqlite3.connect("furniture.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
            admin = cursor.fetchone()

        response['Message'] = "User loged in successfully"
        response['Status_code'] = 200
        response['data'] = admin
        return response
    else:
        if request.method != "PATCH":
            response['message'] = "Incorrect Method"
            response['status_code'] = 400
            return response


@app.route('/user-info/<int:user_id>', methods=["GET"])
def user_info(user_id):
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        conn.row_factory = dict_factory
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
            product_name = request.json['product_name']
            image = request.json['image']
            description = request.json['description']
            product_price = request.json['product_price']

            with sqlite3.connect("furniture.db") as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("INSERT INTO store("
                               "product_name,"
                               "image,"
                               "description,"
                               "product_price) VALUES(?, ?, ?, ?)",
                               (product_name, image, description, product_price))
                conn.commit()
                response["Message"] = "Product added successfully."
                response["Status_code"] = 201
                return jsonify(response)
    except Exception as e:
        return e


@app.route('/get-product/<int:item_id>', methods=["GET"])
def get_product(item_id):
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store WHERE item_id=" + str(item_id))

        response["Status_code"] = 200
        response["Description"] = "Item retrieved successfully."
        response["Data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/get-products/', methods=["GET"])
def get_products():
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store")

        response["Status_code"] = 200
        response["Description"] = "Items retrieved successfully"
        response["Data"] = cursor.fetchall()

    return jsonify(response)


@app.route('/update-products/<int:item_id>', methods=["PUT"])
def update_products(item_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('furniture.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("product_price") is not None:
                put_data["product_price"] = incoming_data.get("product_price")
                with sqlite3.connect('furniture.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE store SET product_price =? WHERE item_id=?",
                                   (put_data["product_price"], item_id))
                    conn.commit()
                    response['Message'] = "Product price updated"
                    response['Status_code'] = 200
    return response


@app.route('/remove-item/<int:item_id>', methods=["DELETE"])
def remove_item(item_id):
    response = {}
    with sqlite3.connect("furniture.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM store WHERE item_id=" + str(item_id))
        conn.commit()
        response['Status_code'] = 200
        response['Message'] = "Item removed successfully."
    return response


if __name__ == '__main__':
    app.run(debug=True)
