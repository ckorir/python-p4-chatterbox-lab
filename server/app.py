from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    if request.method == 'GET':
        dict_messages = []
        for message in messages:
            message_dict = message.to_dict()
            dict_messages.append(message_dict)
        response = make_response(dict_messages, 200)
        return response
    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            username=data.get('username'),
            body=data.get("body")
        )
        db.session.add(new_message)
        db.session.commit()
        dict_new_message = new_message.to_dict()
        response = make_response(dict_new_message, 201)
        return response


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response_body = {
            "error": "Message not found",
            "message": "No message found with the specified ID.",
        }
        response = make_response(response_body, 404)
        return response

    if request.method == 'PATCH':
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])
        db.session.commit()

        message_dict = message.to_dict()
        response = jsonify(message_dict)  # Use jsonify to return a JSON response
        response.status_code = 200
        return response

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message successfully deleted."
        }

        response = jsonify(response_body)  # Use jsonify to return a JSON response
        response.status_code = 200
        return response

if __name__ == '__main__':
    app.run(port=4000, debug=True)