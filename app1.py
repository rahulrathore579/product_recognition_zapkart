
# Final Complete app.py for Desh Cart with Razorpay Integration & Proper DB Init

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from ultralytics import YOLO
from models import db, User
from xhtml2pdf import pisa
from PIL import Image
import razorpay
import base64, io
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Razorpay API keys
app.config['RAZORPAY_KEY_ID'] = 'rzp_test_k3pOA75T9AnyzT'
app.config['RAZORPAY_KEY_SECRET'] = 'Kh4O5Y57Tq2G3LyTYDKA5SVt'
razorpay_client = razorpay.Client(auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))

# Email config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rahulrathore39769@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mtlbkuchbhi@1'
mail = Mail(app)

# Init extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load YOLO model
model = YOLO('my_model.pt')
model.conf = 0.5

# Sample product catalog
product_info ={
    'apple': {'name': 'Apple', 'price': 30, 'image': 'apple.jpeg', 'category': 'Fruits','barcode': '8901234567890'},
    'banana': {'name': 'Banana', 'price': 10, 'image': 'banana.jpeg', 'category': 'Fruits'},
    'bread': {'name': 'Bread', 'price': 40, 'image': 'bread.jpeg', 'category': 'Bakery'},
    'lays': {'name': 'lays', 'price': 20, 'image': 'lays.jpeg', 'category': 'grocery'},
    'pasta': {'name': 'pasta', 'price': 50, 'image': 'pasta.jpeg', 'category': 'grocery'},
    'yippee!': {'name': 'yippee!', 'price': 15, 'image': 'yippee!.jpeg', 'category': 'grocery'},
    'maggi': {'name': 'maggi', 'price': 15, 'image': 'maggi.jpeg', 'category': 'grocery'},
    'monaco biscuit': {'name': 'monaco biscuit', 'price': 10, 'image': 'monaco_biscuit.jpeg', 'category': 'Bakery'},
    'goodday biscuit': {'name': 'goodday biscuit', 'price': 10, 'image': 'goodday_biscuit.jpeg', 'category': 'Bakery'},

    # Men Fashion
    'men_dress': {'name': 'Men Dress', 'price': 799, 'image': 'men_dress.jpeg', 'category': 'men_fashion'},
    'men_tshirt': {'name': 'Men T-Shirt', 'price': 499, 'image': 'men_tshirt.jpeg','category': 'men_fashion'},
    'men_hoodie': {'name': 'Men Hoodie', 'price': 1099, 'image': 'men_hoodie.jpeg','category': 'men_fashion'},
    'men_jacket': {'name': 'Men Jacket', 'price': 1299, 'image': 'men_jacket.jpeg','category': 'men_fashion'},

    # Women Fashion
    'womens_kurti': {'name': 'Women’s Kurti', 'price': 699, 'image': 'womens_kurti.jpeg', 'category': 'women_fashion'},
    'womens_jeans': {'name': 'Women’s Jeans', 'price': 999, 'image': 'womens_jeans.jpeg', 'category': 'women_fashion'},
    'womens_saree': {'name': 'Designer Saree', 'price': 1499, 'image': 'saree.jpeg', 'category': 'women_fashion'},
    'womens_top': {'name': 'Floral Top', 'price': 599, 'image': 'floral_top.jpeg', 'category': 'women_fashion'},

    # Watches
    'analog_watch': {'name': 'Analog Watch', 'price': 1299, 'image': 'analog_watch.jpeg', 'category': 'watches'},
    'smart_watch': {'name': 'Smart Watch', 'price': 2499, 'image': 'smart_watch.jpeg', 'category': 'watches'},
    'digital_watch': {'name': 'Digital Watch', 'price': 999, 'image': 'digital_watch.jpeg', 'category': 'watches'},
    'classic_watch': {'name': 'Classic Leather Watch', 'price': 1999, 'image': 'classic_watch.jpeg','category': 'watches'},

    # Shoes
    'sports_shoes': {'name': 'Sports Shoes', 'price': 1499, 'image': 'sports_shoes.jpeg', 'category': 'shoes'},
    'formal_shoes': {'name': 'Formal Shoes', 'price': 1999, 'image': 'formal_shoes.jpeg', 'category': 'shoes'},
    'sneakers': {'name': 'White Sneakers', 'price': 1199, 'image': 'sneakers.jpeg', 'category': 'shoes'},
    'casual_shoes': {'name': 'Casual Loafers', 'price': 899, 'image': 'casual_shoes.jpeg', 'category': 'shoes'},

    # Grooming
    'face_wash': {'name': 'Face Wash', 'price': 150, 'image': 'face_wash.jpeg', 'category': 'grooming'},
    'shaving_kit': {'name': 'Shaving Kit', 'price': 350, 'image': 'shaving_kit.jpeg', 'category': 'grooming'},
    'body_lotion': {'name': 'Body Lotion', 'price': 250, 'image': 'body_lotion.jpeg', 'category': 'grooming'},
    'beard_oil': {'name': 'Beard Oil', 'price': 180, 'image': 'beard_oil.jpeg', 'category': 'grooming'},

    # Bags
    'leather_bag': {'name': 'Leather Bag', 'price': 999, 'image': 'leather_bag.jpeg', 'category': 'bags'},
    'backpack': {'name': 'Backpack', 'price': 699, 'image': 'backpack.jpeg', 'category': 'bags'},
    'handbag': {'name': 'Ladies Handbag', 'price': 849, 'image': 'handbag.jpeg', 'category': 'bags'},
    'tote_bag': {'name': 'Canvas Tote Bag', 'price': 549, 'image': 'tote_bag.jpeg', 'category': 'bags'},

    # Flip-Flops
    'flipflops_men': {'name': 'Men Flip-Flops', 'price': 299, 'image': 'flipflops_men.jpeg', 'category': 'flip-flops'},
    'flipflops_women': {'name': 'Women Flip-Flops', 'price': 349, 'image': 'flipflops_women.jpeg','category': 'flip-flops'},
    'rubber_flipflops': {'name': 'Rubber Flip-Flops', 'price': 199, 'image': 'rubber_flipflops.jpeg','category': 'flip-flops'},
    'branded_flipflops': {'name': 'Branded Flip-Flops', 'price': 399, 'image': 'branded_flipflops.jpeg','category': 'flip-flops'},

    # Grocery
    'atta': {'name': 'Wheat Flour (Atta)', 'price': 240, 'image': 'atta.jpeg', 'category': 'grocery'},
    'sugar': {'name': 'Sugar', 'price': 45, 'image': 'sugar.jpeg', 'category': 'grocery'},
    'rice': {'name': 'Basmati Rice', 'price': 90, 'image': 'rice.jpeg', 'category': 'grocery'},
    'salt': {'name': 'Iodized Salt', 'price': 20, 'image': 'salt.jpeg', 'category': 'grocery'},

    # Dairy
    'milk': {'name': 'Milk', 'price': 28, 'image': 'milk.jpeg', 'category': 'dairy'},
    'paneer': {'name': 'Paneer', 'price': 160, 'image': 'paneer.jpeg', 'category': 'dairy'},
    'butter': {'name': 'Butter', 'price': 90, 'image': 'butter.jpeg', 'category': 'dairy'},
    'curd': {'name': 'Fresh Curd', 'price': 40, 'image': 'curd.jpeg', 'category': 'dairy'}
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
    rendered = render_template('bill.html', cart=cart, now=datetime.now)
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(rendered), dest=pdf)
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=bill.pdf'
    return response
@app.route('/pay')
@login_required
def pay():
    cart = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart) * 100
    razorpay_order = razorpay_client.order.create(dict(
        amount=total_amount,
        currency='INR',
        payment_capture='1'
    ))
    return render_template('pay.html', cart=cart, total_amount=total_amount,
                           razorpay_order_id=razorpay_order['id'],
                           razorpay_key=app.config['RAZORPAY_KEY_ID'],
                           user=current_user)

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    return render_template('scan.html')

@app.route('/add_barcode', methods=['POST'])
def add_barcode():
    data = request.get_json()
    code = data.get('barcode')
    cart = session.get('cart', [])

    for key, item in product_info.items():
        if item.get('barcode') == code:
            for c in cart:
                if c['name'] == item['name']:
                    c['quantity'] += 1
                    break
            else:
                cart.append({
                    'name': item['name'],
                    'price': item['price'],
                    'image': item['image'],
                    'quantity': 1
                })
            session['cart'] = cart
            return jsonify({'status': 'success', 'item': item})

    return jsonify({'status': 'error', 'message': 'Product not found'}), 404


@app.route('/payment_success', methods=['GET','POST'])
@login_required
def payment_success():
    user_email = current_user.email
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    message = f"Thank you for your purchase!\n\nOrder Summary:\n"
    for item in cart:
        message += f"{item['name']} x {item['quantity']} = ₹{item['price'] * item['quantity']}\n"
    message += f"\nTotal: ₹{total}"
    msg = Message("Desh Cart - Order Confirmation", sender="rahulrathore39769@gmail.com", recipients=[user_email])
    msg.body = message
    mail.send(msg)
    session['cart'] = []
    return render_template('payment_success.html', cart=session.get('cart', []))

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
