from flask_restful import Resource, Api
from app import app
from models import db , Subject

api = Api(app)

class Subject_r(Resource):
    def get(self):
        subjects = Subject.query.all()
        return {'subjects': [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]}
    
api.add_resource(Subject_r, '/api/subject')
