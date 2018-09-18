from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

#storage of all users for their current best chatbot use
userStorage =[]

#all methods of the api below
class User(Resource):
    def get(self, id):
        for user in userStorage:
            if(id == user["id"]):
                return user, 200
        return "User not found", 404

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument("currentBot")
        args = parser.parse_args()

        for user in userStorage:
            if(id == user["id"]):
                user["currentBot"] = args["currentBot"]
                return user, 200

        user = {
            "id": id,
            "currentBot": args["currentBot"]
        }
        userStorage.append(user)
        return user, 201

    def delete(self, id):
        global userStorage
        userStorage = [user for user in userStorage if user["id"] != id]
        return "{} is deleted.".format(id), 200

api.add_resource(User, "/user/<string:id>")

app.run(debug = True, port = 4000)
