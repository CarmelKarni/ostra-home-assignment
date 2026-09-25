from flask import Flask, request, jsonify
from models import db, User, Message
from repositories import SQLAlchemyUserRepository, SQLAlchemyMessageRepository
from handlers import UserHandler, MessageHandler
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_handler: UserHandler = None
message_handler: MessageHandler = None


def init_app():
    global user_handler, message_handler
    user_repo = SQLAlchemyUserRepository(db, User)
    user_handler = UserHandler(user_repo)
    message_repo = SQLAlchemyMessageRepository(db, Message)
    message_handler = MessageHandler(message_repo, user_repo)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    try:
        user = user_handler.create_user(data.get('name'), data.get('email'))
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users', methods=['GET'])
def get_users():
    users = user_handler.get_all_users()
    logger.debug(f"get_users: {users}")
    return jsonify(users), 200


@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = user_handler.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    try:
        updated_user = user_handler.update_user(user_id, data.get('name'), data.get('email'))
        if not updated_user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(updated_user), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        deleted = user_handler.delete_user(user_id)
        if not deleted:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<user_id>/messages/send', methods=['POST'])
def send_message(user_id):
    data = request.get_json()

    try:
        receiver_id = data.get('receiverId')
        message = data.get('message')
        result = message_handler.send_message(user_id, receiver_id, message)
        return jsonify(result), 201
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<user_id>/messages/fetch', methods=['GET'])
def fetch_messages(user_id):
    try:
        start_index = request.args.get('startIndex', default=0, type=int)
        end_index = request.args.get('endIndex', default=-1, type=int)
        result = message_handler.fetch_messages(user_id, start_index, end_index, False)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<user_id>/messages/unread', methods=['GET'])
def fetch_unread_messages(user_id):
    result = message_handler.fetch_messages(user_id, 0, -1, True)
    return jsonify(result), 200


@app.route('/users/<user_id>/messages/<int:message_id>', methods=['DELETE'])
def delete_message(user_id, message_id):
    result = message_handler.delete_message(user_id, message_id)
    return jsonify(result), 200


@app.route('/users/<user_id>/messages/delete-batch', methods=['DELETE'])
def delete_messages(user_id):
    data = request.get_json()

    try:
        message_ids = data.get('messageIds')
        deleted_count = message_handler.delete_messages(user_id, message_ids)
        return jsonify({'message': 'Messages deleted successfully', 'deletedCount': deleted_count}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<user_id>/messages/<int:message_id>/read-status', methods=['PATCH'])
def change_read_status(user_id, message_id):
    read_status = request.args.get('isRead', type=bool)
    result = message_handler.change_read_status(user_id, message_id, read_status)
    return jsonify(result), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_app()
    app.run(debug=True, port=5000)
