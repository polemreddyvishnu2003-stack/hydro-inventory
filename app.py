from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "hydro_secret_key"

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# DATABASE CONNECTION

conn = sqlite3.connect('inventory.db', check_same_thread=False)

cursor = conn.cursor()


# PRODUCTS TABLE

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    size TEXT,
    image TEXT
)
''')


# USERS TABLE

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

conn.commit()


# CREATE DEFAULT LOGIN

cursor.execute(
    "SELECT * FROM users WHERE username=?",
    ("admin",)
)

user = cursor.fetchone()

if not user:

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("admin", "1234")
    )

    conn.commit()


# LOGIN PAGE

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            session['user'] = username

            return redirect('/')

    return render_template('login.html')


# LOGOUT

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# HOME PAGE

@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search')

    if search:

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM products"
        )

    products = cursor.fetchall()

    return render_template(
        'dashboard.html',
        products=products
    )


# ADD PRODUCT

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        size = request.form['size']

        image = request.files['image']

        if image:

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image.filename
                )
            )

            cursor.execute(
                "INSERT INTO products (name, description, size, image) VALUES (?, ?, ?, ?)",
                (name, description, size, image.filename)
            )

            conn.commit()

            return render_template(
                'product.html',
                image=image.filename,
                name=name,
                description=description,
                size=size
            )

    return render_template('add_item.html')


# DELETE PRODUCT

@app.route('/delete/<int:id>')
def delete_product(id):

    if 'user' not in session:
        return redirect('/login')

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect('/')


# EDIT PRODUCT

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        name = request.form['name']
        description = request.form['description']
        size = request.form['size']

        cursor.execute(
            """
            UPDATE products
            SET name=?, description=?, size=?
            WHERE id=?
            """,
            (name, description, size, id)
        )

        conn.commit()

        return redirect('/')

    cursor.execute(
        "SELECT * FROM products WHERE id=?",
        (id,)
    )

    product = cursor.fetchone()

    return render_template(
        'edit_product.html',
        product=product
    )


if __name__ == '__main__':
    app.run(debug=True)