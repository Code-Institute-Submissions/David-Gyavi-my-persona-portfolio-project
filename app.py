import os
from flask import (
    Flask, flash,render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__) 


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)



@app.route("/")
@app.route("/get_fields")
def get_fields():
    fields = mongo.db.fields.find()
    return render_template("fields.html", fields=fields)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Checking if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})


        if existing_user:
            flash("Username already exists")     
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }     
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie  
        session["user"] = request.form.get("username").lower()
        flash("Registration Successfull!") 
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checking usernane if already exits in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})


        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
            else:
                # invalid password match
                 flash("Incorrect Username and/or Password")
                 return redirect(url_for("login")) 

        else:

                # username doesn't exits
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login")) 

    return render_template("login.html")



@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You were logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_contact", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        field = {
            "category_name": request.form.get("catecategory_name"),
            "field_name": request.form.get("field_name"),
            "due_date": request.form.get("due_date"),
            "field_description": request.form.get("field_description"),
        }
        mongo.db.fields.insert_one(field)
        flash("Field Successfully Added")
        return redirect(url_for("get_fields"))


    fields = mongo.db.fields.find().sort("field_name", 1)
    return render_template("add_contact.html", fields=fields)




if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
             port=int(os.environ.get("PORT")),
             debug=True)    