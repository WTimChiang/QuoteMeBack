from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_email import amazon_send_email, send_email
from sqlalchemy.sql import func
from pathlib import Path
import glob

app = Flask(__name__)
# Replace sqlalchemy_database_uri as your own uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlalchemy_database_uri'
db = SQLAlchemy(app)                    

class Data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    email_ = db.Column(db.String(120))
    # height_ = db.Column(db.Integer)
    feeling_ = db.Column(db.String(120))

    def __init__(self, email_, feeling_):
        self.email_ = email_
        self.feeling_ = feeling_


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=['POST'])
def success():
    if request.method == "POST":
        email = request.form["email_name"]
        feeling = request.form["feeling_name"]
        feeling = feeling.lower()
        # check feeling is available
        available_feelings = glob.glob("quotes/*txt")
        available_feelings = [Path(filename).stem for filename in 
                            available_feelings]
        if feeling in available_feelings:
            data = Data(email, feeling)
            db.session.add(data)
            db.session.commit()

            happiness_count = db.session.query(Data).filter(Data.feeling_ == "happiness").count()
            anger_count = db.session.query(Data).filter(Data.feeling_ == "anger").count()
            sadness_count = db.session.query(Data).filter(Data.feeling_ == "sadness").count()
            motivation_count = db.session.query(Data).filter(Data.feeling_ == "motivation").count()
            amazon_send_email(email, feeling, happiness_count, anger_count, sadness_count, motivation_count)
            return render_template("success.html")
    return render_template("index.html", text="Please enter valid feeling")


if __name__ == '__main__':
    app.debug = True
    app.run()