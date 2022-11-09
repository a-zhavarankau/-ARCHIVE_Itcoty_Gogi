from json import dumps

from bson import ObjectId
from flask import Flask, request, url_for, jsonify
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from datetime import datetime
from user_functions import getall, register, login_check, delete_user, delete_vacancy
from pprint import pprint


app = Flask(__name__)
app.config.from_pyfile("config.cfg")

""" Local DB """
app.config["MONGO_URI"] = "mongodb://localhost:27017/DataBaza"
mongodb_client = PyMongo(app)
db = mongodb_client.db


""" ITCoty DataBase """
# app.config["MONGO_URI"] = "mongodb+srv://admin:192168011@cluster0.f8yiv.mongodb.net/ITCOTY?retryWrites=true&w=majority"
# mongodb_client = PyMongo(app)
# db = mongodb_client.db


mail = Mail(app)

srlzr = URLSafeTimedSerializer(app.config["SECRET_KEY"])


@app.route("/", methods=["GET", "POST"])     # Начальная страница с формой регистрации
def index():                                 # Ввод данных через браузер, без Postman
    if request.method == "GET":
        return '<h2>ITCOTY   Home page</h2>' \
               '<form action="/" method="POST"><label>email........</label><input name="email"><br>' \
               '<label>password..</label><input name="password"> <input type="submit"></form>'

    email = request.form['email']
    password = request.form['password']
    if register(email, password) != True:     #check if exists and registration in routes.py
        return register(email, password)

    token = srlzr.dumps(email, salt=app.config["SALT"])

    msg = Message("Registration at ITCOTY", sender=app.config["MAIL_USERNAME"], recipients=[email])

    link = url_for('confirm_email', token=token, _external=True)

    msg.body = f"Your account on ITCOTY was successfully created. Please click the link below to confirm " \
        f"your email address and activate your account:\n {link}"
    mail.send(msg)
    return jsonify("Confirmation letter was sent. Please check your mail."), 200


@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email = srlzr.loads(token, salt=app.config["SALT"], max_age=1200)
    except SignatureExpired:
        return f"Token expired already", 400

    prestime = datetime.now()
    db.Users.update_one({"email": email},
                        {"$set": {"confirmed": True}})

    resp = f"Token obtained successfully. User \"{email}\" has confirmed " \
        f"registration at {prestime}.", 200
    return resp


@app.route("/login", methods=["GET", "POST"])     # Начальная страница с формой регистрации
def login():                                      # Запуск через браузер, без Postman
    if request.method == "GET":
        return '<h2>ITCOTY   Login page</h2>' \
               '<form action="/login" method="POST"><label>email........</label><input name="email"><br>' \
               '<label>password..</label><input name="password"> <input type="submit"></form>'

    email_rq = request.form["email"]
    password_rq = request.form["password"]
    return login_check(email_rq, password_rq)


@app.route("/add_info", methods=["POST"])     # US03-01 Данные пользователя*
def user_info_by_Id():
    email_rq = request.json['email']
    current_user = db.Users.find_one({"email": email_rq})
    if not current_user["confirmed"]:
        return jsonify("User account is not confirmed"), 400
    user_info = {
        "lastname": request.json["lastName"],
        "realname": request.json["realName"],
        "penname": request.json["penName"],
        "photo": request.json["photo"],  # ===================
        "birthdate": request.json["birthDate"],
        "gender": request.json["gender"],
        "living": request.json["living"],
        "phones": request.json["phones"],
        "moreemails": request.json["moreEmails"],
        "links": request.json["links"],
        "hard_skills": request.json["hardSkills"],
        "soft_skills": request.json["softSkills"],
        "marks": request.json["marks"]}

    db.Users.find_one_and_update(
        current_user,
        {"$set": {"user_info": user_info}})

    resp = jsonify("User info added successfully")
    resp.status_code = 200
    return resp


@app.route("/update_info", methods=["POST"])
def update_info():
    email_rq = request.json['email']
    current_user = db.Users.find_one({"email": email_rq})
    new_info = request.json
    db.Users.update_one(current_user,
                        {"$set": {"user_info": new_info}})
    return jsonify("User info updated successfully"), 200


@app.route("/add_cv", methods=["POST"])     # US03-03.1 Создание резюме*
def add_cv_by_Id():
    current_user = db.Users.find_one({"email": request.json["email"]})
    cv_Id = datetime.now().strftime("CV_%Y-%m-%d_%H:%M:%S.%MS")
    cv = {
        "cv_id": cv_Id,
        "desired_position": request.json["dPosition"],
        "desired_salary_size": request.json["dSalarySize"],
        "desired_salary_min": request.json["dSalaryMin"],
        "desired_salary_currency": request.json["dSalaryCurrency"],
        "desired_salary_periodicity": request.json["dSalaryPeriodicity"],
        "desired_salary_taxation": request.json["dSalaryTaxation"],
        "desired_location": request.json["dLocation"],
        "about_me": request.json["aboutMe"],
        "ready_to_internship": request.json["readyToInternship"],
        "ready_to_startup": request.json["readyToStartup"],
        "company_activity": request.json["companyAct"],
        "company_type": request.json["companyType"],
        "cover_letter": request.json["coverLetter"],
        "hard_skills": current_user["user_info"]["hard_skills"],
        "soft_skills": current_user["user_info"]["soft_skills"],
        "photo": current_user["user_info"]["photo"],
        "photo_new": request.json["photoNew"],
    }
    db.Users.update(current_user,
                    {"$push": {"cvs": cv}})

    resp = jsonify("CV added successfully")
    resp.status_code = 200
    return resp


@app.route("/update_cv", methods=["POST"])
def update_the_cv():
    current_cv_id = request.json["cv_id"]
    current_user = db.Users.find_one({"cvs.cv_id": current_cv_id})
    new_cv = request.json
    try:
        new_cv.update({
            "hard_skills": current_user["user_info"]["hard_skills"],
            "soft_skills": current_user["user_info"]["soft_skills"],
            "photo": current_user["user_info"]["photo"]
        })
    except:
        new_cv.update({
            "hard_skills": None,
            "soft_skills": None,
            "photo": None
        })
    db.Users.update({"cvs.cv_id": current_cv_id},
                    {"$set": {"cvs.$": new_cv}})
    resp = jsonify("CV updated successfully"), 200
    return resp


@app.route("/getall", methods=["GET"])
def get_users():
    return getall()


@app.route("/delete", methods=["GET", "POST"])
def delete_by_email():
    if request.method == "GET":
        return '<h2>ITCOTY   Deleting page</h2>' \
               '<form action="/delete" method="POST"><label>email........</label><input name="email"> ' \
               '<input type="submit"></form>'
    email_del = request.form["email"]
    return delete_user(email_del)


@app.route("/create_vacancy", methods={"GET", "POST"})     # US03-05.3/1 Создать вакансию
def make_vacancy():
    vacancy_Id = datetime.now().strftime("VAC_%Y-%m-%d_%H:%M:%S.%MS")
    vacancy = ({
        "vacancy_Id": vacancy_Id,
        "about_company": request.json["aboutCompany"],
        "location_country": request.json["locationCountry"],
        "location_city": request.json["locationCity"],
        "position": request.json["position"],
        "qualification": request.json["qualification"],
        "wage": request.json["wage"],
        "employment_type": request.json["employmentType"],
        "schedule": request.json["schedule"],
        "about_vacancy": request.json["aboutVacancy"],
        "company_size": request.json["companySize"],
        "company_type": request.json["companyType"],
        "benefits": request.json["benefits"],
        "key_skills": request.json["keySkills"],
        })
    try:
        vacancy.update(
            {"location_state": request.json["locationState"]}
        )
    except:
        vacancy.update(
            {"location_state": None}
        )
    db.Vacancies.insert(vacancy)
    resp = jsonify("Vacancy created successfully")
    resp.status_code = 200
    return resp


@app.route("/update_vacancy", methods=["POST"])
def update_vacancy():
    vacancy_Id = request.json['vacancy_Id']
    current_vacancy = db.Vacancies.find_one({"vacancy_Id": vacancy_Id})
    new_vacancy = {"vacancy_Id": vacancy_Id}
    new_vacancy.update(request.json)
    try:
        new_vacancy.update(
            {"location_state": request.json["locationState"]}
        )
    except:
        new_vacancy.update(
            {"location_state": None}
        )
    db.Vacancies.replace_one(current_vacancy,
                             new_vacancy)
    return jsonify("Vacancy updated successfully"), 200


@app.route("/delete_vacancy", methods=["POST"])
def delete_by_vacancy_Id():
    vacancy_Id = request.json['vacancy_Id']
    print(vacancy_Id)
    return delete_vacancy(vacancy_Id)


@app.route("/g")
def g():
    req = request.data()
    return req

if __name__ == '__main__':
    app.run(debug=True)
