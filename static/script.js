document.addEventListener('DOMContentLoaded', function () {
    // Set base API URL and select commonly used DOM elements
    const API_BASE = 'http://127.0.0.1:5000';
    const productGrid = document.getElementById('product-grid');
    const productDetailSection = document.getElementById('product-detail');
    const backButton = document.getElementById('back-to-products');
    const cartList = document.getElementById('cart-list');
    const checkoutButton = document.getElementById('checkout-button');
    const toggleButton = document.getElementById('toggle-cart');
    const sidebar = document.getElementById('cart-sidebar');

    // Toggle sidebar visibility on cart button click
    toggleButton.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    // Go back to product grid from product detail view
    backButton.addEventListener('click', function () {
        productDetailSection.classList.add('hidden');
        document.querySelector('#products').classList.remove('hidden');
    });

    // Run on initial page load
    loadProducts();
    loadCartPreview();

    // Generic helper to fetch data from backend
    async function fetchAPI(endpoint) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    // Load and display all products
    async function loadProducts() {
        try {
            const products = await fetchAPI('/products');
            displayProducts(products);
            lazyLoadImages();
        } catch (error) {
            console.error('Failed to load products:', error);
            productGrid.innerHTML = `
                <div class="error-message">
                    <p>Failed to load products. Please ensure:</p>
                    <ul>
                        <li>The backend server is running (check terminal)</li>
                        <li>You’re accessing via http://127.0.0.1:5000</li>
                    </ul>
                    <p>Error details: ${error.message}</p>
                </div>
            `;
        }
    }

    // Replace lazy image URLs with actual src attributes
    function lazyLoadImages() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            img.src = img.dataset.src;
            img.onload = () => img.classList.add('loaded');
            img.onerror = () => {
                img.src = 'https://via.placeholder.com/300?text=Image+Not+Found';
            };
        });
    }

    // Render product cards into the grid
    function displayProducts(products) {
        productGrid.innerHTML = '';

        if (products.length === 0) {
            productGrid.innerHTML = '<p>No products found.</p>';
            return;
        }

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
            <div class="product-image">
                <img src="/static/images/${product.thumb_url}" alt="${product.name}" style="width: 100%; height: auto;">
            </div>
            <div class="product-info">
                <h3>${product.name}</h3>
                <p class="price">$${product.price.toFixed(2)}</p>
                <span class="category">${product.category}</span>
                <p class="stock_quantity">${product.stock_quantity} in stock</p>
                <button onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
            `;
            productCard.addEventListener('click', (e) => {
                if (e.target.tagName.toLowerCase() !== 'button') {
                    showProductDetail(product.id);
                }
            });
            productGrid.appendChild(productCard);
        });
    }

    // Show detailed product view and recommendations
    async function showProductDetail(productId) {
        try {
            const product = await fetchAPI(`/products/${productId}`);
            document.getElementById('detail-name').textContent = product.name;
            document.getElementById('detail-price').textContent = `$${product.price.toFixed(2)}`;
            document.getElementById('detail-category').textContent = product.category;
            document.getElementById('detail-description').textContent = product.description;
            document.getElementById('detail-stock').textContent = `${product.stock_quantity} in stock`;

            const detailImage = document.getElementById('detail-image_url');
            detailImage.src = 'https://via.placeholder.com/300';
            detailImage.classList.remove('loaded');

            const actualImage = new Image();
            actualImage.src = `/static/images/${product.image_url}`;
            actualImage.onload = () => {
                detailImage.src = actualImage.src;
                detailImage.classList.add('loaded');
            };
            actualImage.onerror = () => {
                detailImage.src = 'https://via.placeholder.com/300?text=Image+Not+Found';
            };

            productDetailSection.classList.remove('hidden');
            document.querySelector('#products').classList.add('hidden');

            const recommendations = await fetchAPI(`/recommendations/${productId}`);
            displayRecommendations(recommendations);

        } catch (error) {
            console.error('Error while loading product details or recommendations:', error);
            alert('Failed to load product details.');
        }
    }

    // Add selected product to cart
    async function addToCart(productId) {
        try {
            const res = await fetch(`${API_BASE}/cart/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId, quantity: 1 })
            });
            const data = await res.json();
            showToast(data.message);
            loadCart();
            loadCartPreview();
        } catch (err) {
            console.error('Add to cart failed:', err);
        }
    }
    window.addToCart = addToCart;

    // Load full cart for display
    async function loadCart() {
        try {
            const res = await fetch(`${API_BASE}/cart`);
            const items = await res.json();
            cartList.innerHTML = '';

            if (items.length === 0) {
                cartList.innerHTML = '<li>Your cart is empty.</li>';
            } else {
                items.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = `${item.name} x ${item.quantity} - $${(item.price * item.quantity).toFixed(2)}`;
                    cartList.appendChild(li);
                });
            }
        } catch (err) {
            console.error('Failed to load cart:', err);
        }
    }

    // Load right-side mini cart preview
    async function loadCartPreview() {
        try {
            const res = await fetch('/cart');
            const items = await res.json();
            const list = document.getElementById('cart-preview-list');
            const totalSpan = document.getElementById('cart-preview-total');
            list.innerHTML = '';
            let total = 0;

            items.forEach(item => {
                const subtotal = item.price * item.quantity;
                total += subtotal;

                const li = document.createElement('li');
                li.innerHTML = `
                    <span>${item.name} x${item.quantity}</span>
                    <button class="remove-btn" onclick="removeFromCart(${item.cart_id})">✖</button>
                `;
                list.appendChild(li);
            });

            totalSpan.textContent = total.toFixed(2);
        } catch (err) {
            console.error('Failed to load cart preview:', err);
        }
    }

    // Remove item from cart
    async function removeFromCart(cartId) {
        try {
            const res = await fetch(`/cart/remove/${cartId}`, { method: 'DELETE' });
            const data = await res.json();
            showToast(data.message || 'Removed from cart');
            loadCartPreview();
            loadCart();
        } catch (err) {
            console.error('Remove from cart failed:', err);
        }
    }
    window.removeFromCart = removeFromCart;

    // Handle checkout button click
    checkoutButton.addEventListener('click', async () => {
        try {
            const res = await fetch(`${API_BASE}/cart/checkout`, { method: 'POST' });
            const data = await res.json();
            if (res.ok) {
                window.location.href = `/order-summary/${data.order_id}`;
            } else {
                alert(data.error || 'Checkout failed.');
            }
        } catch (err) {
            console.error('Checkout error:', err);
            alert('Something went wrong.');
        }
    });

    // Allow retailer to update product details
    window.updateProduct = async function (productId) {
        const name = document.getElementById(`name-${productId}`).value;
        const price = parseFloat(document.getElementById(`price-${productId}`).value);
        const description = document.getElementById(`desc-${productId}`).value;
        const stock = parseInt(document.getElementById(`stock-${productId}`).value);

        try {
            const res = await fetch(`/update-product/${productId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    price,
                    description,
                    stock_quantity: stock
                })
            });

            const data = await res.json();
            if (res.ok) {
                alert(data.message || 'Product updated');
            } else {
                alert(data.error || 'Update failed');
            }
        } catch (err) {
            console.error('Update failed:', err);
            alert('Something went wrong during update.');
        }
    };

    // Display product recommendations on detail view
    function displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations');
        container.innerHTML = '<h3>You Might Also Like</h3>';

        if (!recommendations || recommendations.length === 0) {
            container.innerHTML += '<p>No recommendations available.</p>';
            return;
        }

        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'recommendation-card';
            card.innerHTML = `
                <h4>${rec.name}</h4>
                <p class="price">$${rec.price.toFixed(2)}</p>
                <span class="category">${rec.category}</span>
            `;
            card.addEventListener('click', () => showProductDetail(rec.id));
            container.appendChild(card);
        });
    }

    // Show a toast notification at bottom of page
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
