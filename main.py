import json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from sqlalchemy.sql.expression import column
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from math import sin, cos, sqrt, atan2, radians
import bcrypt
import datetime
import operator

# -----------^IMPORTS^---------------

app = Flask(__name__)
app.secret_key = 'petsharepetsharepetsharepetsharepetsharepetsharepetshare'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# -------------^CONFIGS^-------------

db = SQLAlchemy(app)

class User(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Username = db.Column(db.String(20), nullable=False, unique=True)
    Password = db.Column(db.String(100), nullable=False)
    Mail = db.Column(db.String(100), nullable=False)
    Date_created = db.Column(db.DateTime, nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    Latitude = db.Column(db.Float, nullable=False, default=52.219926064186325)
    Longitude = db.Column(db.Float, nullable=False, default=21.00259908617123)
    
    def __repr__(self):
        return f"Item('{self.Id}', '{self.Username}')"

TYPES = ["Cats-Food", "Cats-Toys", "Cats-Other", "Dogs-Food", "Dogs-Toys", "Dogs-Other", "Other-Food", "Other-Toys", "Other-Other"]

class Item(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Title = db.Column(db.String(50),  nullable=False)
    Creator = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(1000), nullable=False)
    Price = db.Column(db.Integer, nullable=True, default=0)
    Mass = db.Column(db.Float, nullable=True)
    Delivery_type = db.Column(db.Integer, nullable=True)
    Latitude = db.Column(db.Float, nullable=False, default=52.219926064186325)
    Longitude = db.Column(db.Float, nullable=False, default=21.00259908617123)
    Date_created = db.Column(db.DateTime, nullable=False)
    Type = db.Column(db.String(20), nullable=False)
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
        return f"Message('{self.Id}', '{self.Message}')"

db.create_all()
db.session.commit()

# -----------------^DATABASE^-----------------------

def getIdByUsername(username):
    return User.query.filter_by(Username=username).first().Id

def getUsernameById(userid):
    return User.query.filter_by(Id=userid).first().Username

def hashPassword(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verifyPassword(username, provided_password):
    stored_password = User.query.filter_by(Username=username).first()
    if not stored_password:
        return False
    return bcrypt.checkpw(provided_password.encode(), stored_password.Password)

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
    return Item.query.order_by(Item.Id).filter_by(Receiver=user).all()

def calculateUserCategories(user):
    items = getReceivedHistory(user)
    multiplier = 10/float(len(items))
    iterator = 1
    animals = {"Cats": 0, "Dogs": 0, "Other": 0}
    item_types = {"Toys": 0, "Food": 0, "Other": 0}
    for item in items:
        splititems = item.Type.split("-")
        animal = splititems[0]
        item_type = splititems[1]
        if(animal in animals):
            animals[animal] += multiplier * iterator
        if(item_type in item_types):
            item_types[item_type] += multiplier * iterator
        iterator += 1
    return sorted(animals.items(), key=lambda x:x[1], reverse=True)[0][0], sorted(item_types.items(), key=lambda x:x[1], reverse=True)[0][0]

#print(calculateUserCategories("1"))

# -----------------^Newsletter^-----------------------

def addItem(title, description, longitude, latitude, creator, itemtype="Other-Other"):
    item = Item(Title=title, Description=description, Longitude=longitude, Latitude=latitude, Date_created=datetime.datetime.now(), Type=itemtype, Creator=creator)
    db.session.add(item)
    db.session.commit()
    return item

def addPurchase(item, receiver):
    pass

def populateItems():
    item1 = Item(Title="Stanislaw Howard", Description="Stanislaw Howard mata srata", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item1)
    item2 = Item(Title="mata srata", Description="Stanislaw Howard", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item2)
    item3 = Item(Title="sh", Description="sh", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item3)
    db.session.commit()

# -----------------^Items^-----------------------

def searchForItem(text):
    return list({*Item.query.filter(Item.Title.contains(text)).all(), *Item.query.filter(Item.Description.contains(text)).all()})

def orderByPrice(x):
    return sorted(x, key=operator.attrgetter('Price'))

def orderByType(x):
    return sorted(x, key=operator.attrgetter('Type'))

def orderByDateAdded(x):
    return sorted(x, key=operator.attrgetter('Date_created'))

def orderByExpiryDate(x):
    return sorted(x, key=operator.attrgetter('Expiry_date'))

# -----------------^Item filtering^-----------------------

##### Homepage #####

@app.route('/')
def main():
    #populateItems()
    print(orderByPrice(searchForItem("sh")))
    #print(createAccount("howiepolska", "pomarancza1", "j.trzyq@gmail.com", "+31651444094"))
    #print(verifyPassword("howiepolska", "pomarancza1"))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username and password:
        if verifyPassword(username, password):
            id = getIdByUsername(username)
            session['user_id'] = id
            return {
                'username': username,
                'user_id': id,
                'status': 'ok',
            }
        else:
            return {
                'status': 'fail',
                'msg': 'wrong password'
            }
    return {
        'status': 'fail',
        'msg': 'invalid request schema'
    }

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return {
        'status': 'ok'
    }

@app.route('/register', methods=['POST'])
def register():
    pass

# -------^ROUTES^-------

if __name__ == '__main__':
    app.run(debug=True)