from flask import Flask
from flask_restful import Resource, Api, reqparse

import naver_book_searcher
import json_file

app = Flask(__name__)
api = Api(app)

nbs = naver_book_searcher.NaverBookSearcher()

class SearchBook(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('title', required=True, type=str, help='title cannot be blank')
            args = parser.parse_args()

            json_dict = {
                "result": json_file.book_to_json(nbs.from_title(args['title']))
            }
            return json_dict
        except Exception as e:
            return {'error': str(e)}

api.add_resource(SearchBook, '/booksearch')

if __name__ == '__main__':
    app.run('0.0.0.0', port=80)