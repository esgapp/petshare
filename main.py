import json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from sqlalchemy.sql.expression import column
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

# -----------^IMPORTS^---------------

app = Flask(__name__)
app.secret_key = 'petsharepetsharepetsharepetsharepetsharepetsharepetshare'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# -------------^CONFIGS^-------------

db = SQLAlchemy(app)

class User(db.Model):
    User_id = db.Column(db.Integer, primary_key=True, nullable=False)
    Username = db.Column(db.String(20), nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Mail = db.Column(db.String(100), nullable=False)
    Date_created = db.Column(db.DateTime, nullable=False)
    Phone = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"Item('{self.Id}', '{self.Name}')"

class Item(db.Model):
    Item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    Title = db.Column(db.String(50),  nullable=False)
    Creator = db.Column(db.Integer, nullable=False)
    Description = db.Column(db.String(1000), nullable=False)
    Price = db.Column(db.Integer, nullable=True)
    Mass = db.Column(db.Float, nullable=True)
    Delivery_type = db.Column(db.Integer, nullable=False)
    Longitude = db.Column(db.Float, nullable=False)
    Latitude = db.Column(db.Float, nullable=False)
    Date_created = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"User('{self.Id}', '{self.Name}')"

db.create_all()

# -----------------^DATABASE^-----------------------


api = Api(app)
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

# -----------------^API^-----------------------

##### Homepage #####

# @app.route('/')
# def main():
#     print(1)
#     return 1


# -------^ROUTES^-------

if __name__ == '__main__':
    app.run(debug=True)