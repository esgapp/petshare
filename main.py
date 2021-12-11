import json
from flask import Flask, flash, request, jsonify, session, Response, render_template
from sqlalchemy.sql.expression import column
from flask_sqlalchemy import SQLAlchemy
from math import sin, cos, sqrt, atan2, radians
import bcrypt
import datetime
import operator
from sqlalchemy import and_, or_
from mail import *
from animal_model import *
from flask_cors import CORS
import hmac

# -----------^IMPORTS^---------------

app = Flask(__name__)
app.secret_key = 'petsharepetsharepetsharepetsharepetsharepetsharepetshare'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
CORS(app)

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
    Receiver = db.Column(db.Integer, nullable=True, default="NONE")

    def __repr__(self):
        return f"{self.Title},{self.Description},{self.Price}"

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

def createAccount(username, password, mail, phone, longitude=None, latitude=None):
    if User.query.filter_by(Username=username).first():
        return False
    date_created = datetime.datetime.now()
    password = hashPassword(password)
    user = User(Username = username, Password = password, Mail = mail, Date_created = date_created, Phone = phone, Longitude = longitude, Latitude = latitude)
    db.session.add(user)
    db.session.commit()
    return True

def getUserLocation(id):
    user = User.query.filter_by(Id=id).first()
    return user.Latitude, user.Longitude

def getUsername(id):
    user = User.query.filter_by(Id=id).first()
    return user.Username

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
    multiplier = 10/float(len(items)+1)
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
    return animals, item_types

#### Recommendations done, do the rest tommorow
def giveRecommendations(user):
    recommendations = []
    categories = calculateUserCategories(user)
    best_categories = sorted({a+"-"+b: x+y for a,x in categories[0].items() for b,y in categories[1].items()}.items(), key=lambda x:x[1], reverse=True)
    for key in best_categories:
        if(len(recommendations)>=3):
            return recommendations
        recommendations.extend(Item.query.filter(and_(Item.Receiver=="NONE", Item.Type==key[0])).all())
    return recommendations
    
def sendRecommendationEmails(user):
    recommendations = giveRecommendations(user)
    
    email = User.query.filter_by(Username=user).first().Mail
    title = "New product recommendations!"
    contents = f"We created these custom product recommendations based on your preferences:<br/>"
    for recommendation in recommendations:
        contents += f"""<a href="http://127.0.0.1:5000/share/{recommendation.Title}">{recommendation.Title} from the {recommendation.Type.replace("-", " and ")} category<br/></a>"""
    contents += "We hope these listings are of interest to you!"
    sendEmail(email, title, contents, user)
    return True

sendRecommendationEmails("Stanisław")

def sendOrganisationEmail(user, organisation):
    email = User.query.filter_by(Username=user).first().Mail
    title = "Check out this cool animal non-profit!"
    contents = """We would like to invite you to a livestream organised by """ + organisation + """. 
    We belive that the first step to decreasing the carbon footprint is to educate the society on this matter .
    By joining our webinar you will not only learn how to make use of old and used products but also get some insight 
    into as to how to reduce your own carbon footprint by changing little things. 
    
    <br><br><br> Be the change! <br>

    <br> <img src="https://images.pexels.com/photos/1072824/pexels-photo-1072824.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="" style="width: 300px; max-width: 600px; height: auto; margin: auto; display: block;">
    <br> <br> Join Us on a Zoom stream on 20 December 2021 
    <br> https://zoom.us/join?confno=8529015944&pwd=&uname=Nobody%20-%2051800000000
    """
    
    sendEmail(email, title, contents, user)
    return True
#print(sendRecommendationEmails("1"))

# -----------------^Newsletter^-----------------------

def addItem(title, description, longitude, latitude, creator, itemtype="Other-Other"):
    item = Item(Title=title, Description=description, Longitude=longitude, Latitude=latitude, Date_created=datetime.datetime.now(), Type=itemtype, Creator=creator)
    db.session.add(item)
    db.session.commit()
    return item

def addPurchase(item, receiver):
    Item.query.filter_by(Id=item).first().Receiver = receiver
    db.session.commit()
    return True

#print(addPurchase(3, "HOWIEBOWIE"))

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
    # return Item.query.filter(and_(or_(Item.Title.contains(text), Item.Description.contains(text)), Item.Receiver=="NONE")).all()
    return Item.query.all()

def searchForItemFlask(text):
    return Item.query.filter(and_(or_(Item.Title.contains(text), Item.Description.contains(text)), Item.Receiver=="NONE")).all()

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
    print(createAccount("howiepolska", "pomarancza1", "j.trzyq@gmail.com", "+31651444094"))
    return 0

@app.route('/share', defaults={'text': ''})
@app.route('/share/<string:text>')
def share(text):
    items = searchForItemFlask(text)
    items = [str(item).split(",") for item in items]
    return render_template("share.html", items=items, text=text)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if username and password:
        if verifyPassword(username, password):
            id = getIdByUsername(username)
            return jsonify({
                'username': username,
                'user_id': id,
                'status': 'ok',
                'session_key': hmac.new(app.secret_key.encode(), str(id).encode(), 'sha256').hexdigest(),
                'mail': User.query.filter_by(Id=id).first().Mail,
                'phone': User.query.filter_by(Id=id).first().Phone
            })
        else:
            return jsonify({
                'status': 'fail',
                'msg': 'wrong password'
            })
    return jsonify({
        'status': 'fail',
        'msg': 'incomplete request'
    })

# @app.route('/logout', methods=['POST'])
# def logout():
    # session.pop('user_id', None)
    # return jsonify({
        # 'status': 'ok'
    # })

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    mail = data['mail']
    phone = data['phone']
    longitude = data['longitude']
    latitude = data['latitude']
    if createAccount(username, password, mail, phone, longitude, latitude):
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'fail'}) 

@app.route('/listing/<int:id>', methods=['POST'])
def listing(id):
    r = Item.query.filterBy(Id=id).first()
    if not r:
        return jsonify({'status': 'fail'})
    return jsonify({
        'id': r.Id,
        'title': r.Title,
        'creator': getUsername(r.Creator),
        'description': r.Description,
        'price': r.Price,
        'mass': r.Mass,
        'delivery_type': r.Delivery_type,
        'latitude': r.Latitude,
        'longitude': r.Longitude,
        'distance': calculateDistance(user_lat, user_long, r.Latitude, r.Longitude) if user_lat is not None and user_long is not None else None,
        'date_created': r.Date_created,
        'type': r.Type,
        'expiry_date': r.Expiry_date,
        'receiver': r.Receiver,
        'status': 'ok'
    })

@app.route('/add_listing', methods=['POST'])
def add_listing():
    data = request.get_json()
    if 'user_id' not in data or 'session_key' not in data or\
            hmac.new(app.secret_key.encode(), str(data['user_id']).encode(), 'sha256').hexdigest() != data['session_key']:
        return jsonify({
            'status': 'fail',
            'msg': 'user not logged in '
        })
    required = ['title', 'description', 'price', 'delivery_type']
    user_id  = data['user_id']
    for req in required:
        if req not in data:
            return jsonify({
                'status': 'fail',
                'msg': f'{req} information missing'
                })
    latitude, longitude = getUserLocation(user_id)
    item = Item(
        Creator = user_id,
        Title = data['title'],
        Description = data['description'],
        Price = data['price'],
        Mass = data['mass'] if 'mass' in data else None,
        Delivery_type = int(data['delivery_type']),
        Latitude = latitude,
        Longitude = longitude,
        Type = data['type'] if 'type' in data else 'Other-Other',
        Date_created = datetime.datetime.now(),
        Expiry_date = datetime.date.fromisoformat(data['expiry_date']) if 'expiry_date' in data else None,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/listing/contact', methods=['POST'])
def contact():
    data = request.get_json()
    if 'item_id' not in data:
        return jsonify({
            'status': 'fail',
            'msg': 'no item id'
            })
    item_id = data['item_id']
    item = Item.query.filter_by(Id=item_id).first()
    if not item:
        return jsonify({
            'status': 'fail',
            'msg': 'no such item'
            })
    user = User.query.filter_by(Id=item.Creator).first()
    return jsonify({
        'status': 'ok',
        'mail': user.Mail,
        'phone': user.Phone
        })

@app.route('/listings', methods=["POST"])
def listings():
    data = request.get_json()
    user_long = data['user_long'] if 'user_long' in data else None
    user_lat = data['user_lat'] if 'user_lat' in data else None
    max_dist = data['max_dist'] if 'max_dist' in data else None
    sort_by = data['sort_by'] if 'sort_by' in data else None
    sort_order = data['sort_order'] if 'sort_order' in data else None
    key_word = data['key_word'] if 'key_word' in data else ''
    
    items = searchForItem(key_word)
    if user_long and user_lat and max_dist:
        items = [item for item in items if calculateDistance(user_lat, user_long, item.Latitude, item.Longitude) <= max_dist]
    sort_order = sort_order == "desc"
    if sort_order == "added":
        items = orderByDateAdded(items)
    elif sort_order == "expiry":
        items = orderByExpiryDate(items)
    elif sort_order == "price":
        items = orderByPrice(items)
    elif sort_order == "type":
        items = orderByType(items)
    if sort_by == "desc": items = reversed(items)
    res = [{"item" : {  
        'id': r.Id,
        'title': r.Title,
        'creator': getUsername(r.Creator),
        'description': r.Description,
        'price': r.Price,
        'mass': r.Mass,
        'delivery_type': r.Delivery_type,
        'latitude': r.Latitude,
        'longitude': r.Longitude,
        'distance': calculateDistance(user_lat, user_long, r.Latitude, r.Longitude) if user_lat is not None and user_long is not None else None,
        'date_created': r.Date_created,
        'type': r.Type,
        'expiry_date': r.Expiry_date,
        'receiver': int(r.Receiver) if r.Receiver != "NONE" else None
        }} for r in items]
    return jsonify({'status':'ok', 'items': res})

@app.route('/listing/react', methods=["POST"])
def react_to_listing():
    data = request.get_json()
    if 'user_id' not in data or 'session_key' not in data or\
            hmac.new(app.secret_key.encode(), str(data['user_id']).encode(), 'sha256').hexdigest() != data['session_key']:
        return jsonify({
            'status': 'fail',
            'msg': 'user not logged in '
        })
    user_id = data['user_id']
    if 'item_id' not in data:
        return jsonify({
            'status': 'fail',
            'msg': 'no item'
            })
    
    addPurchase(data['item_id'], user_id)

    item = Item.query.filter_by(Id=data['item_id']).first()
    user = User.query.filter_by(Id=item.Creator).first()
    user_receiver = User.query.filter_by(Id=user_id).first()

    sendEmail(user.Mail, 'Your item was reserved', f'Item {item.Title} was reserved by {getUsername(user_id)}', user.Username)
    sendEmail(user_receiver.Mail, 'You reserved an item', f'You reserved {item.Title} from {user.Username}', user_receiver.Username)

    return jsonify({'status': 'ok'})

@app.route('/send_message', methods=["POST"])
def send_message():
    data = request.get_json()
    if 'user_id' not in data or 'session_key' not in data or\
            hmac.new(app.secret_key.encode(), str(data['user_id']).encode(), 'sha256').hexdigest() != data['session_key']:
        return jsonify({
            'status': 'fail',
            'msg': 'user not logged in '
        })
    msg = Message(
        Sender = user_id,
        Receiver = data['receiver'] if 'receiver' in data else None,
        Message = data['message'] if 'message' in data else None,
        Date_created = datetime.datetime.now(),
        Item = data['item'] if 'item' in data else None,
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'status': 'ok'})

@app.route('/item_messages', methods=["POST"])
def item_messages():
    data = request.get_json()
    if 'item' not in data:
        return jsonify({'status': 'fail'})
    res = [{"message" : {  
        'id': r.Id,
        'sender': r.Sender,
        'receiver': r.Receiver,
        'message': r.Message,
        'date_created': r.Date_created
        }} for r in getItemMessages(data['item'])]
    return jsonify({'status': 'ok', 'messages': res})

# -------^ROUTES^-------

if __name__ == '__main__':
    app.run(debug=True)
