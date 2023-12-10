from web_app.db import db
from web_app.defaults import SECRET_KEY

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

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)


# User class
class User(UserMixin):
    def __init__(self, user_data):

        self.id = str(user_data['_id'])
        self.username = user_data['username']


@login_manager.user_loader
def load_user(user_id):

    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        return None
    return User(user_data)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        if db.users.find_one({'username': request.form.get('username')}):
            return render_template('register.html', error='Username already exists.')

        hashed_password = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256"
        )

        db.users.insert_one(
            {'username': request.form.get('username'), 'password': hashed_password}
        )

        user_data = db.users.find_one({'username': request.form.get('username')})
        user = User(user_data)
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = db.users.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid username or password.')
    
    return render_template('login.html')

@app.route('/')
def index():

    if current_user.is_authenticated:
        expenses = db.expenses.find({'expense_friends': {'$in': [current_user.get_id()]}})
        return render_template('index.html', expenses = expenses)
    return render_template('register.html')

@app.route('/expense/<expense_id>')
@login_required
def expense(expense_id):

    expense = db.expenses.find_one({'_id' : ObjectId(expense_id)})

    if (expense):
        return render_template('expense.html', expense = expense)
    else:
        return redirect(url_for('index'))

@app.route('/add', methods = ['GET', 'POST'])
@login_required
def add():

    if (request.method == 'GET'):
        return render_template('add.html')

    else:
        expense_name = request.form.get('expense_name')
        expense_amount = int(request.form.get('expense_amount'))
        expense_friends = request.form.get('expense_friends').strip().split(',')

        expense_friends.append(current_user.get_id())
        per_head_cost = expense_amount/len(expense_friends)

        db.expenses.insert_one({
            'expense_name': expense_name,
            'expense_amount': expense_amount,
            'expense_friends': expense_friends,
            'per_head_cost': per_head_cost
        })

        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=8001, debug=True)
