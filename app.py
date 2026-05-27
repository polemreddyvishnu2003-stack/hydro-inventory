from flask import Flask, render_template, request, redirect
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# CREATE DATABASE
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        size TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# HOME
@app.route("/")
def home():
    return redirect("/login")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            return redirect("/dashboard")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", products=products)


# ADD PRODUCT
@app.route("/add", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")
        size = request.form.get("size")

        image = request.files["image"]

        filename = ""

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO products (name, description, size, image)
        VALUES (?, ?, ?, ?)
        """, (name, description, size, filename))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_item.html")


# PRODUCT DETAILS
@app.route("/product/<int:id>")
def product(id):

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template("product.html", product=product)


# DELETE PRODUCT
@app.route("/delete/<int:id>")
def delete_product(id):

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# RUN
if __name__ == "__main__":
    app.run(debug=True)