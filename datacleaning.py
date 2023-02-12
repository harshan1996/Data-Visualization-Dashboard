from pymongo import MongoClient
from config import password,collection_name,database_name
client = MongoClient(f"mongodb+srv://Harshan:{password}@firstcluster.zxdpy3p.mongodb.net/?retryWrites=true&w=majority")
db=client[database_name]
collection=db[collection_name]

import json
file_open = open('jsondata.json')
jsondata = json.load(file_open)
print(jsondata[:5])

listNew = [{key: str(val) for key, val in dict.items()} for dict in jsondata]
for i in listNew:
    collection.insert_one(i)
print(len(listNew))
    
file_open.close()
