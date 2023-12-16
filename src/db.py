import pymongo
from bson import ObjectId
from flask_login import current_user

from defaults import (
    MONGO_DB_HOST,
    MONGO_DB_PORT,
    # MONGO_DB_USERNAME,
    # MONGO_DB_PASSWORD,
    DATABASE_NAME
)

USERS_COLLECTION = 'users'
EXPENSES_COLLECTION = 'expenses'

MONGO_DB_USERNAME = None
MONGO_DB_PASSWORD = None

if MONGO_DB_USERNAME and MONGO_DB_PASSWORD:
    connection = pymongo.MongoClient(
        MONGO_DB_HOST,
        MONGO_DB_PORT,
        username=MONGO_DB_USERNAME,
        password=MONGO_DB_PASSWORD,
    )
else:
    connection = pymongo.MongoClient(MONGO_DB_HOST, MONGO_DB_PORT)

db = connection[DATABASE_NAME]


def get_users(exclude_current_user=False):
    q = {}
    if exclude_current_user:
        q['_id'] = {'$ne': ObjectId(current_user.get_id())}
    return db[USERS_COLLECTION].find(q)


def get_users_from_ids(user_ids):
    return db[USERS_COLLECTION].find({'_id': {'$in': user_ids}})


def get_user_by_email(email):
    return db[USERS_COLLECTION].find_one({'email': email})
