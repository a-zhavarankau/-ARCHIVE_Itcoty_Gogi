from datetime import datetime

from bson import ObjectId
from flask import Flask, request
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config.from_pyfile("config.cfg")

""" Local DB """
app.config["MONGO_URI"] = "mongodb://localhost:27017/DataBaza"
mongodb_client = PyMongo(app)
db = mongodb_client.db


def create_vacancy(**kwargs):
    # companyId = request.form["_id"]
    # current_user = db.Vacancy.find_one({"_id": ObjectId(companyId)})
    vacancy_Id = datetime.now().strftime("V_%Y-%m-%d_%H:%M:%S.%MS")
    vacancy = {
        "cv_id": vacancy_Id,
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
        "hard_skills": current_user["moreinfo"]["hard_skills"],
        "soft_skills": current_user["moreinfo"]["soft_skills"],
        "photo": current_user["moreinfo"]["photo"],
        "photo_new": request.json["photoNew"],
    }

    db.Vacancies.insert({"_id": ObjectId(vacancy_Id),
                         "set": set,
                         })


    resp = jsonify("CV created successfully")
    resp.status_code = 200
    return resp