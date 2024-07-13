#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''


class CamperResource(Resource):
    def get(self, id):
        camper = db.session.get(Camper, id)
        if camper:
            return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age', 'signups.activity'))), 200)
        else:
            return make_response(jsonify(error="Camper not found"), 404)

    def patch(self, id):
        camper = db.session.get(Camper, id)
        if camper:
            data = request.get_json()
            try:
                if 'name' in data and not data['name']:
                    raise ValueError("Name must be provided")
                if 'name' in data:
                    camper.name = data['name']
                if 'age' in data:
                    camper.age = data['age']
                db.session.commit()
                return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age'))), 202)
            except Exception:
                return make_response(jsonify(errors=["validation errors"]), 400)
        else:
            return make_response(jsonify(error="Camper not found"), 404)


class CamperListResource(Resource):
    def get(self):
        campers = Camper.query.all()
        return make_response(jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers]), 200)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(name=data['name'], age=data['age'])
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict(only=('id', 'name', 'age'))), 201)
        except Exception:
            return make_response(jsonify(errors=["validation errors"]), 400)


class ActivityListResource(Resource):
    def get(self):
        activities = Activity.query.all()
        return make_response(jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities]), 200)


class ActivityResource(Resource):
    def delete(self, id):
        activity = db.session.get(Activity, id)
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response(jsonify({}), 204)
        else:
            return make_response(jsonify(error="Activity not found"), 404)


class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id=data['camper_id'],
                activity_id=data['activity_id'],
                time=data['time']
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(jsonify(new_signup.to_dict(only=('id', 'camper_id', 'activity_id', 'time', 'camper', 'activity'))), 201)
        except Exception:
            return make_response(jsonify(errors=["validation errors"]), 400)


api.add_resource(CamperListResource, '/campers')
api.add_resource(CamperResource, '/campers/<int:id>')
api.add_resource(ActivityListResource, '/activities')
api.add_resource(ActivityResource, '/activities/<int:id>')
api.add_resource(SignupResource, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
