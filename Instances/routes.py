import MySQLdb
from flaskext import mysql

from market import app
from flask import render_template, url_for,redirect, request, flash, jsonify
from market.models import Item, User
from market.form import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
# from flask_mysqldb import MySQL,MySQLdb #pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')


        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    item = Item.query.all()
    id = current_user.id
    if id==1:
         return render_template('admin.html')
    else:
        flash(f"Sorry only admin can access this page",category='danger')
        return redirect(url_for('market_page'))

@app.route('/about')
def about_page():
        return render_template('about.html')


# @app.route("/ajax_add", methods=["POST", "GET"])
# def ajax_add():
#     cursor = mysql.connection.cursor()
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     items = Item.query.all()
#     if request.method == "GET":
#         return render_template('admin.html', items=items)
#     if request.method == 'POST':
#
#         txtname = request.form['name']
#         txtprice = request.form['price']
#         txtbarcode = request.form['barcode']
#         txtdesc = request.form['description']
#
#         print(txtname)
#         if txtname == '':
#             msg = 'Please Input name'
#         elif txtprice == '':
#             msg = 'Please Input Price'
#         elif txtdesc == '':
#             msg = 'Please Input desc'
#         elif txtbarcode == '':
#             msg = 'Please input code'
#         else:
#             cur.execute("INSERT INTO items (name,department,phone) VALUES (%s,%s,%s)",
#                         [txtname, txtprice, txtdesc,txtbarcode])
#             db.session.commit()
#             cur.close()
#             msg = 'New record created successfully'
#     return jsonify(msg)
#
#
# @app.route("/ajax_update", methods=["POST", "GET"])
# def ajax_update():
#     cursor = mysql.connection.cursor()
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     if request.method == 'POST':
#         txtid = request.form['id']
#         txtname = request.form['name']
#         txtprice = request.form['price']
#         txtbarcode = request.form['barcode']
#         txtdesc = request.form['description']
#         print(id)
#         cur.execute("UPDATE items SET name = %s, department = %s, phone = %s WHERE id = %s ",
#                     [txtid,txtname, txtprice, txtbarcode, txtdesc])
#         mysql.connection.commit()
#         cur.close()
#         msg = 'Record successfully Updated'
#     return jsonify(msg)
#
#
# @app.route("/ajax_delete", methods=["POST", "GET"])
# def ajax_delete():
#     cursor = mysql.connection.cursor()
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     if request.method == 'POST':
#         getid = request.form['string']
#         print(getid)
#         cur.execute('DELETE FROM tblemployee WHERE id = {0}'.format(getid))
#         mysql.connection.commit()
#         cur.close()
#         msg = 'Record deleted successfully'
#     return jsonify(msg)