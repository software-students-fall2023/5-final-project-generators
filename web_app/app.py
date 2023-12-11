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

from web_app.db import db, get_users, get_user_by_email
from web_app.defaults import SECRET_KEY, STATIC_DIR, TEMPLATES_DIR

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)
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

        owed_expenses = list(db.expenses.find({"$and": [
            {'paid_by': ObjectId(current_user.get_id())},
            {'payment': False}
        ]}))

        owe_expenses = list(db.expenses.find({"$and": [
            {'paid_by': {'$ne': ObjectId(current_user.get_id())}},
            {f'splits.{current_user.get_id()}': {'$exists': True}},
            {'payment': False}
        ]}))

        owe_amount, owed_amount = get_owe_owed()

        return render_template('index.html',
                               owed_expenses=owed_expenses,
                               owe_expenses=owe_expenses,
                               owed_amount=owed_amount,
                               owe_amount=owe_amount
                               )
    
    return render_template('register.html')


@app.route('/expense/<expense_id>')
@login_required
def expense_details(expense_id):
    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})
    if expense:
        return render_template('expense.html', expense=expense, 
                               own= (ObjectId(expense.get('paid_by')) == ObjectId(current_user.get_id())))
    else:
        return redirect(url_for('index'))


def get_expense_info():
    name = request.form.get('name')
    amount = float(request.form.get('amount'))
    splits = request.form.getlist('splits')
    per_head_cost = amount / len(splits)

    return {
        'name': name,
        'amount': amount,
        'paid_by': ObjectId(current_user.get_id()),
        'splits': {str(get_user_by_email(friend)['_id']): per_head_cost for friend in splits}
    }

def get_balance(user1, user2):

    user1_paid = list(db.expenses.find({'paid_by': ObjectId(user1)}))
    user2_paid = list(db.expenses.find({'paid_by': ObjectId(user2)}))

    print(user1_paid)
    print(user2_paid)

    user_1_owes = 0
    user_2_owes = 0

    for expense in user1_paid:
        user_2_owes += expense.get('splits').get(str(user2), 0)

    for expense in user2_paid:
        user_1_owes += expense.get('splits').get(str(user1), 0)

    return user_1_owes - user_2_owes

def get_owe_owed():

    users = db.users.find({})
    amount_owe = 0
    amount_owed = 0

    for user in users:
        if ObjectId(user.get('_id')) != ObjectId(current_user.get_id()):

            balance = get_balance(current_user.get_id(), user.get('_id'))
            amount_owe += balance if balance > 0 else 0
            amount_owed += -balance if balance < 0 else 0
    
    return amount_owe, amount_owed

def get_owed(user):
    pass

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'GET':
        users = list(get_users(exclude_current_user=True))
        item = get_user_by_email(current_user.email)
        item['selected'] = True
        users.append(item)
        return render_template('add.html', users=users)
    elif request.method == 'POST':
        db.expenses.insert_one({**get_expense_info(), 
                                'payment': False,
                                'created_at': datetime.datetime.utcnow()})
        
        return redirect(url_for('index'))


@app.route('/edit/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})

    if not expense or expense.get('paid_by') != ObjectId(current_user.get_id()):
        return redirect(url_for('index'))

    if request.method == 'GET':
        users = list(get_users())
        for user in users:
            user['selected'] = str(user.get('_id')) in expense['splits']
        return render_template('edit.html', expense=expense, users=users)
    else:
        item = get_expense_info()
        edited_expense = db.expenses.find_one_and_replace(
            {'_id': ObjectId(expense_id)},
            item,
        )
        return redirect(url_for('expense_details', expense_id=edited_expense['_id']))


@app.route('/delete/<expense_id>', methods=['GET'])
@login_required
def delete(expense_id):
    expense = db.expenses.find_one({'_id': ObjectId(expense_id)})

    if not expense or expense.get('paid_by') != ObjectId(current_user.get_id()):
        return redirect(url_for('index'))

    db.expenses.delete_one({'_id': ObjectId(expense_id)})
    return redirect(url_for('index'))

@app.route('/payments', methods=['GET'])
@login_required
def payments():
    
    owe_expenses = list(db.expenses.find({"$and": [
            {'paid_by': {'$ne': ObjectId(current_user.get_id())}},
            {f'splits.{current_user.get_id()}': {'$exists': True}}
        ]}))
    
    user_id_owed = list(set([expense.get('paid_by') for expense in owe_expenses]))
    users_owed = list(db.users.find({'_id': {'$in': user_id_owed}}))

    for user in users_owed:
        print(current_user.get_id(), user.get('_id'))
        balance = get_balance(current_user.get_id(), user.get('_id'))
        print(balance)
        if balance > 0:
            user['amount'] = balance

    return render_template('pay.html', users_owed=users_owed)

@app.route('/pay/<user_id>', methods=['GET', 'POST'])
@login_required
def record_payment(user_id):

    if request.method == 'GET':
        amount_owed = get_balance(current_user.get_id(), user_id)
        return render_template('record_payment.html', user_id = user_id, amount_owed = amount_owed)

    elif request.method == 'POST':

        amount_paid = float(request.form.get('amount'))

        db.expenses.insert_one({
            'payment': True,
            'paid_by': ObjectId(current_user.get_id()),
            'splits': {user_id: amount_paid}
        })

        return redirect(url_for('index'))
        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8001, debug=True)
