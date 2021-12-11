import json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from sqlalchemy.sql.expression import column
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from math import sin, cos, sqrt, atan2, radians
import bcrypt
import datetime

# -----------^IMPORTS^---------------

app = Flask(__name__)
app.secret_key = 'petsharepetsharepetsharepetsharepetsharepetsharepetshare'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# -------------^CONFIGS^-------------

db = SQLAlchemy(app)

class User(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Username = db.Column(db.String(20), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Mail = db.Column(db.String(100), nullable=False)
    Date_created = db.Column(db.DateTime, nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    Latitude = db.Column(db.Float, nullable=False, default=52.219926064186325)
    Longitude = db.Column(db.Float, nullable=False, default=21.00259908617123)
    
    def __repr__(self):
        return f"Item('{self.Id}', '{self.Username}')"

class Item(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Title = db.Column(db.String(50),  nullable=False)
    Creator = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(1000), nullable=False)
    Price = db.Column(db.Integer, nullable=True)
    Mass = db.Column(db.Float, nullable=True)
    Delivery_type = db.Column(db.Integer, nullable=True)
    Latitude = db.Column(db.Float, nullable=False, default=52.219926064186325)
    Longitude = db.Column(db.Float, nullable=False, default=21.00259908617123)
    Date_created = db.Column(db.DateTime, nullable=False)
    Type = db.Column(db.Integer, nullable=False)
    Expiry_date = db.Column(db.DateTime, nullable=True)
    Receiver = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Item('{self.Id}', '{self.Title}')"

class Message(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Sender = db.Column(db.Integer, nullable=False)
    Receiver = db.Column(db.Integer, nullable=False)
    Message = db.Column(db.String(1000), nullable=True)
    Date_created = db.Column(db.DateTime, nullable=False)
    Item = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.Id}', '{self.Message}')"

db.create_all()
db.session.commit()

# -----------------^DATABASE^-----------------------

def getIdByUsername(username):
    return User.query.filter_by(Username=username).first().Id

def hashPassword(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verifyPassword(username, provided_password):
    stored_password = User.query.filter_by(Username=username).first().Password
    return bcrypt.checkpw(provided_password.encode(), stored_password)

def createAccount(username, password, mail, phone):
    if(username in User.query.all().Username):
        return False
    date_created = datetime.datetime.now()
    password = hashPassword(password)
    user = User(Username = username, Password = password, Mail = mail, Date_created = date_created, Phone = phone)
    db.session.add(user)
    db.session.commit()
    return True


# -----------------^LOGIN^-----------------------

def calculateDistance(lat1, lon1, lat2, lon2):
    R = 6.3781 * 1e6
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c 

# -----------------^FUNCTIONS^-----------------------


def sendMessage(sender, receiver, message, item):
    date_created = datetime.datetime.now()
    message = Message(Sender=getIdByUsername(sender), Receiver=getIdByUsername(receiver), Message=message, Date_created=date_created, Item=item)
    db.session.add(message)
    db.session.commit()
    return True

def getItemMessages(item):
    return Message.query.filter_by(Item=item).all()


# -----------------^Messages^-----------------------

# Function that returns all items where a user provided resources
def getProvidedHistory(user):
    return Item.query.filter_by(Creator=getIdByUsername(user)).all()

# Function that returns all items where a user received resources
def getReceivedHistory(user):
    return Item.query.filter_by(Receiver=getIdByUsername(user)).all()

# -----------------^Newsletter^-----------------------

# def populateItems():
#     item1 = Item(Title="Stanislaw Howard", Description="Stanislaw Howard mata srata", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
#     db.session.add(item1)
#     item2 = Item(Title="mata srata", Description="Stanislaw Howard", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
#     db.session.add(item2)
#     item3 = Item(Title="sh", Description="sh", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
#     db.session.add(item3)
#     db.session.commit()

def searchForItem(text, order="e"):
    return list({*Item.query.filter(Item.Title.contains(text)).all(), *Item.query.filter(Item.Description.contains(text)).all()})

def orderByPriceDescending():
    return 

def orderByType():
    pass

def orderByDateAdded():
    pass

def orderByExpiryDate():
    pass

# -----------------^Item filtering^-----------------------

##### Homepage #####

@app.route('/')
def main():
    #populateItems()
    print(searchForItem("sh"))
    #print(createAccount("howiepolska", "pomarancza1", "j.trzyq@gmail.com", "+31651444094"))
    #print(verifyPassword("howiepolska", "pomarancza1"))


# -------^ROUTES^-------

if __name__ == '__main__':
    app.run(debug=True)