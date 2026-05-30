from flask import Flask, render_template, request, redirect
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# DATABASE
def connect_db():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn


# CREATE TABLE
conn = connect_db()

conn.execute("""
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


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect("/dashboard")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    conn = connect_db()

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("dashboard.html", products=products)


# ADD PRODUCT
@app.route("/add", methods=["GET", "POST"])
@app.route("/add-item", methods=["GET", "POST"])
def add_item():

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        size = request.form["size"]

        image_file = request.files.get("image")

        filename = ""

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)

            image_file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        conn = connect_db()

        conn.execute(
            """
            INSERT INTO products
            (name, description, size, image)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, size, filename)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_item.html")


# DELETE PRODUCT
@app.route("/delete/<int:id>")
def delete_product(id):

    conn = connect_db()

    conn.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# EDIT PRODUCT
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    conn = connect_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        size = request.form["size"]

        conn.execute("""
        UPDATE products
        SET name=?, description=?, size=?
        WHERE id=?
        """, (name, description, size, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()

    return render_template(
        "edit_product.html",
        product=product
    )


# PRODUCT SHARE PAGE
@app.route("/product/<int:id>")
def product_page(id):

    conn = connect_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    if not product:
        return "Product Not Found"

    return render_template(
        "product.html",
        product=product
    )


if __name__ == "__main__":
    app.run(debug=True)
