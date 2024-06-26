import random
import string
from flask import Flask, url_for, render_template
from flask import request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import jwt
from sqlalchemy import or_, and_
from dateutil import parser
from dateutil.tz import tzutc
from flask import make_response


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"

# 前端请求接收
web_origin = "http://localhost:3000"

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers.set('Access-Control-Allow-Headers', 'Content-Type')
        resp.headers.set('Access-Control-Allow-Origin', web_origin)
        resp.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        resp.headers.set('Access-Control-Allow-Credentials', 'true')
        resp.headers.set('Access-Control-Max-Age', '86400')
        return resp

@app.after_request
def allow_cors(resp):
    resp.headers.set('Access-Control-Allow-Origin', web_origin)
    resp.headers.set('Access-Control-Allow-Credentials', 'true')
    return resp

# 渲染模板index.html
@app.route('/')
@app.route('/')
def index():
    movies = Movie.query.all()                  # 0：测试表
    user_logins = UserLogin.query.all()         # 1：用户登录表
    log_states = LogState.query.all()           # 2：登录状态表
    sellers = Seller.query.all()                # 3：农场主表
    buyers = Buyer.query.all()                  # 4：消费者表
    all_types = AllType.query.all()             # 5：动物品种表
    farms = Farm.query.all()                    # 6：土地表
    repos = Repo.query.all()                    # 7：仓库表
    product_batches = ProductBatch.query.all()  # 8：生产批次表
    repo_batches = RepoBatch.query.all()        # 9：仓储批次表
    products = Product.query.all()              # 10：商品表
    invoices = Invoice.query.all()              # 11：订单表
    messages = Message.query.all()              # 12：留言表
    
    return render_template('index.html',
                           movies=movies,
                           user_logins = user_logins,
                           log_states = log_states,
                           sellers = sellers,
                           buyers = buyers,
                           all_types = all_types,
                           farms = farms,
                           repos = repos,
                           product_batches = product_batches,
                           repo_batches = repo_batches,
                           products = products,
                           invoices = invoices,
                           messages = messages
                           )

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化扩展，传入程序实例 app
db = SQLAlchemy(app)

# 测试用例的表
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

# 1：用户登录表
class UserLogin(db.Model):
    """
    person_id       用户编号        int
    person_name     用户名          char
    person_pw       用户密码        char
    role_id         角色编号        int
    log_time        注册时间        datetime
    """
    __tablename__ = 'user_login'
    person_id = db.Column(db.Integer, primary_key = True)
    person_name = db.Column(db.String(50), nullable = False)
    person_pw = db.Column(db.String(50), nullable = False)
    role_id = db.Column(db.Integer, nullable = False)
    log_time = db.Column(db.DateTime, nullable = False) # the same as datatime in python

# 2：登录状态表
class LogState(db.Model):
    """
    log_id          登录编号        int
    person_id       用户编号        char
    log_token       登录状态        char
    """
    __tablename__ = 'log_state'
    log_id = db.Column(db.Integer, primary_key = True)
    person_id = db.Column(db.Integer, ForeignKey('user_login.person_id'))
    user_login = db.relationship('UserLogin')
    log_token = db.Column(db.Integer)

# 3：农场主表
class Seller(db.Model):
    """
    seller_id       农场主编号      int
    seller_name     农场主姓名      char
    seller_sex      农场主性别      char
    seller_age      农场主年龄      int
    seller_phone    农场主电话      char
    seller_address  农场主地址      char
    person_id       用户编号        int     通过user_login连接
    """
    __tablename__ = 'seller'
    seller_id = db.Column(db.Integer, primary_key = True)
    seller_name = db.Column(db.String(50))
    seller_sex = db.Column(db.String(2))
    seller_age = db.Column(db.Integer)
    seller_phone = db.Column(db.String(11))
    seller_address = db.Column(db.String(50))
    person_id = db.Column(db.Integer, ForeignKey('user_login.person_id'))
    user_login = db.relationship('UserLogin')

# 4：消费者表
class Buyer(db.Model):
    """
    buyer_id        消费者编号      int
    buyer_name      消费者姓名      char
    buyer_sex       消费者性别      char
    buyer_age       消费者年龄      int
    buyer_phone     消费者电话      char
    buyer_address   消费者地址      char
    person_id       用户编号        int     通过user_login连接
    """
    __tablename__ = 'buyer'
    buyer_id = db.Column(db.Integer, primary_key = True)
    buyer_name = db.Column(db.String(50))
    buyer_sex = db.Column(db.String(2))
    buyer_age = db.Column(db.Integer)
    buyer_phone = db.Column(db.String(11))
    buyer_address = db.Column(db.String(50))
    person_id = db.Column(db.Integer, ForeignKey('user_login.person_id'))
    user_login = db.relationship('UserLogin')

# 5：动植物品种表
class AllType(db.Model):
    """
    type_id         动植物品种编号      int
    type_name       动植物品种名称      char
    type_period     动植物生长周期      int     单位是天
    type_info       动植物品种描述      char
    type_judge      动物/植物判定       int     0是动物 1是植物
    """
    __tablename__ = 'all_type'
    type_id = db.Column(db.Integer, primary_key = True)
    type_name = db.Column(db.String(50))
    type_period = db.Column(db.Integer)
    type_info = db.Column(db.String(100))
    type_judge = db.Column(db.Integer)  # 0 for animals, 1 for plants

# 6：土地表
class Farm(db.Model):
    """
    farm_id         土地编号        int
    seller_id       农场主编号      int     通过seller连接
    farm_size       土地面积        float
    farm_type       土地类型        char    表明是渔场/牧场/农田等
    farm_name       土地名称        char
    """
    __tablename__ = 'farm'
    farm_id = db.Column(db.Integer, primary_key = True)
    seller_id = db.Column(db.Integer, ForeignKey('seller.seller_id'))
    seller = db.relationship('Seller')
    farm_size = db.Column(db.Float)
    farm_type = db.Column(db.String(50))
    farm_name = db.Column(db.String(50))

# 7：仓库表
class Repo(db.Model):
    """
    repo_id         仓库编号        int
    seller_id       农场主编号      int     通过seller连接
    repo_name       仓库名称        char
    repo_info       仓库环境        char    例如温度/湿度
    repo_maxsize    仓库最大容量    int     单位是立方米
    """
    __tablename__ = 'repo'
    repo_id = db.Column(db.Integer, primary_key = True)
    seller_id = db.Column(db.Integer, ForeignKey('seller.seller_id'))
    seller = db.relationship('Seller')
    repo_name = db.Column(db.String(50))
    repo_info = db.Column(db.String(50))
    repo_maxsize = db.Column(db.Integer)

# 8：生产批次表
class ProductBatch(db.Model):
    """
    batch_id        生产批次编号    int
    farm_id         生产土地编号    int     通过farm连接
    type_id         生产品种编号    int     通过all_type连接
    batch_num       生产数量        int     
    batch_start     生产开始时间    datetime
    batch_judge     生产状态        int     0是未成熟 1是成熟且未收获 2是已收货
    """
    __tablename__ = 'product_batch'
    batch_id = db.Column(db.Integer, primary_key = True)
    farm_id = db.Column(db.Integer, ForeignKey('farm.farm_id'))
    farm = db.relationship('Farm')
    type_id = db.Column(db.Integer, ForeignKey('all_type.type_id'))
    all_type = db.relationship('AllType')
    batch_num = db.Column(db.Integer)
    batch_start = db.Column(db.DateTime)
    batch_judge = db.Column(db.Integer)

# 9：仓储批次表
class RepoBatch(db.Model):
    """
    batchrepo_id        仓储批次编号    int
    repo_id             仓库编号        int     通过repo连接
    batchrepo_start     批次入库时间    datetime
    product_id          商品编号        int     通过product连接
    batchrepo_period    产品保质期      int
    batchrepo_size      入库体积        int
    batchrepo_num       入库数量        int
    batchrepo_left      库存数量        int
    batchrepo_on        是否上架        int     0是未上架 1是已上架
    batchrepo_expire    是否过期        int     0是未过期 1是已过期
    """
    __tablename__ = 'repo_batch'
    batchrepo_id = db.Column(db.Integer, primary_key = True)
    repo_id = db.Column(db.Integer, ForeignKey('repo.repo_id'))
    repo = db.relationship('Repo')
    batchrepo_start = db.Column(db.DateTime)
    product_id = db.Column(db.Integer, ForeignKey('product.product_id'))
    product = db.relationship('Product')
    batchrepo_period = db.Column(db.Integer)
    batchrepo_size = db.Column(db.Integer)
    batchrepo_num = db.Column(db.Integer)
    batchrepo_left = db.Column(db.Integer)
    batchrepo_on = db.Column(db.Integer)
    batchrepo_expire = db.Column(db.Integer)

# 10：商品表
class Product(db.Model):
    """
    product_id      商品编号        int
    seller_id       农场主编号      int     通过seller连接
    product_name    商品名称        char
    product_type    商品类型        int     1是水果 2是蔬菜 3是奶制品 4是肉制品 等
    product_price   商品价格        float
    product_num     商品设置的库存  int
    product_info    商品其他信息    char
    """
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key = True)
    seller_id = db.Column(db.Integer, ForeignKey('seller.seller_id'))
    seller = db.relationship('Seller')
    product_name = db.Column(db.String(50))
    product_type = db.Column(db.Integer)
    product_price = db.Column(db.Float)
    product_num = db.Column(db.Integer)
    product_info = db.Column(db.String(100))
    
# 11：订单表
class Invoice(db.Model):
    """
    invoice_id      订单编号        int
    product_id      商品编号        int     通过product连接
    buyer_id        消费者编号      int     通过buyer连接
    invoice_num     购买数量        int     
    invoice_money   订单金额        float
    invoice_time    下单时间        datetime
    invoice_out     发货状态        int     0是未发货 1是已发货
    """
    __tablename__ = 'invoice'
    invoice_id = db.Column(db.Integer, primary_key = True)
    product_id = db.Column(db.Integer, ForeignKey('product.product_id'))
    product = db.relationship('Product')
    buyer_id = db.Column(db.Integer, ForeignKey('buyer.buyer_id'))
    buyer = db.relationship('Buyer')
    invoice_num = db.Column(db.Integer)
    invoice_money = db.Column(db.Float)
    invoice_time = db.Column(db.DateTime)
    invoice_out = db.Column(db.Integer)
    
# 12：留言表
class Message(db.Model):
    """
    message_id      留言标号        int
    person_id       用户编号        int
    message_info    留言内容        char
    message_time    留言时间        datetime
    """
    message_id = db.Column(db.Integer, primary_key = True)
    person_id = db.Column(db.Integer, ForeignKey('user_login.person_id'))
    person = db.relationship('UserLogin')
    message_info = db.Column(db.String(200))
    message_time = db.Column(db.DateTime)

# flask shell, can log into >>> mode
# 测试用例
"""
from app import UserLogin
user = UserLogin(person_name = 'xwk', person_pw = 'xwk', role_id = '1', log_time = datetime(2023, 10, 23))  
db.session.add(user)
db.session.commit()
"""
# 初始化database
"""
db.drop_all()
db.create_all()
quit()
"""

##############################用户注册##############################

# jwt--id+time  暂存的jwt_token
def generate_jwt_token(user):
    payload = {
        'person_id': user.person_id,
        'exp': datetime.utcnow() + timedelta(hours=3)  # Token 3小时后过期
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def generate_log_token(length=50):#random
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['person_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/register', methods=['POST'])
def register():
    """
    input json：
    {
        person_name:
        person_pw:
        role_id:
        
        name:
    }
    """
    data = request.get_json()
    
    # 用户表信息
    person_name = data.get('person_name')
    person_pw = data.get('person_pw')
    role_id = data.get('role_id')

    # 验证用户输入的信息
    if UserLogin.query.filter_by(person_name=person_name).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if role_id != 0 and role_id != 1:
        return jsonify({'error': '用户角色输入错误'}), 400
    
    # 用户表插入
    new_user = UserLogin(
        person_name = person_name,
        person_pw = person_pw,
        role_id = role_id,
        log_time = datetime.now()
    )
    db.session.add(new_user)
    db.session.commit()
    
    # 农场主表插入
    person_id = new_user.person_id
    if role_id == 0:
        new_seller = Seller(
            seller_name = person_name,
            person_id = person_id
        )
        db.session.add(new_seller)
        db.session.commit()
    # 用户表插入
    else:
        new_buyer = Buyer(
            buyer_name = person_name,
            person_id = person_id
        )
        db.session.add(new_buyer)
        db.session.commit()
    
    # 生成 JWT token
    jwt_token = generate_jwt_token(new_user)
    
    # 用户登录表插入
    new_logstate = LogState(
        person_id = new_user.person_id,
        log_token = jwt_token   # indicate that new_user have not log-in
    )
    db.session.add(new_logstate)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 200

###################用户登录##########################
@app.route('/login', methods=['POST'])
def login():
    """
    input json:
    {
        person_name:
        person_pw:
    }
    """
    # get json
    data = request.get_json()
    person_name = data.get('person_name')
    person_pw = data.get('person_pw')

    # 验证用户信息
    user = UserLogin.query.filter_by(person_name=person_name).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400

    if user.person_pw != person_pw:
        return jsonify({'error': '密码错误'}), 400

    # 查找登录状态
    log_state = LogState.query.filter_by(person_id=user.person_id).first()
    jwt_token = generate_jwt_token(user)
    if log_state:
        log_state.log_token = jwt_token
        db.session.commit()
        return jsonify({'message': '用户已登录，token已更新', 'log_token': jwt_token}), 200

    # 添加新的登录状态记录
    new_log_state = LogState(
        person_id=user.person_id,
        log_token=jwt_token
    )
    db.session.add(new_log_state)
    db.session.commit()

    return jsonify({'message': '登录成功', 'log_token': jwt_token}), 200

###################用户信息查询##########################
@app.route('/user_info', methods=['POST'])
def user_info():
    """
    input json:
    {
        person_id:    
    }
    
    output json:
    {
        person_id:
        role_id:
        
        seller:{
            seller_name:
            seller_sex:
            seller_age:
            seller_phone:
            seller_address:
        }
        
        buyer:{
            同理可得, 5个属性
        }
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 用户是农场主
    if user.role_id == 0:
        seller_info = Seller.query.filter_by(person_id=person_id).first()
        if not seller_info:
            return jsonify({'message': '农场主不存在'}), 400
        
        return jsonify({
            'person_id': person_id,
            'role_id': user.role_id,
            'seller': {
                'seller_name': seller_info.seller_name,
                'seller_sex': seller_info.seller_sex,
                'seller_age': seller_info.seller_age,
                'seller_phone': seller_info.seller_phone,
                'seller_address': seller_info.seller_address
            }
        }), 200
    # 用户是消费者
    elif user.role_id == 1:
        buyer_info = Buyer.query.filter_by(person_id=person_id).first()
        
        if not buyer_info:
            return jsonify({'message': '消费者不存在'}), 400
        return jsonify({
            'person_id': person_id,
            'role_id': user.role_id,
            'buyer': {
                'buyer_name': buyer_info.buyer_name,
                'buyer_sex': buyer_info.buyer_sex,
                'buyer_age': buyer_info.buyer_age,
                'buyer_phone': buyer_info.buyer_phone,
                'buyer_address': buyer_info.buyer_address
            }
        }), 200

######################用户信息修改#####################
@app.route('/update_user_info', methods=['POST'])
def update_user_info():
    """
    input json:
    {
        person_id:
        name:
        sex:
        age:
        phone:
        address:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # receive updated info
    name = data.get('name')
    sex = data.get('sex')
    age = data.get('age')
    phone = data.get('phone')
    address = data.get('address')
    
    # 用户是农场主
    if user.role_id == 0:
        cur_seller = Seller.query.filter_by(person_id=person_id).first()
        if cur_seller:
            if name:
                cur_seller.seller_name = name
            if sex:
                cur_seller.seller_sex = sex
            if age:
                cur_seller.seller_age = age
            if phone:
                cur_seller.seller_phone = phone
            if address:
                cur_seller.seller_address = address
                
            db.session.flush()
            db.session.commit()
            
            return jsonify({'message': '农场主信息更新成功'}), 200
        else:
            return jsonify({'error': '农场主不存在'}), 400
    # 用户是消费者
    elif user.role_id == 1:
        cur_buyer = Buyer.query.filter_by(person_id=person_id).first()
        if cur_buyer:
            if name:
                cur_buyer.buyer_name = name
            if sex:
                cur_buyer.buyer_sex = sex
            if age:
                cur_buyer.buyer_age = age
            if phone:
                cur_buyer.buyer_phone = phone
            if address:
                cur_buyer.buyer_address = address
                
            db.session.flush()
            db.session.commit()
            
            return jsonify({'message': '消费者信息更新成功'}), 200
        else:
            return jsonify({'error': '消费者不存在'}), 400

    return jsonify({'error': '未知错误'}), 400


##########################################土地表的操作###################################################
# 增加土地
@app.route('/add_farm', methods=['POST'])
def add_farm():
    """
    input json:
    {
        person_id:
        farm_size:
        farm_type:
        farm_name:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # receive info
    farm_size = data.get('farm_size')
    farm_type = data.get('farm_type')
    farm_name = data.get('farm_name')
    
    # check info
    if not farm_size or not farm_type or not farm_name:
        return jsonify({'error': '农场信息缺失'}), 400
    
    seller = Seller.query.filter_by(person_id = person_id).first()
    seller_id = seller.seller_id

    # 创建新的土地记录并添加到数据库
    new_farm = Farm(
        farm_size = farm_size,
        farm_type = farm_type,
        farm_name = farm_name,
        seller_id = seller_id
    )
    
    db.session.add(new_farm)
    db.session.commit()
    return jsonify({'message': '农田添加成功'}), 200

# 删除土地
@app.route('/delete_farm', methods=['POST'])
def delete_farm():
    """
    input json:
    {
        person_id:
        farm_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0: 
        return jsonify({'error': '用户不是农场主'}), 400
    
    # 获取删除土地id
    farm_id = data.get('farm_id')
    if not farm_id:
        return jsonify({'error': '缺少farm_id'}), 400

    farm_to_delete = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm_to_delete:
        return jsonify({'error': '该土地不存在'}), 404

    db.session.delete(farm_to_delete)
    db.session.commit()
    return jsonify({'message': '删除土地成功'}), 200

# 更新土地
@app.route('/update_farm', methods=['POST'])
def update_farm():
    """
    input json:
    {
        person_id:
        farm_id:
        farm_size:
        farm_type:
        farm_name:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # received data
    farm_id = data.get('farm_id')
    if not farm_id:
        return jsonify({'error': '缺少farm_id'}), 400

    new_farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not new_farm:
        return jsonify({'error': '该土地不存在'}), 404
    else:
        # receive data
        farm_size = data.get('farm_size')
        farm_type = data.get('farm_type')
        farm_name = data.get('farm_name')
        if farm_size:
            new_farm.farm_size = farm_size
        if farm_type:
            new_farm.farm_type = farm_type
        if farm_name:
            new_farm.farm_name = farm_name
        
        db.session.flush()
        db.session.commit()
        return jsonify({'message': '更新土地成功'}), 200

# 条件查询土地
@app.route('/query_farm', methods=['POST'])
def query_farm():
    """
    input json:
    {
        person_id:
        query_string:
    }
    
    output json:
    {
        farms:{
            'farm_id': farm.farm_id,
            'seller_id': farm.seller_id,
            'farm_size': farm.farm_size,
            'farm_type': farm.farm_type,
            'farm_name': farm.farm_name
        }
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    search_value = data.get('query_string')
    if not search_value:
        return jsonify({'error': '缺少查询条件'}), 400

    # 将查询值转为字符串以便于模糊查询
    search_value = str(search_value)

    # 使用or_操作符进行模糊查询
    farms = Farm.query.filter(
        or_(
            Farm.farm_size.like(f'%{search_value}%'),
            Farm.farm_type.like(f'%{search_value}%'),
            Farm.farm_name.like(f'%{search_value}%')
        )
    ).all()

    output = []
    for farm in farms:
        farm_data = {
            'farm_id': farm.farm_id,
            'seller_id': farm.seller_id,
            'farm_size': farm.farm_size,
            'farm_type': farm.farm_type,
            'farm_name': farm.farm_name
        }
        output.append(farm_data)

    return jsonify({'farms': output}), 200

# 查询所有土地
@app.route('/query_all_farms', methods=['POST'])
def query_all_farms():
    """
    input json:
    {
        person_id:
    }
    
    output json:
    {
        farms:{
            'farm_id': farm.farm_id,
            'seller_id': farm.seller_id,
            'farm_size': farm.farm_size,
            'farm_type': farm.farm_type,
            'farm_name': farm.farm_name
        }
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 当前用户是否为农场主
    seller = Seller.query.filter_by(person_id=person_id).first()
    if not seller:
        return jsonify({'error': '当前用户不是农场主'}), 400

    # 获取农场主的土地信息
    farms = Farm.query.filter_by(seller_id=seller.seller_id).all()
    output = []
    for farm in farms:
        farm_data = {
            'farm_id': farm.farm_id,
            'farm_size': farm.farm_size,
            'farm_type': farm.farm_type,
            'farm_name': farm.farm_name
        }
        output.append(farm_data)

    return jsonify({'farms': output}), 200

##########################################生产批次表的操作###################################################
# 增加生产批次
@app.route('/add_produce_batch', methods=['POST'])
def add_produce_batch():
    """
    input json:
    {
        person_id:
        
        farm_id:
        type_id:
        batch_num:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 获取用户输入的新增动植物信息
    farm_id = data.get('farm_id')
    type_id = data.get('type_id')
    batch_num = data.get('batch_num')
    
    if not farm_id or not type_id or not batch_num:
        return jsonify({'error': '批次信息不完整'})

    # 创建新的生产批次
    new_batch = ProductBatch(
        farm_id=farm_id,
        type_id=type_id,
        batch_num=batch_num,
        batch_start=datetime.now(),
        batch_judge=0
    )

    db.session.add(new_batch)
    db.session.commit()
    return jsonify({'message': '添加生产批次成功'}), 200

# 删除生产批次
@app.route('/delete_produce_batch', methods=['POST'])
def delete_produce_batch():
    """
    input json:
    {
        person_id:
        batch_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # check info
    batch_id = data.get('batch_id')
    if not batch_id:
        return jsonify({'error': '缺少batch_id'}), 400

    # 查找并删除生产批次
    batch = ProductBatch.query.filter_by(batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': '批次ID不存在'}), 404
    
    db.session.delete(batch)
    db.session.commit()
    return jsonify({'message': '删除生产批次成功'}), 200

# 更新生产批次
@app.route('/update_produce_batch', methods=['POST'])
def update_produce_batch():
    """
    input json:
    {
        person_id:
        batch_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 获取要更新的批次ID和更新的信息
    batch_id = data.get('batch_id')
    if not batch_id:
        return jsonify({'error': '缺少batch_id'}), 400

    # received data
    farm_id = data.get('darm_id')
    type_id = data.get('type_id')
    batch_num = data.get('batch_num')
    batch_start = data.get('batch_start')
    batch_judge = data.get('batch_judge')
    
    batch = ProductBatch.query.filter_by(batch_id=batch_id).first()
    if batch:
        if farm_id:
            batch.farm_id = farm_id
        if type_id:
            batch.type_id = type_id
        if batch_num:
            batch.batch_num = batch_num
        if batch_start:
            # change time
            dt = parser.parse(batch_start)
            date_str = dt.strftime('%a, %d %b %Y %H:%M:%S %Z')
            naive_dt = datetime.strptime(date_str.split()[0] + ' ' + ' '.join(date_str.split()[1:-1]), '%a, %d %b %Y %H:%M:%S')  
            aware_dt = naive_dt.replace(tzinfo=tzutc())
            batch.batch_start = aware_dt
        
        if batch_judge:
            batch.batch_judge = batch_judge
    
    db.session.flush()
    db.session.commit()
    
    return jsonify({'message': '更新生产批次成功'}), 200

# 查询生产批次
@app.route('/query_produce_batch', methods=['POST'])
def query_produce_batch():
    """
    input json:
    {
        person_id:
        query_string:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    query_string = data.get('query_string')
    if not query_string:
        return jsonify({'error': '查询条件不能为空'}), 400

    # 将查询值转为字符串以便于模糊查询
    query_string = str(query_string)

    # 使用or_操作符进行模糊查询
    product_batches = ProductBatch.query.filter(
        or_(
            ProductBatch.batch_id.like(f'%{query_string}%'),
            ProductBatch.farm_id.like(f'%{query_string}%'),
            ProductBatch.type_id.like(f'%{query_string}%'),
            ProductBatch.batch_num.like(f'%{query_string}%'),
            ProductBatch.batch_judge.like(f'%{query_string}%')
        )
    ).all()

    output = []
    
    for batch in product_batches:
        batch_data = {
            'batch_id': batch.batch_id,
            'farm_id': batch.farm_id,
            'type_id': batch.type_id,
            'batch_num': batch.batch_num,
            'batch_start': batch.batch_start,
            'batch_judge': batch.batch_judge
        }
        output.append(batch_data)

    return jsonify({'product_batches': output}), 200

# 查询所有生产批次
@app.route('/query_all_produce_batch', methods=['POST'])
def query_all_produce_batch():
    """
    查询生产批次表的所有条目
    1. 验证登录状态，获取 log_token
    2. 返回生产批次表中的所有条目
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 查询生产批次表中的所有条目
    all_batches = ProductBatch.query.all()
    output = []
    for batch in all_batches:
        batch_data = {
            'batch_id': batch.batch_id,
            'farm_id': batch.farm_id,
            'type_id': batch.type_id,
            'batch_num': batch.batch_num,
            'batch_start': batch.batch_start,
            'batch_judge': batch.batch_judge
        }
        output.append(batch_data)

    return jsonify({'produce_batches': output}), 200

##########################################品种表的操作###################################################
# 增加品种
@app.route('/add_type', methods=['POST'])
def add_type():
    """
    input json:
    {
        person_id:
        
        type_name:
        type_period:
        type_info:
        type_judge:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 验证请求数据
    required_fields = ['type_name', 'type_period', 'type_info', 'type_judge']
    if not data or any(field not in data for field in required_fields):
        return jsonify({'error': '缺少必要的品种信息'}), 400

    # 创建新的品种记录并添加到数据库
    new_type = AllType(
        type_name=data['type_name'],
        type_period=data['type_period'],
        type_info=data['type_info'],
        type_judge=data['type_judge']
    )

    try:
        db.session.add(new_type)
        db.session.commit()
        return jsonify({'message': '添加品种成功', 'type_name': data['type_name']}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '添加品种失败', 'details': str(e)}), 500

# 删除品种
@app.route('/delete_type', methods=['POST'])
def delete_type():
    """
    删除品种记录
    1. 验证登录状态
    2. 接收用户输入的 type_id
    3. 删除品种表中的相应条目
    4. 返回删除成功或失败信息
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    type_id = data.get('type_id')
    if not type_id:
        return jsonify({'error': '缺少type_id'}), 400

    type_to_delete = AllType.query.filter_by(type_id=type_id).first()
    if not type_to_delete:
        return jsonify({'error': '该品种不存在'}), 404

    try:
        db.session.delete(type_to_delete)
        db.session.commit()
        return jsonify({'message': '删除品种成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除品种失败'}), 500

# 更新品种
@app.route('/update_type', methods=['POST'])
def update_type():
    """
    更新品种记录
    1. 验证登录状态
    2. 接收用户输入的品种信息和要更新的 type_id
    3. 更新品种表中的所有表项
    4. 返回更新成功或失败信息
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    type_id = data.get('type_id')
    if not type_id:
        return jsonify({'error': '缺少type_id'}), 400

    type_to_update = AllType.query.filter_by(type_id=type_id).first()
    if not type_to_update:
        return jsonify({'error': '该品种不存在'}), 404

    try:
        type_to_update.type_name = data.get('type_name', type_to_update.type_name)
        type_to_update.type_period = data.get('type_period', type_to_update.type_period)
        type_to_update.type_info = data.get('type_info', type_to_update.type_info)
        type_to_update.type_judge = data.get('type_judge', type_to_update.type_judge)

        db.session.commit()
        return jsonify({'message': '更新品种成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新品种失败'}), 500

# 查询品种
@app.route('/query_type', methods=['POST'])
def query_type():
    """
    input json:
    {
        person_id:
        
        query_string:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    search_value = data.get('query_string')
    if not search_value:
        return jsonify({'error': '缺少查询条件'}), 400

    # 将查询值转为字符串以便于模糊查询
    search_value = str(search_value)

    # 使用or_操作符进行模糊查询
    types = AllType.query.filter(
        or_(
            AllType.type_id.like(f'%{search_value}%'),
            AllType.type_name.like(f'%{search_value}%'),
            AllType.type_period.like(f'%{search_value}%'),
            AllType.type_info.like(f'%{search_value}%'),
            AllType.type_judge.like(f'%{search_value}%')
        )
    ).all()

    output = []
    for type_item in types:
        type_data = {
            'type_id': type_item.type_id,
            'type_name': type_item.type_name,
            'type_period': type_item.type_period,
            'type_info': type_item.type_info,
            'type_judge': type_item.type_judge
        }
        output.append(type_data)

    return jsonify({'types': output}), 200

# 查询所有品种
@app.route('/query_all_type', methods=['POST'])
def query_all_type():
    """
    input json:
    {
        person_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    all_types = AllType.query.all()
    output = []
    for type_item in all_types:
        type_data = {
            'type_id': type_item.type_id,
            'type_name': type_item.type_name,
            'type_period': type_item.type_period,
            'type_info': type_item.type_info,
            'type_judge': type_item.type_judge
        }
        output.append(type_data)

    return jsonify({'all_types': output}), 200

######################收获提醒###########################
@app.route('/expiry_info', methods=['POST'])
def expiry_info():
    """
    input json:
    {
        person_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 查找seller_id
    seller = Seller.query.filter_by(person_id=person_id).first()
    seller_id = seller.seller_id
    
    farms = Farm.query.filter_by(seller_id=seller_id).all()

    farm_ids = [farm.farm_id for farm in farms]
    
    time = datetime.now()
    

    # 查找生产批次状态为1（已成熟且未收获）的记录
    all_batches = ProductBatch.query.filter(
        ProductBatch.farm_id.in_(farm_ids)
    ).all()
    
    output = []
    for batch in all_batches:
        cur_type = AllType.query.filter_by(type_id = batch.type_id).first()
        if cur_type.type_period < (time - batch.batch_start).days:
            batch.batch_judge = 1
            db.session.flush()
            db.session.commit()
            output.append(
                {
                    'batch_id': batch.batch_id,
                    'farm_id': batch.type_id,
                    'type_id': batch.type_id,
                    'batch_num': batch.batch_num,
                    'batch_start': batch.batch_start,
                    'batch_judge': batch.batch_judge
                }
            )
    
    return jsonify({'mature_batches': output}), 200

###########################仓储管理###################################################
# 产品入库
@app.route('/add_repo_batch', methods=['POST'])
def add_repo_batch():
    """
    input json:
    {
        person_id:
        repo_id:
        product_id:
        batchrepo_period:
        batchrepo_size:
        batchrepo_num:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 获取用户输入的仓储批次信息
    repo_id = data.get('repo_id')
    product_id = data.get('product_id')
    batchrepo_period = data.get('batchrepo_period')
    batchrepo_size = data.get('batchrepo_size')
    batchrepo_num = data.get('batchrepo_num')
    
    if not repo_id or not product_id or not batchrepo_period or not batchrepo_size or not batchrepo_num:
        return jsonify({'error': '批次信息不完整'})

    # 创建新的仓储批次
    new_batch = RepoBatch(
        repo_id=repo_id,
        batchrepo_start=datetime.now(),
        product_id=product_id,
        batchrepo_period=batchrepo_period,
        batchrepo_size=batchrepo_size,
        batchrepo_num=batchrepo_num,
        batchrepo_left=batchrepo_num,
        batchrepo_on=0,
        batchrepo_expire=0
    )

    db.session.add(new_batch)
    db.session.commit()
    return jsonify({'message': '产品入库成功'}), 200

# 更新仓储批次
@app.route('/update_repo_batch', methods=['POST'])
def update_repo_batch():
    """
    input json:
    {
        person_id:
        batchrepo_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 获取要更新的批次ID和更新的信息
    batchrepo_id = data.get('batchrepo_id')
    if not batchrepo_id:
        return jsonify({'error': 'batchrepo_id'}), 400

    # received data
    repo_id = data.get('repo_id')
    batchrepo_start = data.get('batchrepo_start')
    product_id = data.get('product_id')
    batchrepo_period = data.get('batchrepo_period')
    batchrepo_size = data.get('batchrepo_size')
    batchrepo_num = data.get('batchrepo_num')
    batchrepo_left = data.get('batchrepo_left')
    batchrepo_on = data.get('batchrepo_on')
    batchrepo_expire = data.get('batchrepo_expire')
    
    batch = Repo.query.filter_by(batchrepo_id=batchrepo_id).first()
    if batch:
        if repo_id:
            batch.repo_id = repo_id
        if product_id:
            batch.product_id = product_id
        if batchrepo_period:
            batch.batchrepo_period = batchrepo_period
        if batchrepo_size:
            batch.batchrepo_size = batchrepo_size
        if batchrepo_num:
            batch.batchrepo_num = batchrepo_num
        if batchrepo_left:
            batch.batchrepo_left = batchrepo_left
        if batchrepo_on:
            batch.batchrepo_on = batchrepo_on
        if batchrepo_expire:
            batch.batchrepo_expire = batchrepo_expire
        if batchrepo_start is not None:
            # change time
            dt = parser.parse(batchrepo_start)
            date_str = dt.strftime('%a, %d %b %Y %H:%M:%S %Z')
            naive_dt = datetime.strptime(date_str.split()[0] + ' ' + ' '.join(date_str.split()[1:-1]), '%a, %d %b %Y %H:%M:%S')  
            aware_dt = naive_dt.replace(tzinfo=tzutc())
            batch.batch_start = aware_dt
            
    db.session.flush()
    db.session.commit()
    
    return jsonify({'message': '更新仓储批次成功'}), 200

# 查询仓储批次
@app.route('/query_repo_batch', methods=['POST'])
def query_repo_batch():
    """
    input json:
    {
        person_id:
        query_string:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    query_string = data.get('query_string')
    if not query_string:
        return jsonify({'error': '查询条件不能为空'}), 400

    # 将查询值转为字符串以便于模糊查询
    query_string = str(query_string)

    # 使用or_操作符进行模糊查询
    repo_batches = RepoBatch.query.filter(
        or_(
            RepoBatch.batchrepo_id.like(f'%{query_string}%'),
            RepoBatch.repo_id.like(f'%{query_string}%'),
            RepoBatch.batchrepo_start.like(f'%{query_string}%'),
            RepoBatch.product_id.like(f'%{query_string}%')
        )
    ).all()

    output = []
    for batch in repo_batches:
        batch_data = {
            'batchrepo_id': batch.batch_id,
            'repo_id': batch.farm_id,
            'batchrepo_start': batch.type_id,
            'product_id': batch.batch_num
        }
        output.append(batch_data)

    return jsonify({'repo_batches': output}), 200

# 查询所有仓储批次
@app.route('/query_all_repo_batch', methods=['POST'])
def query_all_repo_batch():
    """
    查询仓储批次表的所有条目
    1. 验证登录状态，获取 log_token
    2. 返回仓储批次表中的所有条目
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 查询仓储批次表中的所有条目
    all_batches = RepoBatch.query.all()
    output = []
    for batch in all_batches:
        batch_data = {
            'batchrepo_id': batch.batchrepo_id,
            'repo_id': batch.repo_id,
            'batchrepo_start': batch.batchrepo_start,
            'product_id': batch.product_id,
            'batchrepo_period': batch.batchrepo_period,
            'batchrepo_size': batch.batchrepo_size,
            'batchrepo_num': batch.batchrepo_num,
            'batchrepo_left': batch.batchrepo_left,
            'batchrepo_on': batch.batchrepo_on,
            'batchrepo_expire': batch.batchrepo_expire,
        }
        output.append(batch_data)

    return jsonify({'repo_batches': output}), 200

######################过期提醒###########################
@app.route('/expiry_repo_info', methods=['POST'])
def expiry_repo_info():
    """
    input json:
    {
        person_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # 查找seller_id
    seller = Seller.query.filter_by(person_id=person_id).first()
    seller_id = seller.seller_id
    
    repos = Repo.query.filter_by(seller_id=seller_id).all()
    if not repos:
        return jsonify({'message': '卖家没有关联的仓库'}), 404

    repo_ids = [repo.repo_id for repo in repos]
    
    time = datetime.now()

    # 查找仓储批次状态batchrepo_expire为0（未过期）的记录
    all_batches = RepoBatch.query.filter(
        RepoBatch.repo_id.in_(repo_ids)
    ).all()
    
    output = []
    for batch in all_batches:
        if batch.batchrepo_period < (time - batch.batchrepo_start).days:
            batch.batchrepo_expire = 1
            db.session.flush()
            db.session.commit()
            output.append(
                {
                    'batchrepo_id': batch.batchrepo_id,
                    'repo_id': batch.repo_id,
                    'batchrepo_start': batch.batchrepo_start,
                    'product_id': batch.product_id,
                    'batchrepo_period': batch.batchrepo_period,
                    'batchrepo_size': batch.batchrepo_size,
                    'batchrepo_num': batch.batchrepo_num,
                    'batchrepo_left': batch.batchrepo_left,
                    'batchrepo_on': batch.batchrepo_on,
                    'batchrepo_expire': batch.batchrepo_expire
                }
            )
    
    return jsonify({'expire_batches': output}), 200

###########################销售管理###################################################
# 上架商品
@app.route('/add_product', methods=['POST'])
def add_product():
    """
    input json:
    {
        person_id:
        product_name:
        product_type:
        product_price:
        product_num;
        product_info
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # receive info
    product_name = data.get('product_name')
    product_type = data.get('product_type')
    product_price = data.get('product_price')
    product_num = data.get('product_num')
    product_info = data.get('product_info')

    # check info
    if not product_name or not product_type or not product_price or not product_num:
        return jsonify({'error': '商品信息缺失'}), 400
    
    seller = Seller.query.filter_by(person_id = person_id).first()
    seller_id = seller.seller_id

    # 创建新的土地记录并添加到数据库
    new_product = Product(
        product_name = product_name,
        product_type = product_type,
        product_price = product_price,
        product_num = product_num,
        product_info = product_info,
        seller_id = seller_id
    )
    
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': '商品添加成功'}), 200

# 删除商品
@app.route('/delete_product', methods=['POST'])
def delete_product():
    """
    input json:
    {
        person_id:
        product_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0: 
        return jsonify({'error': '用户不是农场主'}), 400
    
    # 获取删除商品id
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': '缺少product_id'}), 400

    product_to_delete = Product.query.filter_by(product_id=product_id).first()
    if not product_to_delete:
        return jsonify({'error': '该商品不存在'}), 404

    db.session.delete(product_to_delete)
    db.session.commit()
    return jsonify({'message': '删除商品成功'}), 200

# 修改商品信息
@app.route('/update_product', methods=['POST'])
def update_product():
    """
    input json:
    {
        person_id:
        product_id:
        product_name:
        product_type:
        product_price:
        product_num;
        product_info
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400
    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # received data
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': '缺少product_id'}), 400

    new_product = Product.query.filter_by(product_id=product_id).first()
    if not new_product:
        return jsonify({'error': '该商品不存在'}), 404
    else:
        # receive data
        product_name = data.get('product_name')
        product_type = data.get('product_type')
        product_price = data.get('product_price')
        product_num = data.get('product_num')
        product_info = data.get('product_info')
   
        if product_name:
            new_product.product_name = product_name
        if product_type:
            new_product.product_type = product_type
        if product_price:
            new_product.product_price = product_price
        if product_num:
            new_product.product_num = product_num
        if product_info:
            new_product.product_info = product_info
        
        db.session.flush()
        db.session.commit()
        return jsonify({'message': '更新商品信息成功'}), 200

# 查询所有商品(消费者)
@app.route('/query_all_product', methods=['POST'])
def query_all_product():
    """
    input json:
    {
        person_id:
    }
    
    output json:
    {
        product_id:
        product_name:
        product_type:
        product_price:
        product_num:
        product_info:
        seller_name:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if buyer
    if user.role_id != 1:
        return jsonify({'error': '用户不是消费者'}), 400

    products = Product.query.all()
    
    output = []
    for product in products:
        seller = Seller.query.filter_by(seller_id=product.seller_id).first()
        if not seller:
            return jsonify({'error': 'seller不存在'}), 400
        seller_name = seller.seller_name
        product_data = {
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_type': product.product_type,
            'product_price': product.product_price,
            'product_num': product.product_num,
            'product_info': product.product_info,
            'seller_name': seller_name
        }
        output.append(product_data)

    return jsonify({'products': output}), 200

# 查询所属商品(农场主)
@app.route('/query_my_product', methods=['POST'])
def query_my_product():
    """
    input json:
    {
        person_id:
    }
    
    output json:
    {
        product_id:
        product_name:
        product_type:
        product_price:
        product_num:
        product_info:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400
    
    seller = Seller.query.filter_by(person_id = person_id).first()
    seller_id = seller.seller_id
    products = Product.query.filter_by(seller_id=seller_id).all()
    
    output = []
    for product in products:
        product_data = {
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_type': product.product_type,
            'product_price': product.product_price,
            'product_num': product.product_num,
            'product_info': product.product_info
        }
        output.append(product_data)

    return jsonify({'products': output}), 200

# 创建订单
@app.route('/add_invoice', methods=['POST'])
def add_invoice():
    """
    input json:
    {
        person_id:
        product_id:
        invoice_num:
    }
    """

    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if buyer
    if user.role_id != 1:
        return jsonify({'error': '用户不是消费者'}), 400

    # receive info
    product_id = data.get('product_id')
    invoice_num = data.get('invoice_num')
    
    # check info
    if not invoice_num or not product_id:
        return jsonify({'error': '订单信息缺失'}), 400
    
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({'error': '该商品不存在'}), 404
    else:
        product_price = product.product_price
    
    buyer = Buyer.query.filter_by(person_id = person_id).first()
    buyer_id = buyer.buyer_id

    # 创建新的订单并添加到数据库
    new_invoice = Invoice(
        buyer_id = buyer_id,
        product_id = product_id,
        invoice_num = invoice_num,
        invoice_money = product_price*invoice_num,
        invoice_time = datetime.now(),
        invoice_out = 0
    )
    
    db.session.add(new_invoice)
    db.session.commit()
    return jsonify({'message': '下单成功'}), 200

# 修改订单状态
@app.route('/update_invoice', methods=['POST'])
def update_invoice():
    """
    input json:
    {
        person_id:
        invoice_id:
        invoice_out:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400

    # received data
    invoice_id = data.get('invoice_id')
    if not invoice_id:
        return jsonify({'error': '缺少invoice_id'}), 400

    new_invoice = Invoice.query.filter_by(invoice_id=invoice_id).first()
    if not new_invoice:
        return jsonify({'error': '该订单不存在'}), 404
    else:
        # receive data
        invoice_out = data.get('invoice_out')
   
        if invoice_out == 1 or invoice_out == 0:
            new_invoice.invoice_out = invoice_out
            db.session.flush()
            db.session.commit()
            return jsonify({'message': '更新订单状态成功'}), 200
        
        else:
            return jsonify({'error': '订单状态错误'}), 400
            
# 查询订单信息(农场主/消费者所属)
@app.route('/query_my_invoice', methods=['POST'])
def query_my_invoice():
    """
    input json:
    {
        person_id:
    }
    
    output json:
    {
        invoice_id:
        product_name:
        invoice_num:
        invoice_money:
        buyer_name:
        buyer_address:
        buyer_phone:
        seller_name:
        seller_address:
        seller_phone:
        invoice_time:
        invoice_out:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 农场主
    if user.role_id == 0:
        seller = Seller.query.filter_by(person_id = person_id).first()
        seller_id = seller.seller_id
        products = Product.query.filter_by(seller_id=seller_id).all()
        invoices = []
        for product in products:
            product_id = product.product_id
            product_invoices = Invoice.query.filter_by(product_id=product_id).all()
            invoices.extend(product_invoices)
        
        if not invoices:
            return jsonify({'error': '暂无订单'}), 400

    # 消费者
    elif user.role_id == 1:
        buyer = Buyer.query.filter_by(person_id = person_id).first()
        buyer_id = buyer.buyer_id
        invoices = Invoice.query.filter_by(buyer_id=buyer_id).all()
    
        if not invoices:
            return jsonify({'error': '暂无订单'}), 400
    
    output = []
    for invoice in invoices:
        # product_name
        product = Product.query.filter_by(product_id=invoice.product_id).first()
        if not product:
            return jsonify({'error': '订单中的商品不存在'}), 400
        product_name = product.product_name
        
        # buyer info
        buyer = Buyer.query.filter_by(buyer_id=invoice.buyer_id).first()
        if not buyer:
            return jsonify({'error': '订单中的消费者id不存在'}), 400
        buyer_name = buyer.buyer_name
        buyer_address = buyer.buyer_address
        buyer_phone = buyer.buyer_phone
        
        # seller info
        seller = Seller.query.filter_by(seller_id=product.seller_id).first()
        if not seller:
            return jsonify({'error': '订单中的农场主id不存在'}), 400
        seller_name = seller.seller_name
        seller_address = seller.seller_address
        seller_phone = seller.seller_phone
        
        invoice_data = {
            'invoice_id': invoice.invoice_id,
            'product_name': product_name,
            'invoice_num': invoice.invoice_num,
            'invoice_money': invoice.invoice_money,
            'buyer_name': buyer_name,
            'buyer_address': buyer_address,
            'buyer_phone': buyer_phone,
            'seller_name': seller_name,
            'seller_address':seller_address,
            'seller_phone': seller_phone,
            'invoice_time': invoice.invoice_time,
            'invoice_out': invoice.invoice_out
        }
        output.append(invoice_data)
      
    return jsonify({'invoices': output}), 200

###########################留言管理###################################################
# 查询所有留言
@app.route('/query_all_messages', methods=['POST'])
def query_all_messages():
    """
    input json:
    {
        person_id:
    }

    output json:
    {
        message:{
            'message_id': message.message_id,
            'message_info': message.message_info,
            'message_time': message.message_time
        }
    }
    """

    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400

    # 获取所有留言信息
    messages = Message.query.all()
    output = []
    for message in messages:
        message_data = {
            'message_id': message.message_id,
            'message_info': message.message_info,
            'message_time': message.message_time
        }
        output.append(message_data)

    return jsonify({'messages': output}), 200

# 添加留言
@app.route('/add_message', methods=['POST'])
def add_message():
    """
    input json:
    {
        person_id:
        message_info:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400

    # receive info
    message_info = data.get('message_info')
    
    # check info
    if not message_info:
        return jsonify({'error': '留言内容为空'}), 400

    # 创建新的留言记录并添加到数据库
    new_message = Message(
        message_info = message_info,
        message_time = datetime.now(),
        person_id = person_id
    )
    
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': '留言添加成功'}), 200

#################仓库表的操作#################
@app.route('/add_repo', methods=['POST'])
def add_repo():
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 当前用户是否为农场主
    seller = Seller.query.filter_by(person_id=person_id).first()
    if not seller:
        return jsonify({'error': '当前用户不是农场主'}), 400

    # receive
    repo_name = data.get('repo_name')
    repo_info = data.get('repo_info')
    repo_maxsize = data.get('repo_maxsize')
    
    new_repo = Repo(
        repo_name = repo_name,
        repo_info = repo_info,
        seller_id = seller.seller_id,
        repo_maxsize = repo_maxsize
    )
    
    db.session.add(new_repo)
    db.session.commit()
    return jsonify({'message': '仓库添加成功'}), 200

@app.route('/delete_repo', methods=['POST'])
def delete_repo():
    """
    input json:
    {
        person_id:
        repo_id:
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 当前用户是否为农场主
    seller = Seller.query.filter_by(person_id=person_id).first()
    if not seller:
        return jsonify({'error': '当前用户不是农场主'}), 400
    
    repo_id = data.get('repo_id')
    if repo_id is None:
        return jsonify({'error': '缺少repo_id'}), 400
    
    cur_repo = Repo.query.filter_by(repo_id = repo_id).first()
    if cur_repo is None:
        return jsonify({'error': '该仓库不存在'}), 400
    
    db.session.delete(cur_repo)
    db.session.commit()
    return jsonify({'message': '删除仓库成功'}), 200

@app.route('/update_repo', methods=['POST'])
def update_repo():
    """
    input json:
    {
        person_id
        
        seller_id
        repo_name
        repo_info 
        repo_maxsize
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 当前用户是否为农场主
    seller = Seller.query.filter_by(person_id=person_id).first()
    if not seller:
        return jsonify({'error': '当前用户不是农场主'}), 400

    repo_id = data.get('repo_id')
    if not repo_id:
        return jsonify({'error': '缺少repo_id'}), 400
    
    new_repo = Product.query.filter_by(repo_id=repo_id).first()
    if new_repo is None:
        return jsonify({'error': '该仓库不存在'}), 404
    else:
        seller_id = data.get('seller_id')
        repo_name = data.get('repo_name')
        repo_info = data.get('repo_info')
        repo_maxsize = data.get('repo_maxsize')
        
        if seller_id is not None:
            new_repo.seller_id = seller_id
        if repo_name is not None:
            new_repo.repo_name = repo_name
        if repo_info is not None:
            new_repo.repo_info = repo_info
        if repo_maxsize is not None:
            new_repo.repo_maxsize = repo_maxsize
        
        db.session.flush()
        db.session.commit()
        return jsonify({'message': '更新仓库信息成功'}), 200

# 查看农场主名下的所有仓库
@app.route('/query_all_repo', methods=['POST'])
def query_all_repo():
    """
    input json:
    {
        person_id
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # 当前用户是否为农场主
    seller = Seller.query.filter_by(person_id=person_id).first()
    if not seller:
        return jsonify({'error': '当前用户不是农场主'}), 400


    repos = Repo.query.filter_by(seller_id = seller.seller_id).all()
    
    output = []
    for repo in repos:
        repo_data = {
            'repo_id': repo.repo_id,
            'repo_name': repo.repo_name,
            'repo_info': repo.repo_info,
            'repo_maxsize': repo.repo_maxsize
        }
        output.append(repo_data)
    
    return jsonify({'repos': output}), 200
    
# 条件查询
@app.route('/query_repo', methods=['POST'])
def query_repo():
    """
    input json:
    {
        person_id
        query_string
    }
    """
    data = request.get_json()
    token = data.get('log_token')
    person_id = decode_jwt_token(token)
    if not person_id:
        return jsonify({'error': '无效或过期的token'}), 400

    # 验证用户信息
    log_state = LogState.query.filter_by(person_id=person_id,log_token=token).first()
    if not log_state:
        return jsonify({'error': '登录状态无效'}), 400

    # 查找用户
    user = UserLogin.query.filter_by(person_id=person_id).first()
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    # check if seller
    if user.role_id != 0:
        return jsonify({'error': '用户不是农场主'}), 400
    
    query_string = data.get('query_string')
    if query_string is None:
        return jsonify({'error': '缺少查询条件'}), 400
    query_string = str(query_string)
    
    seller = Seller.query.filter_by(person_id = person_id).first()

    repos = Repo.query.filter_by(seller_id = seller.seller_id).all()
    
    if not repos:
        return jsonify({'error': '用户没有建立仓库'}), 400
    
    output = []
    new_repos = [repo for repo in repos 
                 if query_string in repo.repo_name 
                 or query_string in repo.repo_info
                ]
    for repo in new_repos:
        repo_data = {
            'repo_id': repo.repo_id,
            'seller_id': seller.seller_id,
            'repo_name': repo.repo_name,
            'repo_info': repo.repo_info,
            'repo_maxsize': repo.repo_maxsize
        }
        output.append(repo_data)
    
    return jsonify({'repos': output}), 200

if __name__ == '__main__':
    app.run(debug=True)