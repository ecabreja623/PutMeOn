import os
import json
import pymongo as pm
import bson.json_util as bsutil

USER_NM = os.environ.get("MONGO_UN", 'user')
CLOUD_SVC = "cluster0.c45bk.mongodb.net"
PASSWD = os.environ.get("MONGO_PSSWD", 'putmeon')
CLOUD_MDB = "mongodb+srv"
DB_PARAMS = "retryWrites=true&w=majority"

DB_NM = "putmeonDB"
if os.environ.get("TEST_MODE", ''):
    DB_NM = "putmeonDB_test"

CONN_STR = f"{CLOUD_MDB}://{USER_NM}:{PASSWD}@{CLOUD_SVC}/{DB_NM}?{DB_PARAMS}"

REMOTE = '1'
LOCAL = '0'

client = None


def get_client():
    """
    Get and return client given environment variables
    """
    global client
    if os.environ.get("LOCAL_MONGO", REMOTE) == LOCAL:
        print("Connecting to local mongo")
        client = pm.MongoClient()
    else:
        print("Connecting to remote mongo")
        client = pm.MongoClient(CONN_STR)  # , server_api=ServerApi('1'))
    return client


def fetch_one(collect_nm, filters={}):
    """
    Fetch one record that meets filters.
    """
    doc = client[DB_NM][collect_nm].find_one(filters)
    return json.loads(bsutil.dumps(doc))


def del_one(collect_nm, filters={}):
    """
    delete one record that meets filters.
    """
    return client[DB_NM][collect_nm].delete_one(filters)


def del_many(collect_nm, filters={}):
    """
    delete all records for some filter
    """
    if os.environ.get("TEST_MODE", ''):
        return client[DB_NM][collect_nm].delete_many(filters)


def fetch_all(collect_nm, key_nm):
    """
    fetch all records for a certain collection as a list
    """
    all_docs = []
    for doc in client[DB_NM][collect_nm].find():
        all_docs.append(json.loads(bsutil.dumps(doc)))
    return all_docs


def fetch_all_dict(collect_nm, key_nm):
    """
    fetch all records for a certain collection as a dictionary
    """
    all_docs = {}
    for doc in client[DB_NM][collect_nm].find():
        all_docs[doc[key_nm]] = json.loads(bsutil.dumps(doc))
    return all_docs


def insert_doc(collect_nm, doc):
    """
    insert a doc into a certain collection
    """
    client[DB_NM][collect_nm].insert_one(doc)


def update_doc(collect_nm, filters, update):
    """
    updates a doc given filters and new values
    """
    client[DB_NM][collect_nm].update_one(filters, update)
