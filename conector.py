import mysql.connector
from mysql.connector import Error

# Centralized Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'inventory_db',
    'auth_plugin': 'mysql_native_password',
    'use_pure': True
}

def create_connection():
    """Establishes and returns a database connection."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Connection Error: {e}")
    return connection

def get_cursor(connection):
    if connection:
        return connection.cursor()
    return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()

def commit_changes(connection):
    if connection and connection.is_connected():
        connection.commit()

def rollback_changes(connection):
    if connection and connection.is_connected():
        connection.rollback()