from flask import Flask, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile("config.cfg")

""" Local DB """
app.config["MONGO_URI"] = "mongodb://localhost:27017/DataBaza"
mongodb_client = PyMongo(app)
db = mongodb_client.db


def register(email, password):
    if not (email and password):
        return jsonify("Please enter email and password"), 400
    current_user = db.Users.find_one({"email": email})
    if current_user:
        return jsonify("This email already in DB"), 400
    else:
        hashed_password = generate_password_hash(password)
        db.Users.insert({"email": email,
                         "password": hashed_password,
                         "confirmed": False,
                         "cvs": []})
    return True


def login_check(email_rq, password_rq):
    if not (email_rq and password_rq):
        return jsonify("Please enter email and password"), 400
    current_user = db.Users.find_one({"email": email_rq})
    if not current_user:
        return jsonify("No user in DB"), 400
    elif not current_user["confirmed"]:
        return jsonify("User account is not confirmed"), 400
    else:
        if not check_password_hash(current_user["password"], password_rq):
            return jsonify("Check the password and try again"), 400
    return jsonify("Login success"), 200


def getall():
    list = [i for i in db.Users.find()]
    return f"Got users: {list}"


def delete_user(email_del):
    current_user = db.Users.find_one({"email": email_del})
    if not current_user:
        return jsonify("No user in DB"), 400
    db.Users.delete_one(current_user)
    resp = jsonify("Deleted user: '" + current_user["email"] + "'")
    resp.status_code = 200
    return resp


def delete_vacancy(vacancy_Id):
    current_vacancy = db.Vacancies.find_one({"vacancy_Id": vacancy_Id})
    if not current_vacancy:
        return jsonify("No vacancy in DB"), 400
    db.Vacancies.delete_one(current_vacancy)
    # resp = jsonify("Deleted vacancy: '" + current_vacancy["vacancy_Id"] + "'"), 200
    resp = jsonify(f"Deleted vacancy: {vacancy_Id}"), 200
    return resp


def mess(text):
    return f"<h3>{text}</h3>"