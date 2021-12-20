import pymongo as pm

client = pm.MongoClient() 
print(f"{client=}")

thisCollect = client['testDB']['some_collect']


insert_ret = client['testDB']['some_collect'].insert_mant({['foo': 'bar']}
# insert_ret = client['testDB']['some_collect'].insert_one({'foo': 'bar'})
print(f"{insert_ret=}")

print("-------------------------------------------------")

docs = client['testDB']['some_collect'].find()
print(f"{docs=}")
for doc in docs: 
    print(f"{doc=}")

# doc = client['testDB']['some_collect'].find_one()

deletedDoc = thisCollect.delete_many({'foo' : 'bar'})
print(f"{deletedDoc=}")

print("------------------------------------------------")

docs = client['testDB']['some_collect'].find()
print(f"{docs=}")
for doc in docs: 
    print(f"{doc=}")