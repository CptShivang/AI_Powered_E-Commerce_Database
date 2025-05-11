# AI_Powered_E-Commerce_Database
# 🛒 AI Powered E-Commerce Database Management System

This project is a Flask-based web application that simulates an e-commerce platform, enhanced with AI-driven recommendations and efficient database management. It supports two user roles — **Retailers** and **Customers** — and provides full functionality from product listing to order management and checkout.

---

## 🚀 Features

### 👤 Authentication
- Secure user registration and login
- Role-based access: **Retailer** and **Customer**

### 🛍️ For Customers
- Browse product catalog with images and details
- Add items to a dynamic cart sidebar
- AI-powered product recommendations
- Checkout system with order summary
- View **past orders**

### 🛒 For Retailers
- Add, update, and manage product listings (image, price, quantity)
- View and manage **customer orders**
- Update order status (Pending → Shipped → Delivered)
- Upload product images with thumbnail previews

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python with Flask
- **Database:** MySQL
- **AI Recommendations:** Python logic (e.g., similarity or rule-based)

---

## 📁 Project Structure

```

AI\_Powered\_E-Commerce\_Database/
├── app.py
├── ai\_recommendations.py
├── database.sql
├── static/
│   ├── styles.css
│   ├── script.js
│   └── images/
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── customer.html
│   ├── retailer.html
│   ├── checkout.html
│   └── orders.html
└── README.md

2. **Install dependencies**

   Make sure Python and pip are installed.

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MySQL database**

   * Import `database.sql` into your MySQL server.
   * Update `.env` with your database credentials.

4. **Run the app**

   ```bash
   python app.py
   ```

5. **Visit** [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📦 To Do / Future Enhancements

* Integrate real payment gateway (like Razorpay or Stripe)
* Add product search and filtering
* Improve AI recommendations with machine learning
* Email confirmation for orders
* Unit and integration testing

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙋‍♂️ Author

**Shivang Shukla**
[GitHub Profile](https://github.com/CptShivang)


