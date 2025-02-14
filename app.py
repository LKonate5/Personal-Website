from flask import Flask, jsonify, request, render_template, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Allows access to columns by name
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()

    # Table for email subscriptions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for blog articles
    conn.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subtitle TEXT NOT NULL,
            content TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

init_db()  # Ensure tables exist on startup

### **🏠 Main Routes**
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if not name or not email:
            return "Name and email are required!"

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO subscribers (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            return "Thank you for subscribing!"
        except sqlite3.IntegrityError:
            return "This email is already subscribed."
        finally:
            conn.close()

    return render_template('signup.html')

### **📖 Blog API Routes (No Jinja, Uses JSON)**
# Fetch all blog articles
@app.route("/api/articles<int:id>")
def get_articles():
    conn = get_db_connection()
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (id,)).fetchone()
    conn.close()

    if article is None:
        return jsonify({"error": "Article not found"}), 404

    return jsonify(dict(article))

# Fetch a single blog article
@app.route("/api/article/<int:id>")
def get_article(id):
    conn = get_db_connection()
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (id,)).fetchone()
    conn.close()

    if article is None:
        return jsonify({"error": "Article not found"}), 404

    return jsonify(dict(article))

# Add a new blog article (Form submission)
@app.route("/api/new", methods=["POST"])
def new_article():
    data = request.get_json()

    title = data.get("title")
    subtitle = data.get("subtitle")
    content = data.get("content")

    if not title or not subtitle or not content:
        return jsonify({"error": "All fields are required!"}), 400

    conn = get_db_connection()
    conn.execute("INSERT INTO articles (title, subtitle, content) VALUES (?, ?, ?)", 
                 (title, subtitle, content))
    conn.commit()
    conn.close()

    return jsonify({"message": "Article added successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
