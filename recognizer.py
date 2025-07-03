
# recognizer.py - YOLO Inference Logic

import torch
from PIL import Image
import io, base64

# Load YOLOv5 model
from ultralytics import YOLO

model = YOLO('models/my_model.pt')

model.conf = 0.5

# Define known products and their metadata
product_info = {
    'apple': {'name': 'Apple', 'price': 30, 'image': 'apple.jpg', 'category': 'Fruits'},
    'banana': {'name': 'Banana', 'price': 10, 'image': 'banana.jpg', 'category': 'Fruits'},
    'bread': {'name': 'Bread', 'price': 40, 'image': 'bread.jpg', 'category': 'Bakery'},
    'milk': {'name': 'Milk', 'price': 25, 'image': 'milk.jpg', 'category': 'Dairy'}
}

def detect_products_from_image(image_base64):
    try:
        header, encoded = image_base64.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    except Exception as e:
        return {'error': 'Invalid image data'}, 400

    results = model(img)
    detected_items = []

    for *box, conf, cls in results.xyxy[0].tolist():
        class_id = int(cls)
        product_key = model.names[class_id].lower()
        if product_key in product_info:
            item = product_info[product_key]
            detected_items.append({
                'id': product_key,
                'name': item['name'],
                'price': item['price'],
                'image': item['image'],
                'quantity': 1
            })

    return {'detected_items': detected_items}
