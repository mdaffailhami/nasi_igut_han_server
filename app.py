import os
import random
from flask import Flask, request, json, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import json_util
from bson.objectid import ObjectId
from flask_cors import CORS
from flask_mail import Mail, Message

load_dotenv()

app = Flask(
    __name__,
    static_url_path='/',
    template_folder='static'
)

# app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 2525
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

CORS(app)

cluster = MongoClient(os.getenv('DB_CONNECTION_URL'))
db = cluster['nasiIgutHanDB']

admins_collection = db['admins']
qnas_collection = db['qnas']
products_collection = db['products']
settings_collection = db['settings']


@app.route('/admins', methods=['GET'])
def find_one_admin():
    email = request.args.get('email')

    doc = admins_collection.find_one({'email': email})

    status = False if doc == None else True

    return {
        'status': status,
        'doc': json.loads(json_util.dumps(doc))
    }


@app.route('/admins', methods=['POST'])
def insert_one_admin():
    data = request.get_json()

    result = admins_collection.insert_one({
        'email': data['email'],
        'password': data['password'],
    })

    status = False if result.inserted_id == None else True

    return jsonify({'status': status, 'insertedID': str(result.inserted_id)})


@app.route('/admins', methods=['PATCH'])
def update_one_admin():
    email = request.args.get('email')
    data = request.get_json()

    result = admins_collection.update_one(
        {'email': email},
        {'$set': data}
    )

    status = False if result.modified_count == 0 else True

    return jsonify({'status': status})


@app.route('/qnas', methods=['GET'])
def find_qnas():
    docs = list(qnas_collection.find())

    status = False if len(docs) == 0 else True

    return jsonify({
        'status': status,
        'docs': json.loads(json_util.dumps(docs))
    })


@app.route('/qnas', methods=['POST'])
def insert_one_qna():
    data = request.get_json()

    result = qnas_collection.insert_one({
        'question': data['question'],
        'answer': data['answer'],
    })

    status = False if result.inserted_id == None else True

    return jsonify({'status': status, 'insertedID': str(result.inserted_id)})


@app.route('/qnas', methods=['PUT'])
def replace_one_qna():
    id = request.args.get('id')
    data = request.get_json()

    result = qnas_collection.replace_one(
        {'_id': ObjectId(id)},
        {
            'question': data['question'],
            'answer': data['answer'],
        }
    )

    status = False if result.modified_count == 0 else True

    return jsonify({'status': status})


@app.route('/qnas', methods=['DELETE'])
def delete_one_qna():
    id = request.args.get('id')

    result = qnas_collection.delete_one({'_id': ObjectId(id)})

    status = False if result.deleted_count == 0 else True

    return jsonify({'status': status})


@app.route('/products', methods=['GET'])
def find_products():
    docs = list(products_collection.find())

    status = False if len(docs) == 0 else True

    return jsonify({
        'status': status,
        'docs': json.loads(json_util.dumps(docs))
    })


@app.route('/products', methods=['POST'])
def insert_one_product():
    data = request.get_json()

    result = products_collection.insert_one({
        'name': data['name'],
        'description': data['description'],
        'price': data['price'],
        'image': data['image'],
    })

    status = False if result.inserted_id == None else True

    return jsonify({'status': status, 'insertedID': str(result.inserted_id)})


@app.route('/products', methods=['PUT'])
def replace_one_product():
    id = request.args.get('id')
    data = request.get_json()

    result = products_collection.replace_one(
        {'_id': ObjectId(id)},
        {
            'name': data['name'],
            'description': data['description'],
            'price': data['price'],
            'image': data['image'],
        }
    )

    status = False if result.modified_count == 0 else True

    return jsonify({'status': status})


@app.route('/products', methods=['DELETE'])
def delete_one_product():
    id = request.args.get('id')

    result = products_collection.delete_one({'_id': ObjectId(id)})

    status = False if result.deleted_count == 0 else True

    return jsonify({'status': status})


settings_id = ObjectId('6584db892b435f216e702dca')


@app.route('/settings', methods=['GET'])
def find_settings():
    doc = settings_collection.find_one({'_id': settings_id})

    status = False if doc == None else True

    return {
        'status': status,
        'doc': json.loads(json_util.dumps(doc))
    }


@app.route('/settings', methods=['PUT'])
def update_settings():
    data = request.get_json()

    result = settings_collection.replace_one(
        {'_id': settings_id}, data)

    status = False if result.modified_count == 0 else True

    return jsonify({'status': status})


@app.route('/contact-us', methods=['POST'])
def send_email():
    data = request.get_json()
    print(data)

    mail.send(Message(
        sender=os.getenv('MAIL_USERNAME'),
        recipients=[os.getenv('MAIL_USERNAME')],
        subject='Pesan dari Nasi Igut Han Web',
        body=f"Dari: {data['name']} ({data['email']})\nPesan: {data['message']}",
    ))

    return jsonify({'status': True})


@app.route('/reset-password', methods=['GET'])
def reset_password():
    verification_code = str(random.randint(100000, 999999))

    try:
        mail.send(Message(
            sender=os.getenv('MAIL_USERNAME'),
            recipients=[os.getenv('MAIL_USERNAME')],
            subject='Reset Password Nasi Igut Han',
            body=f'Kode verifikasi untuk reset password anda adalah {verification_code}',
        ))

        return jsonify({
            'status': True,
            'verificationCode': verification_code
        })
    except:
        return jsonify({'status': False})


@app.errorhandler(404)
def web_page(e):
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
