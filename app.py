# Final Complete app.py for Desh Cart

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from ultralytics import YOLO
from models import db, User
from xhtml2pdf import pisa
from PIL import Image
import base64, io
import razorpay


app = Flask(__name__)
app.config['RAZORPAY_KEY_ID'] = 'your_key_id'
app.config['RAZORPAY_KEY_SECRET'] = 'your_key_secret'
razorpay_client = razorpay.Client(auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rahulrathore39769@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mtlbkuchbhi@1'
mail = Mail(app)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load YOLO model
model = YOLO('models/my_model.pt')
model.conf = 0.8

# Sample product catalog
product_info = {
    'apple': {'name': 'Apple', 'price': 30, 'image': 'apple.jpeg', 'category': 'Fruits'},
    'banana': {'name': 'Banana', 'price': 10, 'image': 'banana.jpeg', 'category': 'Fruits'},
    'bread': {'name': 'Bread', 'price': 40, 'image': 'bread.jpeg', 'category': 'Bakery'},
    'milk': {'name': 'Milk', 'price': 25, 'image': 'milk.jpeg', 'category': 'Dairy'},
    'lays': {'name': 'lays', 'price': 20, 'image': 'lays.jpeg', 'category': 'grocery'},
    'pasta': {'name': 'pasta', 'price': 50, 'image': 'pasta.jpeg', 'category': 'grocery'},
    'yippee!': {'name': 'yippee!', 'price': 15, 'image': 'yippee!.jpeg', 'category': 'grocery'},
    'maggi': {'name': 'maggi', 'price': 15, 'image': 'maggi.jpeg', 'category': 'grocery'},
    'monaco biscuit': {'name': 'monaco biscuit', 'price': 10, 'image': 'monaco_biscuit.jpeg', 'category': 'Bakery'},
    'goodday biscuit': {'name': 'goodday biscuit', 'price': 10, 'image': 'goodday_biscuit.jpeg', 'category': 'Bakery'}
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='scrypt')
        user = User(email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    name = request.form['name']
    price = float(request.form['price'])
    cart = session.get('cart', [])
    for item in cart:
        if item['name'] == name:
            item['quantity'] += 1
            break
    else:
        cart.append({'name': name, 'price': price, 'quantity': 1})
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    name = request.form['name']
    action = request.form['action']
    for item in cart:
        if item['name'] == name:
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1:
                item['quantity'] -= 1
            elif action == 'delete':
                cart.remove(item)
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/bill')
@login_required
def bill():
    cart = session.get('cart', [])
    rendered = render_template('bill.html', cart=cart)
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(rendered), dest=pdf)
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bill.pdf'
    return response

@app.route('/pay')
@login_required
def pay():
    return render_template('pay.html')

@app.route('/payment/success', methods=['POST'])
@login_required
def payment_success():
    user_email = current_user.email
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    message = "Thank you for your purchase!\n\n"
    for item in cart:
        message += f"{item['name']} x {item['quantity']} = ₹{item['price'] * item['quantity']}\n"
    message += f"\nTotal: ₹{total}"
    msg = Message("Desh Cart - Order Confirmation", sender="your_email@gmail.com", recipients=[user_email])
    msg.body = message
    mail.send(msg)
    session['cart'] = []
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    results = []
    for key, item in product_info.items():
        if query in item['name'].lower() and (category == '' or item['category'] == category):
            results.append({**item, 'id': key})
    return render_template('search.html', results=results)

@app.route('/detect', methods=['POST'])
def detect():
    data = request.get_json()
    img_data = data.get('image', None)
    if not img_data:
        return jsonify({'error': 'No image provided'}), 400
    try:
        _, encoded = img_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return jsonify({'error': 'Invalid image data'}), 400

    results = model(img)
    detected_items = []
    cart = session.get('cart', [])
    for *_, _, cls in results[0].boxes.data.tolist():
        class_id = int(cls)
        product_key = model.names[class_id].lower()
        if product_key in product_info:
            item = product_info[product_key]
            for cart_item in cart:
                if cart_item['name'] == item['name']:
                    cart_item['quantity'] += 1
                    break
            else:
                cart.append({'name': item['name'], 'price': item['price'], 'image': item['image'], 'quantity': 1})
            detected_items.append(item)
    session['cart'] = cart
    return jsonify({'detected_items': detected_items, 'cart': cart})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)