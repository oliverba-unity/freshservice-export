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
cursor.execute("DROP TABLE IF EXISTS service_catalog_categories")
cursor.execute("DROP TABLE IF EXISTS service_catalog_items")

cursor.execute("""
    CREATE TABLE service_catalog_categories(
        id,
        name,
        workspace_id,
        description,
        position,
        created_at,
        updated_at
    )
""")

cursor.execute("""CREATE TABLE service_catalog_items(
    id,
    workspace_id,
    category_id,
    display_id,
    name,
    item_type,
    ci_type_id,
    delivery_time,
    product_id,
    deleted,
    visibility,
    cost_visibility,
    delivery_time_visibility,
    group_visibility,
    agent_group_visibility,
    allow_quantity,
    quantity,
    is_bundle,
    create_child,
    allow_attachments,
    configs_attachment_mandatory,
    configs_subject,
    created_at,
    updated_at
    )
""")

db_connection.commit()

basic = HTTPBasicAuth(API_KEY, '')

def get(path):
    return requests.get(API_URL + path, auth=basic)

response = get('/service_catalog/categories').json()

categories = response['service_categories'];

categories_list = []

for category in categories:
    categories_list.append([
        category['id'],
        category['name'],
        category['workspace_id'],
        category['description'],
        category['position'],
        category['created_at'],
        category['updated_at']
        ])

cursor.executemany("""
    INSERT INTO service_catalog_categories
    VALUES(?, ?, ?, ?, ?, ?, ?)
    """, categories_list)

db_connection.commit()


def get_catalog_items(page = 1):

    print(f"Getting page {page}")

    response = get('/service_catalog/items?per_page=100&page='+str(page))

    service_catalog_items = response.json()['service_items'];

    service_catalog_items_list = []

    for item in service_catalog_items:
        service_catalog_items_list.append([
            item['id'],
            item['workspace_id'],
            item['category_id'],
            item['display_id'],
            item['name'],
            item['item_type'],
            item['ci_type_id'],
            item['delivery_time'],
            item['product_id'],
            item['deleted'],
            item['visibility'],
            item['cost_visibility'],
            item['delivery_time_visibility'],
            item['group_visibility'],
            item['agent_group_visibility'],
            item['allow_quantity'],
            item['quantity'],
            item['is_bundle'],
            item['create_child'],
            item['allow_attachments'],
            item['configs']['attachment_mandatory'],
            item['configs']['subject'],
            item['created_at'],
            item['updated_at']
        ])

    cursor.executemany("""
        INSERT INTO service_catalog_items
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, service_catalog_items_list)

    db_connection.commit()

    print(f"Saved page {page}")

    if 'link' in response.headers:
        print(f"More pages to get - getting next page")
        get_catalog_items(page+1)

get_catalog_items()
