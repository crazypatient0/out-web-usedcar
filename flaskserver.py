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
        query['Price'] = {'$lt': round((float(price)/1000),2)}
    if fuel:
        query['Fuel_Type'] = {'$in': fuel}

    # print(query)
    # 查询数据库
    if query:
        # print(1)
        results = collection.find(query, {'_id': 0})
    else:
        # print(2)
        results = collection.find({}, {'_id': 0})

    # 将查询结果转换为列表形式
    search_results = list(results)

    # print(type(search_results[0]))
    # 返回查询结果
    return jsonify({'results': search_results})


@app.route('/car/<int:id>', methods=['GET'])
def get_car(id):
    collection = db['usedcar']
    car = collection.find_one({"id": id}, {"_id": 0})  # Assuming 'cars' is the collection name
    # print(type(car),car)
    if car:
        # If it does, return it
        return jsonify({'code':200, 'data': car})
    else:
        # If it doesn't, return a 404 error
        return jsonify({'code':404, 'data':''})

@app.route('/car/<int:id>', methods=['PUT'])
def update_car(id):
    collection = db['usedcar']
    car = collection.find_one({"id": id})

    if car:
        price = request.json.get('Price', None)
        if price is not None:
            collection.update_one({"id": id}, {"$set": {"Price": price}})
            return jsonify({'code':200, 'message': 'Car price updated successfully.'})
    else:
        return jsonify({'code':404, 'message': 'Car not found.'})


@app.route('/car/<int:id>', methods=['DELETE'])
def delete_car(id):
    collection = db['usedcar']  # Assuming 'usedcar' is the collection name
    result = collection.delete_one({"id": id})

    if result.deleted_count > 0:
        return jsonify({"code": 200, "message": "Car deleted successfully."})
    else:
        return jsonify({"code": 404, "message": "Car not found."})


@app.route('/search2', methods=['POST'])
def search2():
    collection = db['usedcar']
    collection.create_index([('$**', 'text')], name='searchIndex')
    search_text = request.get_json()['searchText']
    query = {'$text': {'$search': search_text}}
    results = list(collection.find(query, {'_id': 0}))
    return jsonify({"code": 200, "data": results})

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
