from FlaskMetrics import FlaskMetrics
from flask import Flask, render_template, send_from_directory,send_file,request,redirect,jsonify, url_for
from utils import encode_dict, is_endpoint_valid
from internal_database import internal_database
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin, current_user
from random import choices
from flask_dance.contrib.github import make_github_blueprint,github
from constants import *

from flask_ipban import IpBan

# csrf protection
from flask_wtf.csrf import CSRFProtect

#init flask app
app = Flask(__name__)

csrf = CSRFProtect(app)



# excessive crawl protection

ip_ban = IpBan(ban_seconds=3600*24*7) #one week ban
ip_ban.init_app(app)


# sessions and login manager stuff

login_manager = LoginManager()

login_manager.init_app(app)


app.secret_key = "".join(choices("1234567890°+AZERTYUIOP¨£µQSDFGHJKLM%WXCVBN?./§<>azertyuiopqsdfghjklmwxcvbn",k=1024))


from os import environ
environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'



github_blueprint = make_github_blueprint(
    client_id=GITHUB["client_id"],
    client_secret=GITHUB["client_secret"],
    redirect_url="/github_login",
    authorized_url="/authorized",
    scope=["email","profile"]
)



app.register_blueprint(github_blueprint, url_prefix="/github_login")

db = internal_database()

fm = FlaskMetrics(rows=["IP_ADDR","URL","REFERRER","CUSTOM_DATA"])
"""
db.register_user("test")
print(db.get_user_api_key(1))
db.add_endpoint(1)

"""

class User(UserMixin):
    
    
    def __init__(self, name="[anonymous]", id=0, active=True):
        self.name = name
        self.id = int(id)
        self.active = active


    def is_active(self):

        return self.active

    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
    
    def get_id(self):
        return self.id


@login_manager.user_loader
def user_loader(user_id):
    
    user = User(name=db.get_username(user_id),id=user_id)
    return user



        
        
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect("/github_login")











def bd(request):
    
    r = {}
    
    r["URL"] = request.path
    r["IP_ADDR"] = request.remote_addr
    r["REFERRER"] = request.referrer
    if request.headers.get("X-Referrer",default=False):
        r["REFERRER"] = request.get("X-Referrer",type=str)
        
    r["CUSTOM_DATA"] = encode_dict(request.args.to_dict())
        
    
    
    return r

fm.build_dict = bd

#home
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/hit/<endpoint>")
def endpoint(endpoint):
 
    
    if is_endpoint_valid(endpoint) and db.endpoint_exists(int(endpoint)):
        fm.store_visit(request)
        return jsonify({"OK":"Visit stored."})

    else:
        return jsonify({"Error":"Invalid endpoint."})


@app.route("/generate_endpoint",methods=["GET"])
@login_required
def generate_endpoint():
    
    request.args.to_dict()
    
    endpoint = db.add_endpoint(current_user.id)
    if endpoint:
        return jsonify({"new_endpoint":f"http://thaaoblues.pythonanywhere.com/hit/{endpoint}"})
    else: # user must have hit the endpoints number limit
        return jsonify({"Error":"You must have hit your endpoints number limit."})

@app.route("/endpoint_stats/<endpoint>")
def endpoint_stats(endpoint):
    
    if not is_endpoint_valid(endpoint):
        return jsonify({"Error":"Invalid endpoint."})
    
    api_key = request.args.get("api_key",default=False)
    
    if not api_key:
        return jsonify({"Error":"api_key argument not provided."})
    
    if not db.is_key_allowing_endpoint(api_key,endpoint):
        return jsonify({"Error":"You are not allowed to acces this endpoint stats."})

    
    return jsonify({"warning":"week visits count are just going back 7 days ago, not counting actual week.","stats":
        {"day_visits_count":fm.get_visits_count(url=f"/hit/{endpoint}"),
         "distinct_day_visits_count":fm.get_visits_count(url=f"/hit/{endpoint}",distinct=True),
         "week_vists_count":fm.get_visits_count(url=f"/hit/{endpoint}",days=7),
         "distinct_week_visits_count":fm.get_visits_count(url=f"/hit/{endpoint}",days=7,distinct=True),
         "month_vists_count":fm.get_month_visits_count(url=f"/hit/{endpoint}"),
         "distinct_month_visits_count":fm.get_month_visits_count(url=f"/hit/{endpoint}",distinct=True),
         "most_used_referrer":fm.get_most_used_referrer(url=f"/hit/{endpoint}")
         },"database":fm.get_database(distinct=False,url=f"/hit/{endpoint}")})


@app.route("/dashboard")
@login_required
def dashboard():
    
    eps = db.get_user_endpoints(current_user.id)
    
    for ele in eps:
        if not is_endpoint_valid(ele["endpoint_id"]):
            return jsonify({"Error":"Invalid endpoint."})
    
    return render_template("dashboard.html",endpoints=eps,username=current_user.name,api_key=db.get_user_api_key(current_user.id))



@app.route("/github_login")

def register():
    
    
    if not github.authorized:
        return redirect(url_for("github.login"))
    
    resp = github.get("/user").json()
    
    username = resp["login"]
    
    
    if not db.user_exists(username):
        #register the user
        user_id = db.register_user(username)

    else: # user exists
        
        user_id = db.get_user_id(username)
        
    # now that we are sure the user is registered, log him in
    
    user = User(name=username,id=user_id) 
    login_user(user,remember=True)
    return redirect("/dashboard")


@app.route("/rename_endpoint/<endpoint_id>")
@login_required
def rename_endpoint(endpoint_id):
    
    if (not is_endpoint_valid(endpoint_id)) or (not db.endpoint_exists(endpoint_id)):
        return jsonify({"Error":"Invalid endpoint."})

    if not request.args.get("new_name",default=False):
        return jsonify({"Error":"No new_name specified."})
    if not request.args.get("api_key",default=False):
        return jsonify({"Error":"No api_key specified."})
    
    if not db.is_key_allowing_endpoint(request.args.get("api_key"),endpoint_id):
        return jsonify({"Error":"This is not your endpoint."})
    
    db.rename_endpoint(request.args.get("new_name"),endpoint_id)
    
    return jsonify({"success":"Endpoint renamed."})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80,debug=True)