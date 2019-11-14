from flask import Flask
from flask_restful import Resource, Api, reqparse
import json

import nlp_module

app = Flask(__name__)
api = Api(app)

class GetAccuracy(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('ori_title', required=True, type=str, help='ori_title cannot be blank')
            parser.add_argument('searched_title', required=True, type=str, help='searched_title cannot be blank')
            args = parser.parse_args()

            json_dict = {
                "result": nlp_module.search_accsuracy_examine(args['ori_title'], args['searched_title'])
            }
            return json_dict
        except Exception as e:
            return {'error': str(e)}

class AlternativeTitle(Resource) :
    def get(self) :
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('title', required=True, type=str, help='title cannot be blank')
            args = parser.parse_args()

            json_dict = {
                "result": nlp_module.make_alterative_search_set(args['title'])
            }
            return json_dict
        except Exception as e:
            return {'error': str(e)}

api.add_resource(GetAccuracy, '/nlp/accuracy/title')
api.add_resource(AlternativeTitle, '/nlp/alternative')

if __name__ == "__main__" :
    app.run(host="0.0.0.0", port=80, debug=False)