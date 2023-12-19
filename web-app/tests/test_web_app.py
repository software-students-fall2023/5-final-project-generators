import pytest

from src.app import app
from src.db import drop_db


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    """
    Delete the database before and after all tests have run
    """
    drop_db()
    yield
    drop_db()


@pytest.fixture(name="client")
def fixture_client():
    """
    Create a test client for the Flask app.
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF protection in tests

    with app.test_client() as client:
        yield client


@pytest.mark.order(1)
def test_register(client):
    """
    Test the registration route.
    """
    response = client.post(
        "/register",
        data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"},
    )

    # Redirect to home page after registration
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # email already exists
    response = client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )
    assert response.status_code == 200  # error: should go back to registration page
    assert "Email already exists" in response.text


@pytest.mark.order(2)
def test_login(client):
    """
    Test the login route
    """
    response = client.post(
        "/login", data={"email": "foo@bar.com", "password": "foobar"}
    )
    assert response.headers["Location"] == "/"
    assert 'Set-Cookie' in response.headers


@pytest.mark.order(3)
def test_add_edit_delete_expense(client):
    """
    Test expense logs
    """
    # add another user
    client.post(
        "/register", data={"first_name": "Foo1", "last_name": "Bar1", "email": "foo1@bar.com", "password": "foobar"}
    )
    response = client.post(
        "/add", data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com", "foo1@bar.com"]}
    )
    assert response.status_code == 302  # redirect to expense details page
    assert response.headers["Location"].startswith("/expense/")

    # edit
    inserted_id = response.headers["Location"].rsplit("/")[-1]
    response = client.post(f"/edit/{inserted_id}",
                           data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com"]})
    assert response.status_code == 302
    assert response.headers["Location"] == f"/expense/{inserted_id}"

    response = client.get(f"/expense/{inserted_id}")
    assert response.status_code == 200

    # delete
    response = client.get(f"/delete/{inserted_id}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    response = client.get(f"/expense/{inserted_id}")
    assert response.status_code == 404


@pytest.mark.order(4)
def test_add_page(client):
    """
    Test add page
    """
    # not logged in
    response = client.get('/add')
    assert response.status_code == 401  # unauthorized

    # logged in
    client.post(
        "/login", data={"email": "foo1@bar.com", "password": "foobar"})
    response = client.get('/add')
    assert response.status_code == 200

    response = client.post('/add', data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com"]})
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/expense/")

    inserted_id = response.headers["Location"].rsplit("/")[-1]
    response = client.get('/expense/' + inserted_id)
    assert response.status_code == 200


@pytest.mark.order(5)
def test_payments_page(client):
    """
    Test payments page
    """
    # not logged in
    response = client.get('/payments')
    assert response.status_code == 401  # unauthorized

    client.post("/login", data={"email": "foo@bar.com", "password": "foobar"})
    response = client.get('/payments')
    assert response.status_code == 200
    assert '$100' in response.text


@pytest.mark.order(6)
def test_home_page(client):
    """
    Test home page
    """
    # not logged in
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert 'Register' in response.text

    # logged in
    client.post("/login", data={"email": "foo@bar.com", "password": "foobar"})
    response = client.get('/')
    assert response.status_code == 200
    assert "No expenses available." not in response.text
