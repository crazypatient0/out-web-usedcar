from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://localhost:27017/')
db = client['outwork']
collection = db['usrdata']

def create_table():
    if 'usrdata' not in db.list_collection_names():
        collection.insert_one({
            'username': 'admin',
            'password': 'admin'
        })

@app.route('/register', methods=['POST'])
def register():
    # 获取请求中的用户信息
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # 检查用户名是否已存在
    if collection.find_one({'email': email}):
        return jsonify({'code':203,'message': 'Email already exists'})

    # 创建新用户
    user = {
        'email': email,
        'username': username,
        'password': password
    }
    collection.insert_one(user)

    return jsonify({'code':200,'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    # 获取请求中的用户信息
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 检查用户是否存在
    user = collection.find_one({'email': email})
    if not user:
        return jsonify({'code':204,'message': 'User not found'})

    # 检查密码是否正确
    if user['password'] != password:
        return jsonify({'code':205,'message': 'Incorrect password'})

    return jsonify({'code':200,'message': 'Login successful'})


@app.route('/price-range', methods=['GET'])
def get_price_range():
    collection = db['usedcar']
    min_price = collection.find_one({}, sort=[('Price', 1)])['Price']
    max_price = collection.find_one({}, sort=[('Price', -1)])['Price']

    return jsonify({'min_price': min_price, 'max_price': max_price})


@app.route('/search', methods=['POST'])
def search():
    collection = db['usedcar']
    # 获取前端发送的 JSON 数据
    data = request.get_json()

    # 解析 JSON 数据中的搜索条件
    transmission = data.get('Transmission')
    price = data.get('price')
    fuel = data.get('Fuel')

    # 构建查询条件
    query = {}
    if transmission:
        query['Transmission'] = transmission
    if price:
        query['Price'] = {'$gt': price}
    if fuel:
        query['Fuel'] = {'$in': fuel}

    # 查询数据库
    if query:
        results = collection.find(query, {'_id': 0})
    else:
        results = collection.find({}, {'_id': 0})

    # 将查询结果转换为列表形式
    search_results = list(results)

    # 返回查询结果
    return jsonify({'results': search_results})


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
