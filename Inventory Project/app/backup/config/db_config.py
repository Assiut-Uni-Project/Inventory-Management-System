import mysql.connector

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "inventory_db"

def get_db_connection():
    """
    دالة موحدة للاتصال بقاعدة البيانات.
    أي حد في التيم محتاج يكلم الداتا بيز ينادي الدالة دي.
    """
    try:
        conn = mysql.connector.connect(
            host = DB_HOST,   
            user = DB_USER,           
            password = DB_PASSWORD,           
            database = DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error connecting to MySQL: {err}")
        return None