from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'tmp/wordbase-images'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__, static_url_path='', 
            static_folder='public/assets',
            template_folder="public")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

category_map = {
    "active": {
        "1": [1,4],
        "2": [1,3,4],
        "3": [1,3,4],
        "4": [1,2,3,4],
        "5": [1,2,3,4]
    },

    "hobbies":{
        "1": [2],
        "2": [1],
        "3": [4],
        "4": [1,3],
        "5": [1,2,3,4,5],
        "6": [5]
    },

    "values":{
        "1": [1,4],
        "2": [2,3],
        "3": [1,2,3],
        "4": [3],
        "5": [1,3],
        "6": [1]
    },

    "active_hour":{
        "1": [1,2,3],
        "2": [4]
    },

    "cuisine":{
        "1": [5],
        "2": [1],
        "3": [5],
        "4": [2, 4]
    },

    "work_type":{
        "1": [1, 2, 4],
        "2": [1, 2, 3]
    },

    "working_hour":{
        "1": [1, 3],
        "2": [1, 2, 3,4],
        "3": [2,4]
    },
    
    "time_devote":{
        "1": [4],
        "2": [2, 3, 4],
        "3": [1,2,3,4,5],
        "4": [1,2,3,4,5],
        "5": [1,2,3,4,5]
    },

    "age_group":{
        "1": [2,3],
        "2":[2,3,4],
        "3":[1,3,4],
        "4":[1,3]
    }

}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/quick_survey', methods=['POST'])
def login():
    return render_template("quiz.html")

@app.route('/dashboard', methods=['POST'])
def dashboard():
    form = request.form
    category_vec = [0,0,0,0,0]

    active = form.get("active")
    for i in category_map.get("active")[active]:
        category_vec[i-1]+=1

    hobbies = form.getlist("hobbies")
    for each in hobbies:
        for i in category_map.get("hobbies")[each]:
            category_vec[i-1]+=1
    
    values = form.getlist("values")
    for each in values:
        for i in category_map.get("values")[each]:
            category_vec[i-1]+=1
    
    active_hour = form.get("active_hour")
    for i in category_map.get("active_hour")[active_hour]:
        category_vec[i-1]+=1
    
    cuisine = form.getlist("cuisine")
    for each in cuisine:
        for i in category_map.get("cuisine")[each]:
            category_vec[i-1]+=1
    
    work_type = form.get("work_type")
    for i in category_map.get("work_type")[work_type]:
        category_vec[i-1]+=1
    
    working_hour = form.get("working_hour")
    for i in category_map.get("working_hour")[working_hour]:
        category_vec[i-1]+=1
    
    time_devote = form.get("time_devote")
    for i in category_map.get("time_devote")[time_devote]:
        category_vec[i-1]+=1
    
    age_group = form.get("age_group")
    for i in category_map.get("age_group")[age_group]:
        category_vec[i-1]+=1

    user_category = category_vec.index(max(category_vec))+1
    print("Category: {}".format(user_category))
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True, port=8002)