import os

import pytest

os.environ["MONGO_DB_NAME"] = "test-financify"

from src.app import app
from src.db import drop_db


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    drop_db()


@pytest.fixture(name="client")
def fixture_client():
    """
    Create a test client for the Flask app.
    """
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF protection in tests
    client = app.test_client()
    yield client


def test_register(client):
    """
    Test the registration route.
    """
    response = client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )
    assert response.status_code == 302  # Redirect to home page after registration
    assert response.headers["Location"] == "/"

    # email already exists
    response = client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )

    assert response.status_code == 200  # should go back to registration page
    assert "Email already exists" in response.text


def test_login(client):
    """
    Test the login route
    """
    client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )
    client.get('/logout')

    response = client.post(
        "/login", data={"email": "foo@bar.com", "password": "foobar"}
    )
    assert response.headers["Location"] == "/"


def test_add_edit_delete_expense(client):
    """
    Test expense logs
    """

    # add
    client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )
    client.post(
        "/register", data={"first_name": "Foo1", "last_name": "Bar1", "email": "foo1@bar.com", "password": "foobar1"}
    )

    response = client.post(
        "/add", data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com", "foo1@bar.com"]}
    )
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/expense/")

    inserted_id = response.headers["Location"].rsplit("/")[-1]

    # edit
    response = client.post(f"/edit/{inserted_id}",
                           data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com"]})
    assert response.status_code == 302

    response = client.get(f"/expense/{inserted_id}")
    assert response.status_code == 200

    # delete
    response = client.get(f"/delete/{inserted_id}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    response = client.get(f"/expense/{inserted_id}")
    assert response.status_code == 404


def test_add_page(client):
    """
    Test add page
    """
    # not logged in
    response = client.get('/add')
    assert response.status_code == 401  # unauthorized

    # logged in
    client.post(
        "/register", data={"first_name": "Foo", "last_name": "Bar", "email": "foo@bar.com", "password": "foobar"}
    )
    client.post(
        "/login", data={"email": "foo@bar.com", "password": "foobar"})

    response = client.get('/add')
    assert response.status_code == 200

    response = client.post('/add', data={"name": "Expense", "amount": 100, "splits": ["foo@bar.com"]})
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/expense/")

    inserted_id = response.headers["Location"].rsplit("/")[-1]
    response = client.get('/expense/' + inserted_id)
    assert response.status_code == 200

