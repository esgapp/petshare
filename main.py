import json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from sqlalchemy.sql.expression import column
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
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
    Longitude = db.Column(db.Float, nullable=False)
    Latitude = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f"Item('{self.Id}', '{self.Username}')"

class Item(db.Model):
    Id = db.Column(db.Integer, primary_key=True, nullable=False)
    Title = db.Column(db.String(50),  nullable=False)
    Creator = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(1000), nullable=False)
    Price = db.Column(db.Integer, nullable=True, default=0)
    Mass = db.Column(db.Float, nullable=True)
    Delivery_type = db.Column(db.Integer, nullable=True)
    Longitude = db.Column(db.Float, nullable=False)
    Latitude = db.Column(db.Float, nullable=False)
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
        return f"User('{self.Id}', '{self.Message}')"

db.create_all()
db.session.commit()

# -----------------^DATABASE^-----------------------

def getIdByUsername(username):
    return User.query.filter_by(Username=username).first().Id

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

def populateItems():
    item1 = Item(Title="Stanislaw Howard", Description="Stanislaw Howard mata srata", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item1)
    item2 = Item(Title="mata srata", Description="Stanislaw Howard", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item2)
    item3 = Item(Title="sh", Description="sh", Longitude=0.67, Latitude=1.45, Date_created=datetime.datetime.now(), Type=1, Creator=1)
    db.session.add(item3)
    db.session.commit()

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