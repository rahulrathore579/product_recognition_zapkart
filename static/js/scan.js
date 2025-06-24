// static/js/scan.js
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const capturedImage = document.getElementById('capturedImage');
    const startBtn = document.getElementById('startCamera');
    const stopBtn = document.getElementById('stopCamera');
    const captureBtn = document.getElementById('capture');
    const imageUpload = document.getElementById('imageUpload');
    const detectedProductsDiv = document.getElementById('detectedProducts');

    let stream = null;

    // Start camera
    startBtn.addEventListener('click', async function() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.style.display = 'block';
            startBtn.disabled = true;
            stopBtn.disabled = false;
            captureBtn.disabled = false;
        } catch (err) {
            console.error("Error accessing camera: ", err);
            alert("Could not access the camera. Please check permissions.");
        }
    });

    // Stop camera
    stopBtn.addEventListener('click', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            video.style.display = 'none';
            startBtn.disabled = false;
            stopBtn.disabled = true;
            captureBtn.disabled = true;
        }
    });

    // Capture image
    captureBtn.addEventListener('click', function() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to data URL
        const imageData = canvas.toDataURL('image/jpeg');
        capturedImage.src = imageData;
        capturedImage.style.display = 'block';

        // Send to server for detection
        detectProducts(imageData);
    });

    // Handle image upload
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(event) {
                capturedImage.src = event.target.result;
                capturedImage.style.display = 'block';

                // Send to server for detection
                detectProducts(event.target.result);
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // Send image to server for product detection
    function detectProducts(imageData) {
        detectedProductsDiv.innerHTML = '<p>Detecting products...</p>';

        fetch('/detect_products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.products.length > 0) {
                let html = '';
                data.products.forEach(product => {
                    html += `
                    <div class="detected-product">
                        <img src="${product.image_url}" alt="${product.name}">
                        <div>
                            <h6>${product.name}</h6>
                            <p>₹${product.price.toFixed(2)}</p>
                            <button class="btn btn-sm btn-primary add-to-cart" 
                                    data-product-id="${product.id}">
                                Add to Cart
                            </button>
                        </div>
                    </div>
                    `;
                });
                detectedProductsDiv.innerHTML = html;

                // Add event listeners to add-to-cart buttons
                document.querySelectorAll('.add-to-cart').forEach(button => {
                    button.addEventListener('click', function() {
                        const productId = this.getAttribute('data-product-id');
                        addToCart(productId);
                    });
                });
            } else {
                detectedProductsDiv.innerHTML = '<p class="text-muted">No products detected</p>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            detectedProductsDiv.innerHTML = '<p class="text-danger">Error detecting products</p>';
        });
    }

    // Add product to cart
    function addToCart(productId) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}&quantity=1`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_count);
                alert('Product added to cart!');
            }
        });
    }

    // Update cart count in navbar
    function updateCartCount(count) {
        document.getElementById('cartCount').textContent = count;
    }
});