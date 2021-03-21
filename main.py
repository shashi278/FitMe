from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
import os
import json
from oauthlib.oauth2 import WebApplicationClient
import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
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

cat_data = None
current_user_email = ""

# google configurations
GOOGLE_CLIENT_ID = (
    "161589307268-m2b3kcts5njij3fjlf8g94bov125c833.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "tFsSYxOXbx6Qy5_dcSjI7rJl"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

email_verified= False
userinfo_response = json.dumps({})

client_google = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/loginGoogle")
def login_google():
    # takeout auth endpoint url from google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # construct the request uri
    request_uri = client_google.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callbackGoogle",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/loginGoogle/callbackGoogle")
def callbackGoogle():
    # Get authorization code Google sent back
    code = request.args.get("code")

    # Extract the URL to hit to get tokens
    # that allows to ask things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # prepare a request to get tokens
    token_url, headers, body = client_google.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )

    # send the request and get the response
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # parse the token response
    client_google.parse_request_body_response(json.dumps(token_response.json()))

    # Now we already have necessary tokens
    # lets ask Google for required informations
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client_google.add_token(userinfo_endpoint)

    # make the request and get the response
    global userinfo_response
    userinfo_response = requests.get(uri, headers=headers, data=body).json()

    # parse the information
    if userinfo_response.get("email_verified"):
        tmp = userinfo_response
        #print(tmp)
        """ return update_database(
            tmp["sub"], tmp["email"], tmp["picture"], tmp["given_name"]
        ) """
        with open("public/user_data.json", "r") as jf:
            try:
                user_data = json.load(jf)
                if user_data["user_detail"].get(tmp["email"]):
                    #don't send to quiz page. Has already taken quiz
                    global current_user_email
                    current_user_email = tmp["email"]
                    return render_template("profile.html", arg={"name": userinfo_response["given_name"], "image":userinfo_response["picture"]})
                else:
                    #otherwise save use info
                    new_data = {
                            "email": userinfo_response["email"],
                            "given_name": userinfo_response["given_name"],
                            "picture": userinfo_response["picture"]
                    }
                    user_data["user_detail"][userinfo_response["email"]] = new_data
                    #json.dump(new_data, jf, indent=4)
                    write_json(user_data)
                    #global current_user_email
                    current_user_email = userinfo_response["email"]
                    return render_template("quiz.html", arg={"name": userinfo_response["given_name"]})
            except json.decoder.JSONDecodeError:

            
                #otherwise save use info
                new_data = {
                        "email": userinfo_response["email"],
                        "given_name": userinfo_response["given_name"],
                        "picture": userinfo_response["picture"]
                }
                user_data["user_detail"][userinfo_response["email"]] = new_data
                #json.dump(new_data, jf, indent=4)
                write_json(user_data)
                #global current_user_email
                current_user_email = userinfo_response["email"]
                return render_template("quiz.html", arg={"name": userinfo_response["given_name"]})

        #return render_template("profile.html", arg={"name": userinfo_response["given_name"], "image":userinfo_response["picture"]})

    return "User Email not available or not verified"

def write_json(data, filename='public/user_data.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/quick_survey', methods=['POST'])
def login():
    return render_template("quiz.html")

@app.route('/recommendation', methods=['POST'])
def recommendation():
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
    #print("Category: {}".format(user_category))

    with open("public/user_data.json", "r") as jf:
        user_data = json.load(jf)
        
        user_data["user_detail"][current_user_email]["category"] = user_category
        write_json(user_data)
        
        


    return render_template("profile.html", arg={"name": user_data["user_detail"][current_user_email]["given_name"], "image":user_data["user_detail"][current_user_email]["picture"]})

@app.route("/home")
def home():
    with open("public/user_data.json", "r") as jf:
        user_data = json.load(jf)
        user_category = user_data["user_detail"][current_user_email]["category"]
    
    with open("public/categories.json", "r") as jf:
        categories = json.load(jf)
        #global cat_data
        if user_category < 5:
            cat_data = categories[str(user_category)]
        else:
            cat_data = categories["1"]
    return render_template("recommendations.html", cat_data=cat_data)

@app.route("/dashboard")
def dashboard():
    with open("public/user_data.json", "r") as jf:
        user_data = json.load(jf)
    return render_template("dashboard.html", arg={"name": user_data["user_detail"][current_user_email]["given_name"], "image":user_data["user_detail"][current_user_email]["picture"]})

@app.route("/activity")
def activity():
    with open("public/user_data.json", "r") as jf:
        user_data = json.load(jf)
    return render_template("activities.html", arg={"name": user_data["user_detail"][current_user_email]["given_name"], "image":user_data["user_detail"][current_user_email]["picture"]})

@app.route("/profile")
def profile():
    with open("public/user_data.json", "r") as jf:
        user_data = json.load(jf)
    return render_template("profile.html", arg={"name": user_data["user_detail"][current_user_email]["given_name"], "image":user_data["user_detail"][current_user_email]["picture"]})

@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True, port=8002)