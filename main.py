import json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_restful import Resource, Api

# -----------^IMPORTS^---------------

app = Flask(__name__)
app.secret_key = 'petsharepetsharepetsharepetsharepetsharepetsharepetshare'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# -------------^CONFIGS^-------------

db = SQLAlchemy(app)

class Item(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Item('{self.Id}', '{self.Name}')"

class User(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(20), nullable=False)
    Password = db.Column(db.String(100), nullable=False)

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