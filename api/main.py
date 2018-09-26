import os
from flask import Flask
from flask_restplus import Resource, Api

DEBUG = True if os.environ['PROD'] is not None else False

app = Flask(__name__)
api = Api(app)

@api.route('/')
class HelloWorld(Resource):
    def get(self):
        return {'title': 'Welcome to React'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=DEBUG)
