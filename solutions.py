from dotenv import load_dotenv
import os
import requests
import sqlite3
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_URL = os.getenv('API_URL')
DB_FILE = os.getenv('DB_FILE')

db_connection = sqlite3.connect(DB_FILE)
cursor = db_connection.cursor()
cursor.execute("DROP TABLE IF EXISTS solution_article_categories")
cursor.execute("DROP TABLE IF EXISTS solution_article_folders")
cursor.execute("DROP TABLE IF EXISTS solution_articles")

cursor.execute("""
    CREATE TABLE solution_article_categories(
        id,
        name,
        workspace_id,
        description,
        position,
        created_at,
        updated_at
    )
""")

cursor.execute("""
    CREATE TABLE solution_article_folders(
    id,
    parent_id,
    category_id,
    workspace_id,
    name,
    description,
    visibility,
    position,
    approval_settings,
    default_folder,
    has_subfolders,
    created_at,
    updated_at
    )
""")

cursor.execute("""
    CREATE TABLE solution_articles(
    id,
    title,
    description,
    description_text,
    article_type,
    url,
    status,
    source,
    position,
    user_id,
    folder_id,
    category_id,
    workspace_id,
    folder_visibility,
    created_at,
    updated_at,
    review_date,
    modified_at,
    modified_by,
    approval_status,
    thumbs_up,
    thumbs_down,
    views,
    inserted_into_tickets
    )
""")

basic = HTTPBasicAuth(API_KEY, '')

def get(path):
    return requests.get(API_URL + path, auth=basic)

def get_solution_articles(folder_id, page = 1):

    print(f"Getting articles in folder {folder_id} page {page}")

    solution_articles_response = get('/solutions/articles?folder_id=' + str(folder_id) + '&per_page=100&page=' + str(page))

    solution_articles = solution_articles_response.json()['articles']

    solution_articles_list = []

    for article in solution_articles:
        solution_articles_list.append([
            article['id'],
            article['title'],
            article['description'],
            article['description_text'],
            article['article_type'],
            article['url'],
            article['status'],
            article['source'],
            article['position'],
            article['user_id'],
            article['folder_id'],
            article['category_id'],
            article['workspace_id'],
            article['folder_visibility'],
            article['created_at'],
            article['updated_at'],
            article['review_date'],
            article['modified_at'],
            article['modified_by'],
            article['approval_status'],
            article['thumbs_up'],
            article['thumbs_down'],
            article['views'],
            article['inserted_into_tickets']
        ])

    cursor.executemany("""
        INSERT INTO solution_articles
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, solution_articles_list)

    db_connection.commit()

    print(f"Saved page {page}")

    if 'link' in solution_articles_response.headers:
        print(f"More pages to get - getting next page")
        get_solution_articles(folder_id, page+1)


def get_solution_folders(category_id, page = 1):

    print(f"Getting solution folders in category {category_id}")

    solution_folders_response = get('/solutions/folders?category_id=' + str(category_id)).json()

    folders = solution_folders_response['folders']

    folders_list = []

    for folder in folders:
        folders_list.append([
            folder['id'],
            folder['parent_id'],
            folder['category_id'],
            folder['workspace_id'],
            folder['name'],
            folder['description'],
            folder['visibility'],
            folder['position'],
            folder['approval_settings'],
            folder['default_folder'],
            folder['has_subfolders'],
            folder['created_at'],
            folder['updated_at']
        ])
        get_solution_articles(folder['id'])

    cursor.executemany("""
        INSERT INTO solution_article_folders
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, folders_list)

    db_connection.commit()

print("Getting solution categories")

response = get('/solutions/categories').json()

categories = response['categories']

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
    get_solution_folders(category['id'])

cursor.executemany("""
    INSERT INTO solution_article_categories
    VALUES(?, ?, ?, ?, ?, ?, ?)
    """, categories_list)

db_connection.commit()
