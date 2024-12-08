from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(100), unique = False, nullable = False)
    password = db.Column(db.String(100), nullable = False)

    def to_dict(self):
        return {
            "id" : self.id,
            "username" : self.username,
            "password" : self.password
        }

# with app.app_context():
#     db.create_all()

@app.route("/users", methods = ["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error" : "Please enter username or password."}), 400

    existing_user = User.query.filter_by(username = username).first()
    if existing_user:
        return jsonify({"error" : "username already exists."}), 400

    # Create new user
    new_user = User(username = username, password = password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message" : "New user created", "user" : new_user.to_dict()}), 200

@app.route("/users", methods = ["GET"])
def get_users():
    all_users=  User.query.all()
    return jsonify([user.to_dict() for user in all_users]), 200

@app.route("/users/<int:user_id>", methods = ["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error" : "User not found."}), 404
    return jsonify(user.to_dict()), 200

@app.route("/users/<int:user_id>", methods = ["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error" : "User not found"}), 404

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Update only the required fields
    if username:
        # Check if username already exists
        existing_user = User.query.filter_by(username = username).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error" : "Username already exists."}), 400
        user.username = username
    if password:
        user.password = password

    db.session.commit()
    return jsonify({"message" : "User details updated", "user" : user.to_dict()}), 200

@app.route("/users/<int:user_id>", methods = ["DELETE"])
def detele_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error" : "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message" : "User Deleted"}), 200

if __name__ == "__main__":
    app.run(debug = True)