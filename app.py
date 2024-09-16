# from inspect import CORO_SUSPENDED
import os
from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
# app.config["MONGO_URI"] = "mongodb://localhost:27017/stockdb"
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'ohwhodis@gmail.com'
# app.config['MAIL_PASSWORD'] = 'ksed mcag gnlx rodg'
# app.config['MAIL_DEFAULT_SENDER'] = 'ohwhodis@gmail.com'

mongo = PyMongo(app)
CORS(app)
mail = Mail(app)


@app.route("/")
def default():
    return render_template('index.html')

@app.route('/get_stock/<item>', methods=['GET'])
def get_stock(item):
    stock = mongo.db.stock.find_one({'item': item})
    if stock:
        return jsonify(stock['count'])
    return jsonify({'error': 'Item not found'}), 404

@app.route('/update_stock/<item>', methods=['POST'])
def update_stock(item):
    change = request.json.get('change')
    if change is None:
        return jsonify({'error': 'No change specified'}), 400
    stock = mongo.db.stock.find_one({'item': item})
    if stock:
        new_count = stock['count'] + change
        if new_count < 0:
            new_count = 0
        mongo.db.stock.update_one({'item': item}, {'$set': {'count': new_count}})
        if item == 'logitech-mk270' and new_count < 10:
            send_low_stock_email(item, new_count)
    else:
        if change < 0:
            return jsonify({'error': 'Cannot add new item with negative change'}), 400
        mongo.db.stock.insert_one({'item': item, 'count': change})
        new_count = change

    return jsonify({'count': new_count}), 200

def send_low_stock_email(item, count):
    msg = Message('Low stock alert', recipients=['kfir.zelnik@gmail.com'])
    msg.body = f'Item {item} is low on stock, current count is {count}'
    mail.send(msg)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5000, debug=True)
