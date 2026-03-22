from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # random string for session security

# ---------- MySQL connection ----------
db = mysql.connector.connect(
    host="localhost",
    user="flaskuser",       # Use your MySQL user
    password="Flask@123",   # Password for that user
    database="invetory_db"  # Your database name
)

cursor = db.cursor()

# ---------- LOGIN ----------
@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['user'] = username  # store user in session
            return redirect('/dashboard')
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')  # prevent direct access

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()  # Fetch all products from MySQL

    # Calculate total inventory value
    total_value = sum([p[2]*p[3] for p in products])

    return render_template('dashboard.html', products=products, total_value=total_value)


# ---------- ADD PRODUCT ----------
@app.route('/add', methods=['POST'])
def add_product():
    if 'user' not in session:
        return redirect('/')

    name = request.form['name'].strip()
    quantity = int(request.form['quantity'])
    price = int(request.form['price'])

    if not name or quantity < 0 or price < 0:
        return "Invalid input!", 400

    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)",
                   (name, quantity, price))
    db.commit()
    return redirect('/dashboard')


# ---------- DELETE PRODUCT ----------
@app.route('/delete/<int:id>')
def delete_product(id):
    if 'user' not in session:
        return redirect('/')

    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    db.commit()
    return redirect('/dashboard')


# ---------- EDIT/UPDATE PRODUCT ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name'].strip()
        quantity = int(request.form['quantity'])
        price = int(request.form['price'])

        if not name or quantity < 0 or price < 0:
            return "Invalid input!", 400

        cursor.execute("UPDATE products SET name=%s, quantity=%s, price=%s WHERE id=%s",
                       (name, quantity, price, id))
        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()
    return render_template('edit.html', product=product)


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)  # remove user from session
    return redirect('/')


# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)