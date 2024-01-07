# Import required modules
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

#  Flask app
app = Flask(__name__)

#  MongoDB
app.config[
    "MONGO_URI"
] = "mongodb+srv://alpcivan858:c27nCi1qs38eEre0@cluster0.6ofoijn.mongodb.net/task4?retryWrites=true&w=majority"  # MODIFY THIS!!! You can use the link that I sent you separately
mongo = PyMongo(app)


#  user router
@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "GET":
        users = mongo.db.users.find()
        users = [user for user in users]
        for user in users:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return jsonify({"users": users})

    elif request.method == "POST":
        user = {"username": request.json["user"], "password": request.json["password"]}
        mongo.db.users.insert_one(user)
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return jsonify({"user": user})


#  user deletion router
@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    return jsonify({"message": "User deleted successfully!"})


#  admin router
@app.route("/admins", methods=["GET", "POST"])
def admins():
    if request.method == "GET":
        admins = mongo.db.admins.find()
        admins = [admin for admin in admins]
        for admin in admins:
            admin["_id"] = str(admin["_id"])  # Convert ObjectId to string
        return jsonify({"admins": admins})

    elif request.method == "POST":
        admin = {"username": request.json["user"], "password": request.json["password"]}
        mongo.db.admins.insert_one(admin)
        admin["_id"] = str(admin["_id"])  # Convert ObjectId to string
        return jsonify({"admin": admin})

    # comment router


@app.route("/comment", methods=["GET", "POST"])
def comment():
    if request.method == "GET":
        comments = mongo.db.comments.find()
        comments = [comment for comment in comments]
        for comment in comments:
            comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        return jsonify({"comments": comments})

    elif request.method == "POST":
        comment = {
            "content": request.json["content"],
            "username": request.json["username"],
        }
        mongo.db.comments.insert_one(comment)
        comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        return jsonify({"comment": comment})


# comment deletion router
@app.route("/comment/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    mongo.db.comments.delete_one({"_id": ObjectId(comment_id)})
    return jsonify({"message": "Comment deleted successfully!"})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
