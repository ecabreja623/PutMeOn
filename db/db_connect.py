import os
import json
import pymongo as pm
# from pymongo.server_api import ServerApi
import bson.json_util as bsutil

# USER_NM = os.environ.get("MONGO_UN", '')
# CLOUD_SVC = "serverlessinstance0.irvgp.mongodb.net"
# PSSWD = os.environ.get("MONGO_PSSWD", '')
# CLOUD_MDB = "mongodb+srv"
# DB_PARAMS = "retryWrites=true&w=majority"

DB_NM = "putmeonDB"
if os.environ.get("TEST_MODE", ''):
    DB_NM = "putmeonDB_test"

REMOTE = '1'
LOCAL = '0'

client = None


def get_client():
    """
    Get and return client given environment variables
    """
    global client
    if os.environ.get("LOCAL_MONGO", REMOTE) == LOCAL:
        print("connecting to local mongo")
        client = pm.MongoClient()
    # else:
    #     print("connecting to remote mongo")
    #     client = pm.MongoClient(f"{CLOUD_MDB}://{USER_NM}:{PASSWD}@"
    #                             + f"{CLOUD_SVC}/{DB_NM}?"
    #                             + f"{DB_PARAMS}",
    #                             server_api=ServerApi('1'))
    return client


def fetch_one(collect_nm, filters={}):
    """
    Fetch one record that meets filters.
    """
    return client[DB_NM][collect_nm].find_one(filters)


def del_one(collect_nm, filters={}):
    """
    Fetch one record that meets filters.
    """
    return client[DB_NM][collect_nm].delete_one(filters)


def fetch_all(collect_nm, key_nm):
    """
    fetch all records for a certain collection
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
