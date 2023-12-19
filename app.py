import os
from flask import Flask, request, json, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util
from bson.objectid import ObjectId
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

cluster = MongoClient(os.getenv('DB_CONNECTION_URL'))
db = cluster['nasiIgutHanDB']

qnas_collection = db['qnas']
admins_collection = db['admins']


@app.route('/admins', methods=['GET'])
def find_one_admin():
    email = request.args.get('email')
    print(email)

    doc = admins_collection.find_one({'email': email})
    print(doc)

    status = False if doc == None else True

    return {
        'status': status,
        'doc': json.loads(json_util.dumps(doc))
    }


@app.route('/admins', methods=['POST'])
def insert_one_admin():
    data = request.get_json()
    print(data)

    result = admins_collection.insert_one({
        'email': data['email'],
        'password': data['password'],
    })

    print(result)

    status = False if result.inserted_id == None else True

    return jsonify({'status': status})


@app.route('/qnas', methods=['GET'])
def find_qnas():
    docs = list(qnas_collection.find())
    print(docs)

    status = False if len(docs) == 0 else True

    return jsonify({
        'status': status,
        'docs': json.loads(json_util.dumps(docs))
    })


@app.route('/qnas', methods=['POST'])
def insert_one_qna():
    data = request.get_json()
    print(data)

    result = qnas_collection.insert_one({
        'question': data['question'],
        'answer': data['answer'],
    })

    print(result)

    status = False if result.inserted_id == None else True

    return jsonify({'status': status})


@app.route('/qnas', methods=['PUT'])
def replace_one_qna():
    id = request.args.get('id')
    data = request.get_json()

    print(id)
    print(data)

    result = qnas_collection.replace_one(
        {'_id': ObjectId(id)},
        {
            'question': data['question'],
            'answer': data['answer'],
        }
    )

    print(result)

    status = False if result.modified_count == 0 else True

    return jsonify({'status': status})


if __name__ == '__main__':
    app.run(debug=True)
