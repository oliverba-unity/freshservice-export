from dotenv import load_dotenv
import os
import requests
import json
import sqlite3
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_URL = os.getenv('API_URL')
DB_FILE = os.getenv('DB_FILE')

db_connection = sqlite3.connect(DB_FILE)
cursor = db_connection.cursor()
cursor.execute("DROP TABLE categories")
cursor.execute("CREATE TABLE categories(id, name)")

basic = HTTPBasicAuth(API_KEY, '')

def get(path):
    return requests.get(API_URL + path, auth=basic)

response = get('/solutions/categories').json()

categories = response['categories'];

for category in categories:
     cursor.execute("INSERT INTO categories VALUES('" + str(category['id']) + "', '" + category['name'] + "')")

db_connection.commit()

result = cursor.execute("SELECT * FROM categories")

print(result.fetchall())