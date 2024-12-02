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
cursor.execute("DROP TABLE IF EXISTS agents")

cursor.execute("""
    CREATE TABLE agents(
        id,
        external_id,
        email,
        first_name,
        last_name,
        job_title,
        reporting_manager_id,
        active,
        api_key_enabled,
        has_logged_in,
        occasional,
        auto_assign_tickets,
        created_at,
        updated_at,
        last_active_at,
        last_login_at,
        auto_assign_status_changed_at,
        license_type,
        location_id,
        location_name,
        language,
        time_format,
        time_zone,
        signature
    )
""")

basic = HTTPBasicAuth(API_KEY, '')

def get(path):
    return requests.get(API_URL + path, auth=basic)

def get_agents(page = 1):

    print(f"Getting agents - page {page}")

    agents_response = get('/agents?per_page=100&page=' + str(page))

    agents = agents_response.json()['agents']

    agents_list = []

    for agent in agents:
        agents_list.append([
            agent['id'],
            agent['external_id'],
            agent['email'],
            agent['first_name'],
            agent['last_name'],
            agent['job_title'],
            agent['reporting_manager_id'],
            agent['active'],
            agent['api_key_enabled'],
            agent['has_logged_in'],
            agent['occasional'],
            agent['auto_assign_tickets'],
            agent['created_at'],
            agent['updated_at'],
            agent['last_active_at'],
            agent['last_login_at'],
            agent['auto_assign_status_changed_at'],
            agent['license_type'],
            agent['location_id'],
            agent['location_name'],
            agent['language'],
            agent['time_format'],
            agent['time_zone'],
            agent['signature']
        ])

    cursor.executemany("""
        INSERT INTO agents
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, agents_list)

    db_connection.commit()

    print(f"Saved page {page}")

    if 'link' in agents_response.headers:
        print(f"More pages to get - getting next page")
        get_agents(page+1)

get_agents()