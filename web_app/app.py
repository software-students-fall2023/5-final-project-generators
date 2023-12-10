import datetime

from bson.objectid import ObjectId
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash

from web_app.db import db, get_users
from web_app.defaults import SECRET_KEY

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)


# User class
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.email = user_data['email']


@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        return None
    return User(user_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if any(not field for field in [first_name, last_name, email, password]):
            return render_template('register.html', error='Please fill all the fields.')
        if db.users.find_one({'email': email}):
            return render_template('register.html', error='Email already exists.')

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        db.users.insert_one({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        })

        user_data = db.users.find_one({'email': email})
        user = User(user_data)
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_data = db.users.find_one({'email': email})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')


@app.route('/')
def index():
    if current_user.is_authenticated:

        owed_expenses = db.expenses.find({'paid_by': ObjectId(current_user.get_id())})
        owe_expenses = db.expenses.find({f'paid.{current_user.email}' : {'$exists': True}})
        return render_template('index.html', owed_expenses=list(owed_expenses), owe_expenses=list(owe_expenses))
    
    return render_template('register.html')


@app.route('/expense/<expense_id>')
@login_required
def expense(expense_id):
    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})

    if (expense):
        return render_template('expense.html', expense=expense)
    else:
        return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html', users=get_users())
    else:

        name = request.form.get('name')
        amount = float(request.form.get('amount'))
        splits = request.form.get('splits').strip().split(',')

        splits.append(current_user.email)
        per_head_cost = amount / len(splits)

        db.expenses.insert_one({
            'name': name,
            'amount': amount,
            'paid_by': ObjectId(current_user.get_id()),
            'splits': {friend: per_head_cost for friend in splits}
        })

        return redirect(url_for('index'))


@app.route('/edit/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):

    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})
    print(expense)


    if not expense or expense.get('paid_by') != ObjectId(current_user.get_id()):
        return redirect(url_for('index'))

    if (request.method == 'GET'):
        return render_template('edit.html', expense=expense)

    else:
        name = request.form.get('name')
        amount = int(request.form.get('amount'))
        splits = request.form.get('splits').strip().split(',')

        splits.append(current_user.email)
        per_head_cost = amount / len(splits)

        splits = {friend: per_head_cost for friend in splits}

        edited_expense = db.expenses.find_one_and_replace({'_id': ObjectId(expense_id)}, {
            'name': name,
            'amount': amount,
            'paid_by': ObjectId(current_user.get_id()),
            'splits': splits,
        })

        return redirect(url_for('edit'))
    
@app.route('/delete/<expense_id>', methods = ['GET'])
@login_required
def delete(expense_id):

    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})
    
    if not expense or expense.get('paid_by') != ObjectId(current_user.get_id()):
        return redirect(url_for('index'))
    
    db.expenses.delete_one({'_id': ObjectId(expense_id)})
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8001, debug=True)